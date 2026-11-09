"""Track one hand; estimate waving from repeated horizontal palm movement."""

from collections import deque
from pathlib import Path
import math
import time


class WaveMotion:
    """Count substantial direction changes within a short time window."""

    def __init__(self):
        self.samples = deque()

    def update(self, timestamp, x, hand_size, open_hand):
        if not open_hand:
            self.samples.clear()
            return False
        self.samples.append((timestamp, x))
        while self.samples and timestamp - self.samples[0][0] > 1.5:
            self.samples.popleft()
        anchor = self.samples[0][1]
        direction = 0
        reversals = 0
        for _, position in self.samples:
            delta = position - anchor
            if abs(delta) < max(hand_size * 0.45, 0.025):
                continue
            next_direction = 1 if delta > 0 else -1
            if direction and direction != next_direction:
                reversals += 1
            direction = next_direction
            anchor = position
        return reversals >= 2


class HandRecognition:
    def __init__(self):
        try:
            import mediapipe as mp
        except ImportError:
            raise SystemExit(
                "Install tracking first: python -m pip install -r requirements.txt"
            )
        model = Path(__file__).resolve().parents[1] / "models" / "hand_landmarker.task"
        if not model.is_file():
            raise SystemExit(
                "Hand model missing. Follow the setup steps in put_the_teaching_docs_here/02-hand-tracking.md"
            )
        self.mp = mp
        self.motion = WaveMotion()
        self.started = time.perf_counter()
        self.last_timestamp = -1
        self.detector = mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_hands=1,
            )
        )

    def process(self, frame):
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        timestamp = max(
            self.last_timestamp + 1, int((time.perf_counter() - self.started) * 1000)
        )
        self.last_timestamp = timestamp
        result = self.detector.detect_for_video(
            self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb), timestamp
        )
        if not result.hand_landmarks:
            self.motion.samples.clear()
            return "Unknown: no visible hand"
        points = result.hand_landmarks[0]
        height, width = frame.shape[:2]
        for point in points:
            cv2.circle(
                frame,
                (int(point.x * width), int(point.y * height)),
                4,
                (60, 230, 60),
                -1,
            )

        # Distances use pixel aspect ratio so a wide image does not distort them.
        def distance(a, b):
            return math.hypot(
                (points[a].x - points[b].x) * width / height, points[a].y - points[b].y
            )

        extended = sum(
            distance(tip, 0) > distance(joint, 0) * 1.15
            for tip, joint in ((8, 6), (12, 10), (16, 14), (20, 18))
        )
        size = abs(points[5].x - points[17].x)
        waving = self.motion.update(timestamp / 1000, points[9].x, size, extended >= 3)
        return "Waving (rule estimate)" if waving else "Hand visible: no wave detected"

    def close(self):
        self.detector.close()
