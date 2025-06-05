Phase 1: Core MOT 
Input: Left camera images
YOLOv8 → BYTETrack → KITTI format
Visualize & evaluate with KITTI

BYTETrack actually uses:
IOU-only matching (no appearance)
Tracks both high conf detections and low conf for association
Simple Kalman (center x, y, aspect ratio, height)

| Metric           | Meaning                                                                    | Real-world Example  |
| ---------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------- |
| **IDF1**         | Identity F1 score (Higher)                                                 | Keep assigning the correct ID to car A & B across frames without mix-up|
| **IDP**          | Identity Precision                                                         | Out of all track IDs your model predicted, how many were correct|
| **IDR**          | Identity Recall                                                            | Out of all real car identities, how many did you correctly follow |
| **MOTA** for coverage | Multi-Object Tracking Accuracy (summary of FP, FN, ID switches) (Higher)| If many cars missed (FN), make ID mistakes (ID switches), MOTA goes down |
| **MOTP**         | Multi-Object Tracking Precision (localization error of bounding boxes) (Lower)| Measures how precisely our predicted boxes match the ground truth (IoU)|
| **MT / PT / ML** | Mostly Tracked ( >80%)/ Partially / Mostly Lost  <20%         | Total 9 cars: 6 were well-tracked(MT), 2 sometimes(PT), 1 mostly lost(ML) |
| **FP / FN**      | False Positives / False Negatives                                          | FP: Detect a car when none is there. FN: Missed a real car|
| **IDs** for ID preservation | ID switches                                                                | If Car A "ID 1" in frame 0, but then "ID 3" later, this is a switch|
| **FM**           | Fragmentations                                                             | The track is broken, disappears, then reappears |



