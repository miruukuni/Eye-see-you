# Step 2: hand tracking and waving

Continue with [Lesson 3: make your own gestures](03-make-your-own-gestures.md) after trying this step. It explains landmarks, custom pinch and peace-sign rules, movement gestures, and testing from a beginner's perspective.

Run these commands in the Eye-can-see-you project terminal. They use your existing project environment.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
New-Item -ItemType Directory -Force models
Invoke-WebRequest -Uri 'https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task' -OutFile models\hand_landmarker.task
.\.venv\Scripts\python.exe webcam.py --hands
```

The download is a pretrained Google MediaPipe hand model. Camera frames are processed locally; this code does not upload or record them. If installation says no compatible distribution exists, share that message before changing your Python environment.

Hold one open hand in view and wave left and right several times. Green dots mark hand landmarks. Q or Escape closes the preview. Without `--hands`, the original camera preview still works.

## How it works

1. OpenCV reads a frame and mirrors it.
2. MediaPipe estimates 21 hand points, called landmarks.
3. We check whether at least three fingers look extended.
4. We keep 1.5 seconds of horizontal palm positions and look for two substantial direction changes.

MediaPipe finds the points; our own rules decide whether their movement resembles waving. This is a first baseline, not a trained activity classifier or a probability score. Only one hand is tracked. Changing hands without a detection gap, rotating your hand, and moving the camera can confuse it.

Try a still open hand, a closed fist, reaching sideways, and a real wave. Note mistakes. In `patterns/handrecognition.py`, change the `1.5` second window or the `0.45` movement threshold one at a time and compare the results.

Next: test this baseline in your camera view, then add the facing-monitor estimate and phone detection separately. They are not implemented yet.

[Official MediaPipe Hand Landmarker documentation](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
