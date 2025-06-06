# Step 2: Run tracker on all the detection from YOLOv8
# This function does the following:
# Updates tracker for detection done by YOLOv8 for specific classes,
# Computes IoU between track box & all detections to assign class, and
# Writes results in KITTI format for evaluation.

import os
import cv2
import numpy as np
from types import SimpleNamespace
from yolox.tracker.byte_tracker import BYTETracker

# Config (Object-style config)
args = SimpleNamespace(  # quick way to create an object with attributes instead of a dictionary
    track_thresh=0.5,    # detection confidence threshold, higher = fewer detections, but more reliable
    track_buffer=30,     # how long to keep a lost track, helps in occlusion recovery (if a car is hidden briefly)
    match_thresh=0.8,    # IOU threshold for associating new detections with existing tracks, higher = stricter match, may lose fast-moving objects
    mot20=False,         # use MOT20-specific thresholds
    min_box_area=100     # filter very small boxes
)
image_dir = "/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000"
det_file = "/content/0000.txt"
output_txt = "/content/drive/MyDrive/kitti_tracking/tracks_bytetrack/0000.txt"

# Setup
tracker = BYTETracker(args, frame_rate=30)
image_files = sorted(os.listdir(image_dir))

# Load detections
frame_detections = dict()
with open(det_file, "r") as f:
    for line in f:
        parts = line.strip().split(',')
        frame_id = int(parts[0])
        x1, y1, x2, y2 = map(float, parts[2:6])
        conf = float(parts[6])
        cls_id = int(parts[7])
        if cls_id in [0, 1, 2]:  # person, bicycle, car (COCO IDs)  3-class filtering happens again
            det = [x1, y1, x2, y2, conf, cls_id]
            frame_detections.setdefault(frame_id, []).append(det) # If frame_id doesn’t exist, create it with an empty list, else frame_detections[frame_id].append(det)

# Helper: Compute IoU
# Problem: BYTETrack doesn't store the class information
# Solution: Match 'track_box' from BYTETrack to a detection box from YOLO with the highest IoU overlap and grabs its cls_id.

def compute_iou(box1, box2):
    xi1, yi1 = max(box1[0], box2[0]), max(box1[1], box2[1])
    xi2, yi2 = min(box1[2], box2[2]), min(box1[3], box2[3])
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0

# Tracking loop
output_lines = []

for frame_id in range(len(image_files)):
    img_path = os.path.join(image_dir, image_files[frame_id])
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    dets = frame_detections.get(frame_id, [])
    if len(dets) > 0:
        dets_np = np.array([[*d[:4], d[4]] for d in dets], dtype=np.float32)
    else:
        dets_np = np.empty((0, 5), dtype=np.float32)

    tracks = tracker.update(dets_np, img_info=(h, w), img_size=(h, w)) # (original_h, original_w). (resized_h, resized_w)

    for t in tracks:
        x1, y1, x2, y2 = t.tlbr
        track_box = [x1, y1, x2, y2]
        track_id = t.track_id

        # Match track to original detection by IoU
        best_iou = 0
        best_cls_id = -1
        for det in dets:
            iou = compute_iou(track_box, det[:4]) # matching tracked box (no class info) with detection box (has class info)
            if iou > best_iou:
                best_iou = iou
                best_cls_id = int(det[5])

        # Fallback if no good match
        class_id = best_cls_id if best_iou > 0.3 else 2  # 2 = car default

        line = f"{frame_id} {track_id} {class_id} 0 0 -1 {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} 0 0 0 0"
        output_lines.append(line)

# Save output
os.makedirs(os.path.dirname(output_txt), exist_ok=True)
with open(output_txt, 'w') as f:
    f.write('\n'.join(output_lines))

print(f" Saved tracking results to: {output_txt}")
