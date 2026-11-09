# Lesson 3: make your own gestures

In this lesson you will design a gesture, turn its shape into measurements, and add a rule that gives it a name. Start with a pinch, then try a peace sign. After that, you will learn how movement gestures such as waving differ from poses.

This is a guided exercise: the snippets below are changes for you to make in `patterns/handrecognition.py`. They have not been inserted into the running program. Your existing waving code continues to work.

## 1. Understand what the computer receives

Your camera does not send the word “hand.” It sends an image made of pixels. MediaPipe processes that image and estimates 21 locations on a hand. We call those locations **landmarks**.

Your program stores them here:

```python
points = result.hand_landmarks[0]
```

`result.hand_landmarks` contains the detected hands. Python counts from zero, so `[0]` selects the first hand. The current project asks MediaPipe to track only one hand.

`points[8]` selects landmark 8 on that hand. Each point has `.x`, `.y`, and `.z` coordinates. For our first gestures, use only x and y.

- **x** describes left-to-right position. Approximately 0 is the left edge; 1 is the right edge.
- **y** describes top-to-bottom position. Approximately 0 is the top edge; 1 is the bottom edge.
- **z** estimates depth relative to the wrist. It is not a direct physical distance measurement from your camera.

For example, in a 640-pixel-wide frame, `x = 0.5` means approximately pixel 320. Your drawing code multiplies normalized coordinates by the image width and height to locate the green dots.

Your program mirrors the frame before detection. Think in terms of the displayed image when debugging left and right.

## 2. Learn the landmark numbers

| Part | Landmark numbers, from base toward tip |
| --- | --- |
| Wrist | 0 |
| Thumb | 1, 2, 3, **4** |
| Index finger | 5, 6, 7, **8** |
| Middle finger | 9, 10, 11, **12** |
| Ring finger | 13, 14, 15, **16** |
| Pinky | 17, 18, 19, **20** |

The bold numbers are fingertips. You do not need to memorize the whole table. Look up the points needed for the gesture you are building.

Optional exercise: label the dots. Inside `process()`, replace the loop that draws green dots with this loop:

```python
for number, point in enumerate(points):
    position = (int(point.x * width), int(point.y * height))
    cv2.circle(frame, position, 4, (60, 230, 60), -1)
    cv2.putText(
        frame, str(number), position,
        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1,
    )
```

`enumerate()` supplies both the item number and the item itself. `str(number)` converts a number into text so OpenCV can draw it.

Run the camera, move your fingers slowly, and find landmarks 4 and 8. Press Q before editing again.

## 3. Describe a gesture before writing code

“Recognize my gesture” is too vague to turn into a rule. Write a description that you could check using the points.

For a **pinch**, use this first definition:

> The thumb tip and index fingertip are close together compared with the width of my palm.

This suggests three steps: measure fingertip distance, measure palm width, then divide one by the other.

Why divide? When you move toward the camera, both your hand and the gap look larger. A ratio makes the rule less sensitive to distance from the camera. It does not solve every perspective or tracking problem.

## 4. Build your first custom gesture: pinch

Find the helper named `distance()` inside `process()`. It is already in your file:

```python
def distance(a, b):
    return math.hypot(
        (points[a].x - points[b].x) * width / height,
        points[a].y - points[b].y,
    )
```

`a` and `b` are landmark numbers. `math.hypot()` calculates the straight-line distance using horizontal and vertical differences. Multiplying the horizontal difference by `width / height` accounts for the image shape, so distances are comparable on both axes.

Directly **after the entire helper function**, add this code. Align it with `extended = sum(...)`, not with the helper's `return`:

```python
palm_width = max(distance(5, 17), 0.001)
pinch_ratio = distance(4, 8) / palm_width
pinching = pinch_ratio < 0.30
```

Read it one line at a time:

1. `distance(5, 17)` measures across the palm, from the index base to the pinky base.
2. `max(..., 0.001)` prevents division by zero if the estimate becomes extremely small.
3. `distance(4, 8)` measures the gap between thumb and index tips.
4. Dividing by palm width produces a ratio. A ratio of 0.20 means the gap is one fifth of the palm width in this image measurement.
5. `< 0.30` asks whether the gap is less than 30% of palm width. The answer is `True` or `False`, called a Boolean.

