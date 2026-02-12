import base64
import math
import os

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
from mediapipe.tasks.python.vision.pose_landmarker import PoseLandmarker, PoseLandmarkerOptions

# Path to the pose landmarker model
MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "models",
    "pose_landmarker_lite.task",
)

# Landmark indices we care about for posture analysis
LEFT_EAR = 7
RIGHT_EAR = 8
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_HIP = 23
RIGHT_HIP = 24

# Connections to draw for the body outline
POSTURE_CONNECTIONS = [
    (LEFT_EAR, RIGHT_EAR),
    (LEFT_EAR, LEFT_SHOULDER),
    (RIGHT_EAR, RIGHT_SHOULDER),
    (LEFT_SHOULDER, RIGHT_SHOULDER),
    (LEFT_SHOULDER, LEFT_HIP),
    (RIGHT_SHOULDER, RIGHT_HIP),
    (LEFT_HIP, RIGHT_HIP),
]


def create_pose_detector(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
):
    """Create a MediaPipe PoseLandmarker instance."""
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=VisionTaskRunningMode.IMAGE,
        num_poses=1,
        min_pose_detection_confidence=min_detection_confidence,
        min_pose_presence_confidence=min_tracking_confidence,
    )
    return PoseLandmarker.create_from_options(options)


def decode_frame(base64_frame):
    """Decode a base64-encoded JPEG frame to a numpy array (RGB)."""
    # Strip data URI prefix if present
    if "," in base64_frame:
        base64_frame = base64_frame.split(",", 1)[1]

    img_bytes = base64.b64decode(base64_frame)
    np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    frame_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if frame_bgr is None:
        return None
    return cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)


def extract_landmarks(pose_detector, frame_rgb):
    """
    Run MediaPipe PoseLandmarker on an RGB frame.
    Returns a list of {x, y, z, visibility} dicts for all 33 landmarks, or None.
    """
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = pose_detector.detect(mp_image)

    if not result.pose_landmarks or len(result.pose_landmarks) == 0:
        return None

    # result.pose_landmarks is a list of poses; take the first one
    pose = result.pose_landmarks[0]
    landmarks = []
    for lm in pose:
        landmarks.append({
            "x": lm.x,
            "y": lm.y,
            "z": lm.z,
            "visibility": lm.visibility,
        })
    return landmarks


def get_landmark(landmarks, index):
    """Get a single landmark dict by index."""
    if landmarks and 0 <= index < len(landmarks):
        return landmarks[index]
    return None


def midpoint(lm1, lm2):
    """Compute the midpoint between two landmarks."""
    return {
        "x": (lm1["x"] + lm2["x"]) / 2,
        "y": (lm1["y"] + lm2["y"]) / 2,
        "z": (lm1["z"] + lm2["z"]) / 2,
    }


def distance_2d(lm1, lm2):
    """Euclidean distance between two landmarks in 2D (x, y)."""
    return math.sqrt((lm1["x"] - lm2["x"]) ** 2 + (lm1["y"] - lm2["y"]) ** 2)


def angle_from_vertical(top, bottom):
    """
    Angle (degrees) that the line from bottom to top makes with the vertical.
    0 = perfectly vertical, positive = tilted right, negative = tilted left.
    """
    dx = top["x"] - bottom["x"]
    dy = top["y"] - bottom["y"]  # y increases downward in image coords
    # atan2 of horizontal deviation over vertical span
    return math.degrees(math.atan2(dx, -dy))


def landmarks_visible(landmarks, indices, min_visibility=0.5):
    """Check if all specified landmarks meet the minimum visibility threshold."""
    for idx in indices:
        lm = get_landmark(landmarks, idx)
        if lm is None or lm["visibility"] < min_visibility:
            return False
    return True


def serialize_posture_landmarks(landmarks):
    """
    Extract only the posture-relevant landmarks for sending to the frontend.
    Returns a dict mapping landmark names to {x, y} for overlay rendering.
    """
    if not landmarks:
        return None

    mapping = {
        "left_ear": LEFT_EAR,
        "right_ear": RIGHT_EAR,
        "left_shoulder": LEFT_SHOULDER,
        "right_shoulder": RIGHT_SHOULDER,
        "left_hip": LEFT_HIP,
        "right_hip": RIGHT_HIP,
    }
    result = {}
    for name, idx in mapping.items():
        lm = get_landmark(landmarks, idx)
        if lm:
            result[name] = {"x": round(lm["x"], 4), "y": round(lm["y"], 4)}
    return result
