### KITTI Tracking Performance (YOLOv8 + BYTETrack on Seq 0000)

| Metric | Value |
|--------|-------|
| IDF1   | 71.7% |
| MOTA   | 58.0% |
| MOTP   | 0.183 |
| Recall | 86.0% |
| Precision | 76.6% |
| ID Switches | 4 |
| Fragments | 6 |
| Mostly Tracked | 6 |
| Mostly Lost | 1 |









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