`0.30` is a starting threshold to experiment with, not a universal correct value. A side-on hand makes palm width unreliable; start with your palm facing the camera.

Now find the final return statement in `process()`:

```python
return "Waving (rule estimate)" if waving else "Hand visible: no wave detected"
```

Replace that one statement with:

```python
if pinching:
    return "Pinching (rule estimate)"
if waving:
    return "Waving (rule estimate)"
return "Hand visible: no known gesture"
```

Leave the calculations of `extended`, `size`, and `waving` above these returns. That lets the movement history keep updating even while the displayed label is pinch.

`return` ends this call to `process()` and sends text back to `webcam.py`. The webcam program draws that text. The first matching condition wins, so pinch has display priority here.

Run from the project terminal:

```powershell
.\.venv\Scripts\python.exe webcam.py --hands
```

Touch your thumb and index tips, then separate them. Watch the label change.

## 5. See the measurement instead of guessing

Temporarily insert this after calculating `pinch_ratio`:

```python
cv2.putText(
    frame, f"Pinch ratio: {pinch_ratio:.2f}", (15, height - 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2,
)
```

The `f` makes this a formatted string: Python substitutes the value inside braces. `:.2f` shows two decimal places. Drawing the value on the frame is easier to follow than printing it for every camera frame.

Observe ratios for a clear pinch and an open gap. Pick a threshold between those groups, then repeat at different camera distances. If the groups overlap, changing a threshold alone will not fix the ambiguity. Improve the definition, hand visibility, or measurements.

## 6. A second gesture: peace sign

Start with a limited definition: the index and middle fingers are extended, the ring and pinky are folded, and the two raised fingertips are separated. Hold your palm toward the camera.

Your existing code estimates extended fingers by comparing tip-to-wrist and joint-to-wrist distances. We can reuse that idea. It is an approximation; curled fingers and hand rotations can fool it.

Below your pinch calculations, add:

```python
index_up = distance(8, 0) > distance(6, 0) * 1.15
middle_up = distance(12, 0) > distance(10, 0) * 1.15
ring_up = distance(16, 0) > distance(14, 0) * 1.15
pinky_up = distance(20, 0) > distance(18, 0) * 1.15
tips_apart = distance(8, 12) / palm_width > 0.35

peace_sign = (
    index_up and middle_up
    and not ring_up and not pinky_up
    and tips_apart
)
```

`and` means every condition must be true. `not` reverses a Boolean: `not ring_up` means the ring finger did not pass our extension check. Parentheses let us spread an expression across lines for readability.

Add this immediately before `if waving:` in the return section:

```python
if peace_sign:
    return "Peace sign (rule estimate)"
```

Your priority is now pinch, then peace sign, then waving. This is a display decision, not a claim that gestures cannot overlap. Later, a list of active labels can represent simultaneous activities.

Exercise: try two fingers held together, a peace sign, three raised fingers, and a closed fist. Record which ones confuse your rules. Tune one threshold at a time.

## 7. Shape gestures and movement gestures

A pinch or peace sign can be estimated from one frame. A wave requires a sequence: a still hand in the middle of a wave can look exactly like a hand that never moves.

Your `WaveMotion` class remembers recent `(timestamp, x)` pairs. A **class** groups related data and functions. `self.samples` is the history belonging to that particular motion tracker. A `deque` is a container that can efficiently discard the oldest items.

The existing wave rule:

1. Clears history when the hand no longer passes the open-hand check.
2. Adds the current time and palm position.
3. Removes positions older than 1.5 seconds.
4. Ignores tiny changes that may be tracking noise.
5. Counts substantial changes of horizontal direction.
6. Reports a wave when it finds at least two reversals.

Larger movement thresholds require larger gestures. A longer history accepts slower gestures but may leave a label visible longer after movement stops. Neither setting directly means “more accurate.” Test the effect you want.

