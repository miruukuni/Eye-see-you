# What Am I Doing?

A beginner Python project that will use a webcam to recognize waving, facing the monitor, and visible phone interaction.

**Current version: webcam preview only. Activity recognition has not been implemented.**

## Start here

Python and OpenCV were found on your computer during setup. To try the first milestone:

1. Open this `activity-recognition` folder in File Explorer.
2. Right-click an empty area and choose **Open in Terminal**. On some Windows versions, use **Show more options** first.
3. Run:

```powershell
python webcam.py
```

You should see a mirrored camera view and a frames-per-second (FPS) counter. Click the video window and press **Q** or **Escape** to stop. Closing the window also stops it.

The program displays frames locally. It contains no video recording or upload code.

To check the dependency without opening the camera:

```powershell
python webcam.py --check
```

If OpenCV is missing, install it using:

```powershell
python -m pip install -r requirements.txt
```

On another machine, you can keep dependencies in a project environment. Run these once inside this folder, then use `.\.venv\Scripts\python.exe webcam.py` to start:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Define the activities before building the model

| Activity                  | Initial definition                                                                                                                                        | Examples that should not trigger it                                   |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Waving                    | An open hand moves side to side repeatedly over a short interval.                                                                                         | Holding a hand still, reaching for a cup, touching your face.         |
| Facing the monitor        | Your visible face is approximately oriented toward the screen-mounted camera. This is a proxy for looking at the monitor, not proof of gaze or attention. | Looking away or having no reliably visible face.                      |
| Visible phone interaction | A visible phone is held near a hand, with visual evidence of interaction. This is an estimate of phone use.                                               | A phone lying on the desk or another rectangular object in your hand. |

Use a camera mounted near the monitor for the facing-monitor proxy. If the camera is elsewhere, that interpretation changes.

These activities can overlap: you can wave while facing the monitor. Eventually show separate activity indicators, with **unknown** when visibility or evidence is insufficient. Do not force every moment into one of the three labels.

## Build one milestone at a time

1. **Camera preview — included.** Read and display frames; understand the loop and quit controls.
2. **Hand tracking.** Add MediaPipe Hand Landmarker and draw hand points. It provides landmarks, not a waving prediction by itself.
3. **Waving baseline.** Track the palm position over a short time window, normalize movement by hand size, and count direction changes. Combine movement with an open-hand check. Start with readable rules and test the confusing examples above.
4. **Facing-monitor estimate.** Add face landmarks and estimate face orientation relative to the camera. Calibrate a comfortable forward-facing position; report unknown when the face is not reliably visible.
5. **Phone interaction estimate.** Add a pretrained detector that supports cell phones. Combine phone detections with nearby hand positions across frames; check whether holding a phone and using it can actually be distinguished in your camera view.
6. **Learn from examples.** Label short clips and compare a small trained classifier with the rules. Keep a separate output for each activity so overlap is possible.
7. **Portfolio demo.** Add activity indicators, a timeline, results on unseen recordings, and a short demo video.

## What to learn from this first file

Read `webcam.py` from top to bottom:

- `import` loads a library so your code can use it.
- `main()` groups the program's main steps into a function.
- `VideoCapture` opens the camera; `read()` gets the next frame.
- `while True` repeats until a quit condition is reached.
- `flip()` mirrors an image; `putText()` draws text on it.
- `finally` makes sure the camera gets released.

Try these small edits, one at a time: change the window title, change the displayed message, then remove mirroring and observe what changes. Run after each edit.

## How to evaluate the recognition later

- Record positive examples and confusing negative examples in several separate sessions.
- Split training and test data by recording session, not randomly by individual frames. Nearby frames from one recording are very similar.
- For each activity, report how many detections were correct (precision) and how many real occurrences you caught (recall).
- Include overlap, low light, hands outside the image, and a partly hidden phone.
- Keep a small table of failures and the changes you tried. Compare the original rules with any trained model on the same held-out recordings.

## Troubleshooting

- **Camera will not open:** close other camera apps and check Windows **Settings > Privacy & security > Camera**, including desktop app access.
- **Wrong camera:** try `python webcam.py --camera 1`.
- **No window support:** this needs desktop OpenCV, not the headless package. The installed OpenCV was checked for Windows window support during setup.
- **Text is clipped:** make the camera output larger in a later exercise or reduce the text scale in `putText()`.

## Official references

- [OpenCV camera tutorial](https://docs.opencv.org/4.12.0/dd/d43/tutorial_py_video_display.html)
- [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker)
- [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker)
- [MediaPipe Object Detector](https://ai.google.dev/edge/mediapipe/solutions/vision/object_detector)
