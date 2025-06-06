# Step 1: Detection using YOLOv8
# This code does the following:
# Perform detections on specific classes (Class ID as per COCO on which YOLO was trained)
# Write those dteections in a format acceptable by BYTETrack (not COCO or KITTI) i.e., # frame_id, -1, x1, y1, x2, y2, conf, cls where -1: placeholder for tracking ID.

from ultralytics import YOLO
import os
from PIL import Image
import cv2

# Load YOLOv8 model
model = YOLO("yolov8s.pt")

input_folder = "/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000"
output_det_file = "/content/0000.txt"
wanted_classes = {'car': 2, 'person': 0, 'bicycle': 1}  # COCO class IDs used by YOLOv8.

# Invert dictionary for name mapping
id_to_name = {v: k for k, v in wanted_classes.items()}

results_lines = []
frame_id = 0
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".png"):
        frame_path = os.path.join(input_folder, filename)
        frame = Image.open(frame_path)

        detections = model.predict(source=frame, conf=0.3, verbose=False)[0]

        for det in detections.boxes.data:
            x1, y1, x2, y2, conf, cls = det.tolist()
            cls = int(cls)
            if cls in id_to_name: # Filter for Specific Classes
                # Example: 0,-1,1109.93,174.78,1200.78,315.24,0.85,0
                results_lines.append(f"{frame_id},{-1},{x1:.2f},{y1:.2f},{x2:.2f},{y2:.2f},{conf:.2f},{cls}\n")
        frame_id += 1

# Save in BYTETrack format
with open(output_det_file, "w") as f:
    f.writelines(results_lines)
