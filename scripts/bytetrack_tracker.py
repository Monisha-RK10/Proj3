# Step 2: Run tracker on all the detection from YOLOv8
# This function does the following:
# Updates tracker for detection done by YOLOv8 for specific classes 
# YOLO gives detections, BYTETrack uses detections + history to match or create tracks.
# Computes best IoU between track box & all detections to assign class.
# If best IoU > 0.3, consider that detection's class ID, else fallback.
# Writes results in KITTI format for evaluation.

# Helper: Compute IoU
# Problem: BYTETrack doesn't store the class information
# Solution: Match 'track_box' from BYTETrack to a detection box from YOLO with the highest IoU overlap 
# and grab its cls_id if IoU> 0.3.

# Note: 
# 1) Low-confidence secondary queue logic can be added for further stability, especially in occlusion scenarios
# 2) Fallback is considered ('car') for class assignment when IoU for best match < 0.3.
# A class-aware tracker or fused re-ID may improve the fallback scenario. 
# Reason: In KITTI, most false unmatched tracks are likely cars. 
# It is a design tradeoff to avoid losing potentially valuable tracklets, though it may impact evaluation.

import os
import cv2
import numpy as np
from types import SimpleNamespace
from yolox.tracker.byte_tracker import BYTETracker

# Config (Object-style config)
args = SimpleNamespace(                                                         # Quick way to create an object with attributes instead of a dictionary
    track_thresh=0.5,                                                           # Detection confidence threshold. Higher = fewer detections, but more reliable
    track_buffer=30,                                                            # How long to keep a lost track, helps in occlusion recovery (if a car is hidden briefly)
    match_thresh=0.8,                                                           # IOU threshold for associating new detections with existing tracks. Higher = stricter match, may lose fast-moving objects
    mot20=False,                                                                # Use MOT20-specific thresholds
    min_box_area=100                                                            # Filter very small boxes
)
image_dir = "/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000"
det_file = "/content/0000.txt"
output_txt = "/content/drive/MyDrive/kitti_tracking/tracks_bytetrack/0000.txt"

# Setup
tracker = BYTETracker(args, frame_rate=30)
image_files = sorted(os.listdir(image_dir))

# Load detections
frame_detections = dict()                                                       # Grouping detections by frame_id
with open(det_file, "r") as f:
    for line in f:
        parts = line.strip().split(',')
        frame_id = int(parts[0])
        x1, y1, x2, y2 = map(float, parts[2:6])
        conf = float(parts[6])
        cls_id = int(parts[7])
        if cls_id in [0, 2]:                                                    # 2-class filtering happens again for person & car (COCO IDs)  
            det = [x1, y1, x2, y2, conf, cls_id]
            frame_detections.setdefault(frame_id, []).append(det)               # If frame_id doesn’t exist, create it with an empty list. Else frame_detections[frame_id].append(det)
  
            # Example: frame_detections
            # { 0: [ [100.0, 150.0, 200.0, 300.0, 0.90, 2] # car,  [50.0, 100.0, 80.0, 180.0, 0.85, 0] # person]}

# Compute IoU between track box and det box
def compute_iou(box1, box2):
    # x1 y1 x2 y2 i.e., 0, 1, 2, 3. max for x1, y1 and min for x2, y2 between box1 and box2
    xi1, yi1 = max(box1[0], box2[0]), max(box1[1], box2[1])                     # Top-left of intersection (max)
    xi2, yi2 = min(box1[2], box2[2]), min(box1[3], box2[3])                     # Bottom-right of intersection (min)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)                          # Width × height

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])                       # x2-x1 * y2-y1
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0

# Tracking loop
output_lines = []

for frame_id in range(len(image_files)):
    img_path = os.path.join(image_dir, image_files[frame_id])
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    dets = frame_detections.get(frame_id, [])                                   # If no detecions, return empty
    if len(dets) > 0:
        dets_np = np.array([[*d[:4], d[4]] for d in dets], dtype=np.float32)    # cls_id is removed. ** is used for dictionaries. * is used for lists or tuples
    else:
        dets_np = np.empty((0, 5), dtype=np.float32)                            # cls_id is removed 

    tracks = tracker.update(dets_np, img_info=(h, w), img_size=(h, w))          # (original_h, original_w), (resized_h, resized_w)

    for t in tracks:
        x1, y1, x2, y2 = t.tlbr
        track_box = [x1, y1, x2, y2]
        track_id = t.track_id

        # Match track to original detection by IoU
        best_iou = 0
        best_cls_id = -1
        for det in dets:                                                        # dets = YOLO detections for this frame, cls_id is present
            iou = compute_iou(track_box, det[:4])                               # Matching tracked box (no class info) with detection box (has class info)
            if iou > best_iou:
                best_iou = iou
                best_cls_id = int(det[5])                                       # get class ID of best-matching YOLO box

        # Fallback if no good match
        class_id = best_cls_id if best_iou > 0.3 else 2                         # 2 = car default

        line = f"{frame_id} {track_id} {class_id} 0 0 -1 {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} 0 0 0 0"
        output_lines.append(line)

# Save output
os.makedirs(os.path.dirname(output_txt), exist_ok=True)
with open(output_txt, 'w') as f:
    f.write('\n'.join(output_lines))

print(f" Saved tracking results to: {output_txt}")
