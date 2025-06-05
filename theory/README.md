| Metric           | Meaning                                                                    | Real-world Example  |
| ---------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **IDF1**         | Identity F1 score (Higher)                                                 | Keep assigning the correct ID to car A & B across frames without mix-up|
| **IDP**          | Identity Precision                                                         | Out of all track IDs your model predicted, how many were correct|
| **IDR**          | Identity Recall                                                            | Out of all real car identities, how many did you correctly follow |
| **MOTA**         | Multi-Object Tracking Accuracy (summary of FP, FN, ID switches) (Higher)   | If many cars missed (FN), make ID mistakes (ID switches), MOTA goes down |
| **MOTP**         | Multi-Object Tracking Precision (localization error of bounding boxes)     | Lower = better box alignment with ground truth |
| **MT / PT / ML** | Mostly Tracked / Partially / Mostly Lost                                   | Total 9 cars: 6 were well-tracked(MT), 2 sometimes(PT), 1 mostly lost(ML) |
| **FP / FN**      | False Positives / False Negatives                                          | FP: Detect a car when none is there. FN: Missed a real car|
| **IDs**          | ID switches                                                                | If Car A "ID 1" in frame 0, but then "ID 3" later, this is a switch|
| **FM**           | Fragmentations                                                             | The track is broken, disappears, then reappears |






Phase 1: Core MOT 
Input: Left camera images
YOLOv8 → BYTETrack → KITTI format
Visualize & evaluate with KITTI

Phase 2: Add Stereo Vision
Use KITTI right images and camera calibration
Run a stereo depth model like AANet or PSMNet
Compute disparity maps → convert to depth maps
Use calibration to compute 3D coordinates → pointcloud (optional)


"MOTA (Multiple Object Tracking Accuracy)"
It measures overall tracking performance by combining False Positives, False Negatives, and ID switches (penalizes FP + FN + ID switches).
A higher MOTA means fewer mistakes across all tracked objects.
MOTA = 1 - (FP + FN + ID switches) / total GT detections


MOTP (Multiple Object Tracking Precision)
Measures how precisely our predicted boxes match the ground truth in terms of IoU.


ID Switches
This is how many times our tracker accidentally assigned different IDs to the same object across frames — a key metric for real-time ADAS.

MT (Most Tracked)
Tracks with >80% of lifetime tracked well

ML (Most Lost)
Tracks with <20% of lifetime tracked

MOTA for coverage, IDF1 for ID preservation. HOTA for balance

BYTETrack actually uses:
IOU-only matching (no appearance)
Tracks both high conf detections and low conf for association
Simple Kalman (center x, y, aspect ratio, height)


DetA (Detection Accuracy): How good are detections (YOLO)?
AssA (Association Accuracy): How well are linking objects over time (BYTETrack)?
MOTA is affected by both. HOTA separates them.
