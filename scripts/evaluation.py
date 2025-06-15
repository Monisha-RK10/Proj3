# Step 3: Evaluate tracker
# Kitti ground truth has many classes such as 'Dont Care', 'Van', 'Cyclist'. 
# For this project, only 'Car' and 'Pedestrian' are filtered.
# BYTETrack file has class IDs 0 and 2 which correspond to person and car as per COCO-ID

# This piece of code does the following:
# Get the filtered GT and pred.
# Separate track ID and boxes for both GT and pred.
# Computes pairwise IoU distance matrix between GT and pred boxes.
# Update accumulator using this distance for track IDs of GT and pred boxes.
# Print the metrics.

import motmetrics as mm
import os
import numpy as np

# Patch for NumPy 2.0+
if not hasattr(np, 'asfarray'):
    np.asfarray = lambda a: np.asarray(a, dtype=np.float64)

ALLOWED_CLASSES = ["Car", "Pedestrian"]                                                                 # For KITTI ground truth file
ALLOWED_CLASS_IDS = [0, 2]                                                                              # For BYTETrack output file, 0 = person (Pedestrian), 2 = car 

def read_kitti_gt_file(file_path, allowed_classes):
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split()
            frame_id = int(fields[0])
            track_id = int(fields[1])
            obj_type = fields[2]
            if obj_type not in allowed_classes:
                continue
            bbox = list(map(float, fields[6:10]))                                                       # [x1, y1, x2, y2]
            if frame_id not in data:
                data[frame_id] = []
            data[frame_id].append([track_id] + bbox)                                                    # { frame_id: [ [track_id, x1, y1, x2, y2], ... ] } 
    return data

def read_tracker_file(file_path, allowed_classes_id):                                                   
    data = {}
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split(',')
            if len(fields) < 7:
                fields = line.strip().split()                                                           # support space-separated
            frame_id = int(fields[0])
            track_id = int(fields[1])
            class_id = int(fields[2])
            
            if class_id not in allowed_classes_id:
                continue                                                                                # discard bicycles or misclassed detections
                
            bbox = list(map(float, fields[6:10]))                                                       # [x1, y1, x2, y2]
            if frame_id not in data:
                data[frame_id] = []
            data[frame_id].append([track_id] + bbox)                                                    # { frame_id: [ [track_id, x1, y1, x2, y2], ... ] }  

    return data

def evaluate_mot(gt_data, pred_data):
    acc = mm.MOTAccumulator(auto_id=True)                                                               # Automatically assign internal IDs to detections that aren't explicitly matched, tracks matches frame-by-frame
    for frame_id in sorted(gt_data.keys()):
        gt_objs = gt_data.get(frame_id, [])                                                             # GT for this frame
        pred_objs = pred_data.get(frame_id, [])                                                         # Tracker output

        gt_ids = [obj[0] for obj in gt_objs]
        gt_boxes = [obj[1:] for obj in gt_objs]

        pred_ids = [obj[0] for obj in pred_objs]
        pred_boxes = [obj[1:] for obj in pred_objs]

        # Compute pairwise IoU distance matrix (inverted IoU = 1 - IoU), the better the overlap (higher IoU), the lower the distance
        distances = mm.distances.iou_matrix(gt_boxes, pred_boxes, max_iou=0.5)

        # Update accumulator with this frame's GT <-> prediction matches
        # Does matching for that frame using the Hungarian algorithm, then stores those matches to accumulate metrics over all frames.
        acc.update(gt_ids, pred_ids, distances)                                                         # distance[i][j] = 1 - IoU between GT i and Pred j

    mh = mm.metrics.create()
    summary = mh.compute(acc, metrics=mm.metrics.motchallenge_metrics, name='summary')
    print(mm.io.render_summary(summary, formatters=mh.formatters, namemap=mm.io.motchallenge_metric_names))

# Paths
gt_file = '/content/drive/MyDrive/kitti_tracking/data_tracking_label_2/training/label_02/0000.txt'
pred_file = '/content/drive/MyDrive/kitti_tracking/tracks_bytetrack/0000.txt'

gt_data = read_kitti_gt_file(gt_file, allowed_classes=ALLOWED_CLASSES)
pred_data = read_tracker_file(pred_file, allowed_classes_id=ALLOWED_CLASS_IDS)

evaluate_mot(gt_data, pred_data)
