# scripts/

This folder contains all core scripts for the real-time Multi-Object Tracking (MOT) pipeline on the KITTI Tracking dataset, using YOLOv8 for object detection and BYTETrack for class-agnostic identity tracking. The full pipeline also includes class reassignment logic, KITTI-compatible output, quantitative evaluation, and visualizations.

---

## Pipeline Overview
KITTI Image → YOLOv8 → Detection (.txt) → BYTETrack → Tracking (.txt) → KITTI Eval + Visualization

---

## Files

### `yolov8_detect.py` (Detection, YOLOv8)
- Function: Runs YOLOv8 on KITTI frames for car, person, and bicycle classes.
- Class Logic:
  - Calculates IoU between person and bicycle boxes.
  - If overlap is high, assumes cyclist (discarded); else keeps as pedestrian.
- Output: Writes detections in BYTETrack format with only class IDs 0 (person) and 2 (car).

### `bytetrack_tracker.py` (Tracking, BYTETrack + Class Mapping)
- Function: Applies BYTETrack on detections to create persistent identity tracks.
- Problem: BYTETrack is class-agnostic.
- Solution: Matches tracker output box with the best IoU detection box from YOLO:
  - If IoU > 0.3, assign detection's class ID.
  - Else assign fallback class (car) for unmatched boxes (based on KITTI prior).
- Output: Tracker results are saved in KITTI format for downstream evaluation.

### `evaluation.py` (KITTI Format Evaluation)
- Function: Computes MOT metrics (MOTA, IDF1, FP, FN, etc.) between GT and predictions.
- Process:
  - Filters GT and predictions for car and pedestrian classes.
  - Computes pairwise IoUs.
  - Uses MOT accumulator to evaluate frame-wise matching.
- Note: Follows KITTI benchmark style; ignores 'DontCare', 'Van', etc.

### visualize_results.py (Tracking Visualization)
- Function: Visualizes frame-by-frame tracking:
  - Green: Ground truth boxes
  - Blue: Predicted tracked boxes with IDs
- Output:
  - Annotated video for quick review
  - Optional conversion to GIF for preview in repor
