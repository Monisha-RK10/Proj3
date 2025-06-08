# Real-Time MOT using YOLOv8 & BYTETrack on KITTI: Cyclist Filtering, Evaluation, & ROS2 Deployment

This project implements a **tracking-by-detection** pipeline for autonomous driving scenarios using YOLOv8 for real-time object detection, BYTETrack for identity-preserving tracking, quantitative evaluation using MOTMetrics, and ROS2 for deployment.


---

## Dataset
- **[KITTI Tracking Dataset](http://www.cvlibs.net/datasets/kitti/eval_tracking.php)**
- Real-world driving scenes captured from a moving vehicle
- Annotated bounding boxes for object categories like `Car`, `Pedestrian`, and `Cyclist`
- Used **sequence 0000** for this project
  
----

## Challenges & Solutions

### Challenge 1: Class mismatch
- YOLOv8 (COCO) has `person`, `car`, `bicycle`
- KITTI expects `Car`, `Pedestrian`, `Cyclist`

**Solution:** Implemented a **cyclist filter**, if IoU between `person` and `bicycle` is high → discard as `Cyclist`

### Challenge 2: BYTETrack ignores class labels
- BYTETrack only tracks bounding boxes

**Solution:** After tracking, reassign **class IDs** to each track by matching with original YOLO detections using IoU

---


## Pipeline Overview 


- **Input:** Left camera frames (`image_02/`) + KITTI labels (`label_02/`)
- **Steps:**
  - **Detection:** YOLOv8 for object detection
  - **Cyclist Filter:** Match `person` and `bicycle` using IoU
  - **Tracking:** BYTETrack with filtered detections
  - **Class ID assignment:** Match tracked boxes with original detection boxes
  - **Evaluation:** Compare against KITTI labels using `motmetrics`
  - **Deployment:** ROS2 publisher → subscriber → detection + tracking → publish result
- **Output:** MOT metrics + tracked frames visualized in **Rviz**

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
## Observation

| Frame | Person Detected? | Bicycle Detected? | IoU Match | Final Output            |
| ----- | ---------------- | ----------------- | --------- | ----------------------- |
| 1–10  | Yes              | Yes               | Yes       | No (filtered out)        |
| 11–20 | Yes              | No                | No        | Yes (shown as pedestrian) |

---

## Future Directions
No appearance cues were used, so tracking is purely IoU-based. There is still room to reduce identity switches and false positives, possibly by:

- Adding appearance-based re-ID (e.g. DeepSORT)
- Using depth-aware filtering to improve spatial consistency
- Filtering out very low-confidence boxes

## Demo Video

<p align="center">
  <img src="videos/kitti_tracking_output.gif" width="1000"/>
</p>

[Download full MP4 video](videos/kitti_tracking_output.mp4)

## Author

**Monisha**  
Connect via [Medium](https://medium.com/@monishatemp20)  

---
