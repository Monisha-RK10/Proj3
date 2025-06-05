## KITTI Tracking Performance (YOLOv8 + BYTETrack on Seq 0000)

| **Metric** | IDF1 |  IDP  | IDR |  Rcll | Prcn | GT | MT | PT | ML | FP | FN | IDs | FM  | MOTA | MOTP | IDt | IDa | IDm|
|------------|------|-------|-----|-------|------|----|----|----|----|----|----|-----|-----|------|------|-----|-----|----|
| **Value** |69.5% | 65.1% |74.5% |88.9%| 77.7%|  9 |  6|   2  | 1  | 62|  27 |  14 |  6  | 57.6% | 0.247 |12  | 5 |   3|

---
## Evaluation Result (YOLOv8 + BYTETrack on KITTI)
- **IDF1 (69.5%)**: Good identity consistency across frames
- **IDP / IDR (65.1% / 74.5%)**: Balanced precision and recall of track IDs
- **FP / FN (62 / 27)**: False positives slightly higher, possible over-detections
- **IDs (14)**: Identity switches still present, can improve
- **MOTA (57.6%)**: Overall multi-object tracking accuracy is reasonable for basic IoU-based tracking
- **MT / PT / ML (6 / 2 / 1)**: 6 cars well-tracked, 2 partially, 1 mostly lost
---
## Future Directions
No appearance cues were used, so tracking is purely IoU-based. There is still room to reduce identity switches and false positives, possibly by:

- Adding appearance-based re-ID (e.g. DeepSORT)
- Using depth-aware filtering to improve spatial consistency
- Filtering out very low-confidence boxes

---
