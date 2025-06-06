# Input/

This folder contains three types of input files used in the project:

- `kitti_label/` — Ground truth labels used for YOLOv8 training and tracking evaluation.
- `detection_file/` — Detections from the YOLOv8 model, formatted for BYTETrack.
- `tracker_file/` — Tracker output from BYTETrack, formatted for KITTI tracking evaluation.

## Format Specifications

### 1. KITTI Ground Truth Format
Used for YOLOv8 training and tracking evaluation.

`frame id | track id | class | trunc | occ | alpha | bbox left | top | right | bottom | ...3D info...`


**Example:**

>0 -1 DontCare -1 -1 -10.00 219.31 188.49 245.50 218.56 -1000.00 -1000.00 -1000.00 -10.00 -1.00 -1.00 -1.00

---

### 2. BYTETrack Detection Format
Used as input to BYTETrack. Each line corresponds to one detection.

`frame_id | -1 | x1 | y1 | x2 | y2 | score | class_id`

**Example:**

>0,-1,1109.93,174.78,1200.78,315.24,0.85,0

---

### 3. Tracker Output Format (KITTI-style)
Output from BYTETrack, used for KITTI-style multi-object tracking evaluation.

`frame_id | track_id | class | trunc | occ | alpha | bbox_left | top right | bottom | ... (3D info optional)`

**Example:**

>0 477 0 0 0 -1 1109.93 174.78 1200.78 315.24 0 0 0 0

---
