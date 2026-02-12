import math

from .landmark_utils import (
    LEFT_EAR,
    LEFT_HIP,
    LEFT_SHOULDER,
    RIGHT_EAR,
    RIGHT_HIP,
    RIGHT_SHOULDER,
    angle_from_vertical,
    distance_2d,
    get_landmark,
    landmarks_visible,
    midpoint,
)

# Weights for overall score
WEIGHTS = {
    "head_position": 0.30,
    "shoulder_levelness": 0.25,
    "shoulder_rounding": 0.25,
    "spine_alignment": 0.20,
}

# All landmark indices we need for scoring
REQUIRED_LANDMARKS = [
    LEFT_EAR, RIGHT_EAR,
    LEFT_SHOULDER, RIGHT_SHOULDER,
    LEFT_HIP, RIGHT_HIP,
]

# Score range labels
SCORE_RANGES = [
    (85, 100, "excellent"),
    (70, 84, "good"),
    (55, 69, "fair"),
    (40, 54, "needs_work"),
    (0, 39, "poor"),
]


def get_score_label(score):
    for low, high, label in SCORE_RANGES:
        if low <= score <= high:
            return label
    return "poor"


class PostureScorer:
    """
    Computes a posture score (0-100) from MediaPipe landmarks.

    Optionally uses calibration landmarks as the "ideal" baseline.
    Without calibration, uses geometric heuristics for ideal posture.
    """

    def __init__(self, calibration_landmarks=None):
        self.calibration = calibration_landmarks

    def score(self, landmarks):
        """
        Compute all component scores and overall score.

        Returns dict with:
            overall_score, head_position_score, shoulder_levelness_score,
            shoulder_rounding_score, spine_alignment_score, issues[], label
        Or None if landmarks are insufficient.
        """
        if not landmarks_visible(landmarks, REQUIRED_LANDMARKS):
            return None

        head = self._score_head_position(landmarks)
        level = self._score_shoulder_levelness(landmarks)
        rounding = self._score_shoulder_rounding(landmarks)
        spine = self._score_spine_alignment(landmarks)

        overall = (
            head["score"] * WEIGHTS["head_position"]
            + level["score"] * WEIGHTS["shoulder_levelness"]
            + rounding["score"] * WEIGHTS["shoulder_rounding"]
            + spine["score"] * WEIGHTS["spine_alignment"]
        )
        overall = round(max(0, min(100, overall)), 1)

        issues = head["issues"] + level["issues"] + rounding["issues"] + spine["issues"]

        return {
            "overall_score": overall,
            "head_position_score": round(head["score"], 1),
            "shoulder_levelness_score": round(level["score"], 1),
            "shoulder_rounding_score": round(rounding["score"], 1),
            "spine_alignment_score": round(spine["score"], 1),
            "issues": issues,
            "label": get_score_label(overall),
        }

    def _score_head_position(self, landmarks):
        """
        Forward head position: measures how far the ear midpoint is
        forward (in x) relative to the shoulder midpoint.

        In a frontal view, forward head posture manifests as the ears
        appearing higher and the head tilting forward, changing the
        ear-to-shoulder vertical ratio.
        """
        ear_mid = midpoint(
            get_landmark(landmarks, LEFT_EAR),
            get_landmark(landmarks, RIGHT_EAR),
        )
        shoulder_mid = midpoint(
            get_landmark(landmarks, LEFT_SHOULDER),
            get_landmark(landmarks, RIGHT_SHOULDER),
        )

        if self.calibration:
            cal_ear_mid = midpoint(
                get_landmark(self.calibration, LEFT_EAR),
                get_landmark(self.calibration, RIGHT_EAR),
            )
            cal_shoulder_mid = midpoint(
                get_landmark(self.calibration, LEFT_SHOULDER),
                get_landmark(self.calibration, RIGHT_SHOULDER),
            )
            ideal_offset_y = cal_ear_mid["y"] - cal_shoulder_mid["y"]
            current_offset_y = ear_mid["y"] - shoulder_mid["y"]
            # Also check horizontal drift
            ideal_offset_x = abs(cal_ear_mid["x"] - cal_shoulder_mid["x"])
            current_offset_x = abs(ear_mid["x"] - shoulder_mid["x"])

            # Deviation from calibrated ideal
            y_deviation = abs(current_offset_y - ideal_offset_y)
            x_deviation = abs(current_offset_x - ideal_offset_x)
            deviation = math.sqrt(y_deviation**2 + x_deviation**2)
        else:
            # Without calibration, measure ear-shoulder vertical distance ratio
            # and horizontal alignment
            vertical_dist = abs(ear_mid["y"] - shoulder_mid["y"])
            horizontal_drift = abs(ear_mid["x"] - shoulder_mid["x"])
            # Ideal: ears directly above shoulders, good vertical separation
            deviation = horizontal_drift + max(0, 0.15 - vertical_dist)

        # Convert deviation to score (0-100). Max deviation ~0.15 normalized coords.
        score = max(0, 100 - (deviation / 0.15) * 100)

        issues = []
        if score < 70:
            issues.append({
                "component": "head_position",
                "severity": get_score_label(score),
                "message": "Head is forward of ideal position — try tucking your chin back.",
            })

        return {"score": score, "issues": issues}

    def _score_shoulder_levelness(self, landmarks):
        """
        Shoulder levelness: Y-coordinate difference between left and right shoulders.
        Perfectly level shoulders have the same Y value.
        """
        left_sh = get_landmark(landmarks, LEFT_SHOULDER)
        right_sh = get_landmark(landmarks, RIGHT_SHOULDER)

        y_diff = abs(left_sh["y"] - right_sh["y"])

        if self.calibration:
            cal_left = get_landmark(self.calibration, LEFT_SHOULDER)
            cal_right = get_landmark(self.calibration, RIGHT_SHOULDER)
            ideal_diff = abs(cal_left["y"] - cal_right["y"])
            deviation = abs(y_diff - ideal_diff)
        else:
            deviation = y_diff

        # Max tolerable deviation ~0.05 in normalized coords
        score = max(0, 100 - (deviation / 0.05) * 100)

        issues = []
        if score < 70:
            higher = "left" if left_sh["y"] < right_sh["y"] else "right"
            issues.append({
                "component": "shoulder_levelness",
                "severity": get_score_label(score),
                "message": f"Your {higher} shoulder is higher — try to relax and level your shoulders.",
            })

        return {"score": score, "issues": issues}

    def _score_shoulder_rounding(self, landmarks):
        """
        Shoulder rounding: ratio of shoulder width to hip width.
        Rounded shoulders reduce the apparent shoulder width relative to hips.
        """
        left_sh = get_landmark(landmarks, LEFT_SHOULDER)
        right_sh = get_landmark(landmarks, RIGHT_SHOULDER)
        left_hip = get_landmark(landmarks, LEFT_HIP)
        right_hip = get_landmark(landmarks, RIGHT_HIP)

        shoulder_width = distance_2d(left_sh, right_sh)
        hip_width = distance_2d(left_hip, right_hip)

        if hip_width < 0.01:
            return {"score": 50, "issues": []}

        ratio = shoulder_width / hip_width

        if self.calibration:
            cal_sw = distance_2d(
                get_landmark(self.calibration, LEFT_SHOULDER),
                get_landmark(self.calibration, RIGHT_SHOULDER),
            )
            cal_hw = distance_2d(
                get_landmark(self.calibration, LEFT_HIP),
                get_landmark(self.calibration, RIGHT_HIP),
            )
            ideal_ratio = cal_sw / cal_hw if cal_hw > 0.01 else 1.0
            deviation = max(0, ideal_ratio - ratio)  # rounding decreases ratio
        else:
            # Good posture: shoulders wider than hips (ratio ~1.1-1.3)
            ideal_ratio = 1.2
            deviation = max(0, ideal_ratio - ratio)

        # Max deviation ~0.3
        score = max(0, 100 - (deviation / 0.3) * 100)

        issues = []
        if score < 70:
            issues.append({
                "component": "shoulder_rounding",
                "severity": get_score_label(score),
                "message": "Shoulders appear rounded — pull your shoulder blades back and together.",
            })

        return {"score": score, "issues": issues}

    def _score_spine_alignment(self, landmarks):
        """
        Spine alignment: angle of the torso midline from vertical.
        Measures the line from hip midpoint to shoulder midpoint.
        """
        shoulder_mid = midpoint(
            get_landmark(landmarks, LEFT_SHOULDER),
            get_landmark(landmarks, RIGHT_SHOULDER),
        )
        hip_mid = midpoint(
            get_landmark(landmarks, LEFT_HIP),
            get_landmark(landmarks, RIGHT_HIP),
        )

        angle = abs(angle_from_vertical(shoulder_mid, hip_mid))

        if self.calibration:
            cal_shoulder_mid = midpoint(
                get_landmark(self.calibration, LEFT_SHOULDER),
                get_landmark(self.calibration, RIGHT_SHOULDER),
            )
            cal_hip_mid = midpoint(
                get_landmark(self.calibration, LEFT_HIP),
                get_landmark(self.calibration, RIGHT_HIP),
            )
            ideal_angle = abs(angle_from_vertical(cal_shoulder_mid, cal_hip_mid))
            deviation = abs(angle - ideal_angle)
        else:
            deviation = angle  # ideal is 0 degrees (vertical)

        # Max tolerable deviation ~15 degrees
        score = max(0, 100 - (deviation / 15) * 100)

        issues = []
        if score < 70:
            issues.append({
                "component": "spine_alignment",
                "severity": get_score_label(score),
                "message": "Your torso is leaning to one side — sit or stand upright.",
            })

        return {"score": score, "issues": issues}
