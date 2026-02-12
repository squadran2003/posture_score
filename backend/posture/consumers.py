import asyncio
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone

from .landmark_utils import (
    create_pose_detector,
    decode_frame,
    extract_landmarks,
    serialize_posture_landmarks,
)
from .models import PostureScore, PostureSession
from .scoring import PostureScorer

logger = logging.getLogger(__name__)

# Calibration: collect landmarks over this many frames
CALIBRATION_FRAMES = 45  # ~3 seconds at 15 fps
# Persist a score to DB every N frames (~1 second at 15fps)
PERSIST_EVERY_N_FRAMES = 15


class PostureConsumer(AsyncJsonWebsocketConsumer):
    """
    WebSocket consumer for real-time posture analysis.

    Protocol:
        Client sends:
            {"action": "start_session"}
            {"action": "calibrate"}           — begin 3s calibration
            {"action": "frame", "frame": "<base64 JPEG>"}
            {"action": "end_session"}

        Server responds:
            {"type": "session_started", "session_id": ...}
            {"type": "calibration_started"}
            {"type": "calibration_progress", "progress": 0.0-1.0}
            {"type": "calibration_complete"}
            {"type": "posture_result", "score": ..., "details": {...}, ...}
            {"type": "session_ended", "summary": {...}}
            {"type": "error", "message": "..."}
    """

    async def connect(self):
        self.user = self.scope.get("user")
        if not self.user or self.user.is_anonymous:
            await self.close(code=4001)
            return

        self.session = None
        self.scorer = None
        self.pose_detector = None
        self.calibrating = False
        self.calibration_landmarks = []
        self.frame_count = 0
        self.score_sum = 0.0
        self.score_count = 0

        await self.accept()

    async def receive_json(self, content):
        action = content.get("action")

        try:
            if action == "start_session":
                await self._handle_start_session()
            elif action == "calibrate":
                await self._handle_start_calibration()
            elif action == "frame":
                await self._handle_frame(content.get("frame", ""))
            elif action == "end_session":
                await self._handle_end_session()
            else:
                await self.send_json({
                    "type": "error",
                    "message": f"Unknown action: {action}",
                })
        except Exception as e:
            logger.exception("Error processing action %s", action)
            await self.send_json({
                "type": "error",
                "message": str(e),
            })

    async def disconnect(self, code):
        # Clean up: end any active session
        if self.session:
            await self._finalize_session()
        if self.pose_detector:
            self.pose_detector.close()
            self.pose_detector = None

    # ── Action handlers ─────────────────────────────────────────────

    async def _handle_start_session(self):
        if self.session:
            await self.send_json({
                "type": "error",
                "message": "Session already active. End it first.",
            })
            return

        self.session = await self._create_session()
        self.pose_detector = await asyncio.to_thread(create_pose_detector)
        self.scorer = PostureScorer()
        self.frame_count = 0
        self.score_sum = 0.0
        self.score_count = 0
        self.calibrating = False
        self.calibration_landmarks = []

        await self.send_json({
            "type": "session_started",
            "session_id": self.session.id,
        })

    async def _handle_start_calibration(self):
        if not self.session:
            await self.send_json({
                "type": "error",
                "message": "No active session. Send start_session first.",
            })
            return

        self.calibrating = True
        self.calibration_landmarks = []

        await self.send_json({"type": "calibration_started"})

    async def _handle_frame(self, frame_data):
        if not self.session:
            await self.send_json({
                "type": "error",
                "message": "No active session. Send start_session first.",
            })
            return

        if not frame_data:
            return

        # Decode and extract landmarks in a thread (CPU-bound)
        landmarks = await asyncio.to_thread(
            self._process_frame_sync, frame_data
        )

        if landmarks is None:
            await self.send_json({
                "type": "posture_result",
                "landmarks_detected": False,
                "message": "No pose detected — make sure your upper body is visible.",
            })
            return

        # Calibration mode: collect frames
        if self.calibrating:
            self.calibration_landmarks.append(landmarks)
            progress = len(self.calibration_landmarks) / CALIBRATION_FRAMES

            await self.send_json({
                "type": "calibration_progress",
                "progress": round(min(progress, 1.0), 2),
                "landmarks": serialize_posture_landmarks(landmarks),
            })

            if len(self.calibration_landmarks) >= CALIBRATION_FRAMES:
                await self._complete_calibration()
            return

        # Normal analysis mode
        self.frame_count += 1
        result = self.scorer.score(landmarks)

        if result is None:
            await self.send_json({
                "type": "posture_result",
                "landmarks_detected": True,
                "message": "Insufficient landmark visibility for scoring.",
            })
            return

        self.score_sum += result["overall_score"]
        self.score_count += 1

        # Persist every Nth frame
        if self.frame_count % PERSIST_EVERY_N_FRAMES == 0:
            await self._save_score(result)

        # Build response with current + ideal landmarks
        response = {
            "type": "posture_result",
            "landmarks_detected": True,
            "score": result["overall_score"],
            "label": result["label"],
            "details": {
                "head_position": result["head_position_score"],
                "shoulder_levelness": result["shoulder_levelness_score"],
                "shoulder_rounding": result["shoulder_rounding_score"],
                "spine_alignment": result["spine_alignment_score"],
            },
            "issues": result["issues"],
            "landmarks": serialize_posture_landmarks(landmarks),
        }

        # Include ideal landmarks if calibration was done
        if self.scorer.calibration:
            response["ideal_landmarks"] = serialize_posture_landmarks(
                self.scorer.calibration
            )

        await self.send_json(response)

    async def _handle_end_session(self):
        if not self.session:
            await self.send_json({
                "type": "error",
                "message": "No active session.",
            })
            return

        summary = await self._finalize_session()

        if self.pose_detector:
            self.pose_detector.close()
            self.pose_detector = None

        await self.send_json({
            "type": "session_ended",
            "summary": summary,
        })

    # ── Calibration ─────────────────────────────────────────────────

    async def _complete_calibration(self):
        """Average collected calibration landmarks to get the ideal pose."""
        self.calibrating = False

        # Average each landmark across all calibration frames
        num_landmarks = len(self.calibration_landmarks[0])
        averaged = []
        for i in range(num_landmarks):
            avg_x = sum(f[i]["x"] for f in self.calibration_landmarks) / len(self.calibration_landmarks)
            avg_y = sum(f[i]["y"] for f in self.calibration_landmarks) / len(self.calibration_landmarks)
            avg_z = sum(f[i]["z"] for f in self.calibration_landmarks) / len(self.calibration_landmarks)
            avg_vis = sum(f[i]["visibility"] for f in self.calibration_landmarks) / len(self.calibration_landmarks)
            averaged.append({
                "x": avg_x,
                "y": avg_y,
                "z": avg_z,
                "visibility": avg_vis,
            })

        self.scorer = PostureScorer(calibration_landmarks=averaged)

        # Persist calibration data to the session
        cal_data = serialize_posture_landmarks(averaged)
        await self._save_calibration(cal_data)

        self.calibration_landmarks = []

        await self.send_json({
            "type": "calibration_complete",
            "ideal_landmarks": cal_data,
        })

    # ── Sync helpers (run in thread) ────────────────────────────────

    def _process_frame_sync(self, frame_data):
        """Decode base64 frame and extract landmarks. Runs in a thread."""
        frame_rgb = decode_frame(frame_data)
        if frame_rgb is None:
            return None
        return extract_landmarks(self.pose_detector, frame_rgb)

    # ── DB operations ───────────────────────────────────────────────

    @database_sync_to_async
    def _create_session(self):
        return PostureSession.objects.create(user=self.user)

    @database_sync_to_async
    def _save_score(self, result):
        PostureScore.objects.create(
            session=self.session,
            overall_score=result["overall_score"],
            head_position_score=result["head_position_score"],
            shoulder_levelness_score=result["shoulder_levelness_score"],
            shoulder_rounding_score=result["shoulder_rounding_score"],
            spine_alignment_score=result["spine_alignment_score"],
            issues=result["issues"],
        )

    @database_sync_to_async
    def _save_calibration(self, cal_data):
        self.session.calibration_data = cal_data
        self.session.save(update_fields=["calibration_data"])

    @database_sync_to_async
    def _finalize_session(self):
        """Mark session as ended, compute average score."""
        self.session.ended_at = timezone.now()
        self.session.is_active = False

        if self.score_count > 0:
            self.session.average_score = round(self.score_sum / self.score_count, 1)

        self.session.save(update_fields=["ended_at", "is_active", "average_score"])

        summary = {
            "session_id": self.session.id,
            "duration_seconds": (
                self.session.ended_at - self.session.started_at
            ).total_seconds(),
            "average_score": self.session.average_score,
            "total_frames_analyzed": self.frame_count,
            "scores_recorded": self.score_count,
        }
        self.session = None
        self.scorer = None
        return summary
