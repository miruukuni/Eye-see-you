"""Milestone 1: display a webcam feed. Activity recognition comes next."""

import argparse
import sys
import time

try:
    import cv2
except ImportError:
    print("OpenCV is missing. Run: python -m pip install -r requirements.txt")
    raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Camera number (default: 0)")
    parser.add_argument("--check", action="store_true", help="Check OpenCV without opening the camera")
    args = parser.parse_args()

    if args.check:
        print(f"Python {sys.version.split()[0]}; OpenCV {cv2.__version__}")
        print("OpenCV imported successfully. No camera was opened.")
        return 0

    # A camera produces a sequence of images, called frames.
    camera = cv2.VideoCapture(args.camera)
    window_name = "Activity Recognition - Milestone 1"

    try:
        if not camera.isOpened():
            print("Could not open the camera. Close other camera apps and check Windows camera permissions.")
            print("If you have another camera, try: python webcam.py --camera 1")
            return 1

        print("Camera open. Click the video window and press Q or Escape to quit.")
        print("This milestone displays video only; it does not recognize activities or save recordings.")
        previous_time = time.perf_counter()
        fps = 0.0

        while True:
            success, frame = camera.read()
            if not success:
                print("Could not read a camera frame. Check the camera connection.")
                return 1

            # Mirror the image so moving your hand feels natural.
            frame = cv2.flip(frame, 1)
            now = time.perf_counter()
            elapsed = now - previous_time
            previous_time = now
            if elapsed > 0:
                fps = 0.9 * fps + 0.1 / elapsed

            # These are status messages, not predictions.
            lines = [
                "Milestone 1: camera preview",
                "Activity recognition: not added yet",
                f"FPS: {fps:.0f} | Q / Esc: quit",
            ]
            for index, line in enumerate(lines):
                position = (15, 30 + index * 30)
                cv2.putText(frame, line, position, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 4)
                cv2.putText(frame, line, position, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            cv2.imshow(window_name, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), ord("Q"), 27):
                break
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break

        return 0
    finally:
        # Release the camera even if the program stops unexpectedly.
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nStopped.")
    except cv2.error as error:
        print(f"OpenCV could not complete the camera preview: {error}")
        raise SystemExit(1)