To design an up-and-down gesture, follow the same approach with the palm's y coordinate. Give that gesture its **own** motion tracker; sharing one history between horizontal and vertical measurements mixes unrelated values. Remember that image y increases downward.

## 8. Stop flickering and repeated actions

A threshold can make a label flicker when a measurement sits near its boundary. Two useful ideas are:

- **Hysteresis:** enter pinch below 0.25, but stay pinching until the ratio rises above 0.40. This requires remembering the previous state. The gap between entry and exit thresholds prevents small changes from toggling the label constantly.
- **Duration:** require a condition to remain true for, for example, 0.2 seconds before accepting it. Measure elapsed time rather than counting frames, because frame rate changes between computers.

Displaying “Pinching” on every frame is fine. Triggering an action every frame is different: one held pinch could accidentally trigger dozens of actions. For a future counter, trigger when the state changes from inactive to active, and require release before another trigger. For this lesson, keep gestures as labels while you learn how reliable they are.

## 9. Design any new gesture with this worksheet

Copy this into your notes for each idea:

| Question | Example: pinch |
| --- | --- |
| What should it mean? | Thumb and index tips nearly touch. |
| Which points matter? | 4 and 8; 5 and 17 for scale. |
| Which measurements describe it? | Fingertip gap divided by palm width. |
| Does it require history? | No, but a short hold can improve stability. |
| What should not trigger it? | Open hand, fist, fingertips merely crossing in the image. |
| What views are supported initially? | One visible hand, palm facing the camera. |
| How does it reset? | Tips separate or the hand disappears. |

Try an open palm next. Then try a fist, noting that “none of my four fingers looks extended” does not necessarily prove a fist: a side-on or badly tracked hand may look similar. Keep an unknown result for ambiguous cases.

## 10. Test before calling a gesture finished

For each gesture, try ten deliberate attempts and ten confusing non-examples. Repeat in another session with different lighting and camera distance. Write down correct detections, missed attempts, and false detections. Decide in advance what counts as a successful attempt; a brief incorrect label still matters.

| Test | Expected result | Actual result | Change to try |
| --- | --- | --- | --- |
| Open hand held still | No pinch or wave | Fill in | Fill in |
| Thumb and index touching | Pinch | Fill in | Fill in |
| Reach for a drink | No wave | Fill in | Fill in |
| Hand leaves the frame | Unknown | Fill in | Fill in |

Do not invent accuracy numbers from a few successful demonstrations. These small tests help you improve the baseline. More formal evaluation comes later.

## 11. When should you train a model?

Rules are useful when you can describe the gesture with a few clear measurements. Consider training a classifier when many gestures overlap, hand orientation varies widely, or rules become difficult to maintain.

A future learning workflow is: collect labeled landmark examples, normalize them for position and scale, split by recording session, train a small classifier, and evaluate on untouched sessions. For movement gestures, collect sequences rather than isolated frames. Include examples of unknown gestures. A classifier's score still needs evaluation before you treat it as reliable confidence.

You do not need to train a model to finish this lesson. A readable rule, careful tests, and an explanation of failure cases already make a useful learning milestone.

## If something breaks

- **IndentationError:** code inside `process()` normally has eight leading spaces; code inside its nested `distance()` helper has twelve. Align new gesture calculations with `extended = sum(...)`.
- **NameError for `distance`:** place the calculations after the helper's definition and inside `process()`.
- **NameError for `pinching`:** calculate it before the return section.
- **No new label:** keep new conditions before the final fallback `return`; code after a return is not reached on that path.
- **Lots of console messages:** your current file prints wave/no-wave every frame. You can remove that print line; it is not needed for recognition.
- **Two hands behave strangely:** this version tracks one hand. Test each gesture using one visible hand first.

## Completion checklist

- Explain what landmarks 4 and 8 represent.
- Explain why a distance ratio helps when the hand moves closer.
- Add pinch and display its measured ratio.
- Add a second shape gesture yourself.
- Test confusing non-examples and write down one limitation.
- Explain why waving needs history but a basic pinch does not.

Reference: [Google's official Hand Landmarker guide](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) describes the 21 landmarks and model outputs. The gesture thresholds and exercises here are experimental rules for this project.
