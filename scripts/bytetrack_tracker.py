# Step 2: Run tracker on all the detection from YOLOv8

import os
import cv2
import numpy as np
from types import SimpleNamespace
from yolov8_detect import run_yolov8_on_frames
from yolox.tracker.byte_tracker import BYTETracker

# Fix np.float deprecation (only if needed for older ByteTrack code)
np.float = float

def run_bytetrack(image_dir, model_path="yolov8n.pt", seq_id="0000", output_dir="results/", frame_rate=30):
    # Tracker arguments using SimpleNamespace
    args = SimpleNamespace(
        track_thresh=0.5,  # detection confidence threshold
        track_buffer=30,   # how long to keep a lost track
        match_thresh=0.8,  # IOU matching threshold
        mot20=False,       # use MOT20-specific thresholds
        min_box_area=100   # filter very small boxes
    )

    # Tracker initialization
    tracker = BYTETracker(args, frame_rate=frame_rate)

    # Collect image paths
    image_files = sorted(os.listdir(image_dir))
    frames = [os.path.join(image_dir, img) for img in image_files]

    # Run YOLOv8 detection
    all_detections = run_yolov8_on_frames(frames, model_path=model_path)

    output_lines = []

    for frame_id, dets in enumerate(all_detections):
        img = cv2.imread(frames[frame_id])
        h, w = img.shape[:2]

        # Prepare detections for BYTETracker: [x1, y1, x2, y2, conf, cls]
        byte_dets = [[*d[:4], d[4]] for d in dets if d[4] > 0.3]  # confidence threshold
        byte_dets = np.array(byte_dets)

        tracks = tracker.update(byte_dets, img_info=(h, w), img_size=(h, w))

        for t in tracks:
            x1, y1, x2, y2 = t.tlbr
            track_id = t.track_id
            class_id = 1  # Hardcoded for now (e.g., car)

            # KITTI tracking format
            line = f"{frame_id} {track_id} {class_id} 0 0 -1 {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f} 0 0 0 0"
            output_lines.append(line)

    # Save results in KITTI format
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, f"{seq_id}.txt"), "w") as f:
        f.write("\n".join(output_lines))

    print(f"Tracking results saved to {output_dir}/{seq_id}.txt")

# Example run:
# run_bytetrack("/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000")
