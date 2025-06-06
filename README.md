# Real-Time Multi-Object Tracking for Autonomous Driving using YOLOv8 and BYTETrack with KITTI Evaluation

This project implements a **tracking-by-detection** pipeline for autonomous driving scenarios using:

- **YOLOv8** for real-time object detection
- **BYTETrack** for identity-preserving multi-object tracking
- Evaluation against the **KITTI Tracking Benchmark** using `motmetrics`

---

## Dataset

- **[KITTI Tracking Dataset](http://www.cvlibs.net/datasets/kitti/eval_tracking.php)**
- Real-world driving scenes
- Annotated bounding boxes for object categories like `Car`, `Pedestrian`, and `Cyclist`
- Used **sequence 0000** for this project

## Pipeline Overview
- Input: Left camera images
- YOLOv8 → BYTETrack → KITTI format
- Visualize & evaluate with KITTI

---

## Detection Confidence Tuning Results (YOLOv8 + BYTETrack)

I evaluated the effect of varying the confidence threshold (`conf`) from 0.5 to 0.8. Below are the key MOT metrics across settings. 

| Conf | IDF1  | IDP  | IDR  | Rcll | Prcn | FP  | FN  | IDs | MOTA | Comments |
|------|-------|------|------|------|------|-----|-----|------|------|----------|
| 0.5  | 60.0% | 47.7% | 80.7% | 89.3% | 52.8% | 334 | 45  | 9  | 7.4%  | Good balance |
| 0.6  | 62.5% | 51.5% | 79.7% | 86.2% | 55.6% | 288 | 58  | 9  | 15.3% | **Best IDF1**, slightly more FN |
| 0.7  | 60.7% | 57.0% | 64.9% | 70.6% | 62.1% | 181 | 123 | 12 | 24.6% | Too many missed GTs (FN↑) |
| 0.8  | 43.2% | 58.1% | 34.4% | 39.4% | 66.5% | 83  | 254 | 10 | 17.2% | FN very high, recall broken |

> **At conf=0.6**, I achieved the highest IDF1 (62.5%) and a solid MOTA of 15.3% with only 1 mostly lost track. Precision and recall were well balanced (55.6% / 86.2%), and false positives dropped meaningfully. I chose this setting as the optimal point in the precision-recall trade-off for multi-object tracking on KITTI.

---

## Future Directions
No appearance cues were used, so tracking is purely IoU-based. There is still room to reduce identity switches and false positives, possibly by:

- Adding appearance-based re-ID (e.g. DeepSORT)
- Using depth-aware filtering to improve spatial consistency
- Filtering out very low-confidence boxes

## Demo Video

<p align="center">
  <img src="videos/output_yolo_bytetrack.gif" width="1000"/>
</p>

[Download full MP4 video](videos/output_yolo_bytetrack.mp4)

