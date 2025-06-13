# Step 1: Detection using YOLOv8
# This piece of code does the following:
# Performs inference on the kitti frame and give outputs where class ID correspond to YOLO/COCO format.
# Computes IoU between person & bicycle to classify either pedestrian (keep) or cyclist (discard) based on threshold.
# Saves all detection (cars, persons only) in BYTETrack format.

from ultralytics import YOLO
import os
from PIL import Image
import cv2

def compute_iou(boxA, boxB):
    # box: [x1, y1, x2, y2] consider max for 0, 1 and min for 2, 3
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)                  
    if interArea == 0:
        return 0.0

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])                                           # x2-x1 * y2-y1
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

# Load YOLOv8 model
model = YOLO("yolov8s.pt")

input_folder = "/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000"
output_det_file = "/content/filtered_0000.txt"

wanted_classes = {'person': 0, 'bicycle': 1, 'car': 2}                                             # as per COCO labels
id_to_name = {v: k for k, v in wanted_classes.items()}

results_lines = []
frame_id = 0
for filename in sorted(os.listdir(input_folder)):
    if filename.endswith(".png"):
        frame_path = os.path.join(input_folder, filename)
        frame = Image.open(frame_path)

        detections = model.predict(source=frame, conf=0.6, verbose=False)[0]

        persons = []
        bicycles = []
        cars = []

        for det in detections.boxes.data:
            x1, y1, x2, y2, conf, cls = det.tolist()
            cls = int(cls)
            if cls == 0:
                persons.append([x1, y1, x2, y2, conf])
            elif cls == 1:
                bicycles.append([x1, y1, x2, y2, conf])
            elif cls == 2:
                cars.append([x1, y1, x2, y2, conf])

        matched_person_indices = set()
        for bi in bicycles:
            for i, pi in enumerate(persons):                                                              # Example: persons = [p1, p2, p3]  # 3 persons, bicycles = [b1], If b1 overlaps with p2, then: matched_person_indices = {1}
                iou = compute_iou(bi[:4], pi[:4])
                if iou > 0.4:  # Cyclist detected
                    matched_person_indices.add(i)

        # Save unmatched persons as pedestrians
        for i, pi in enumerate(persons):
            if i not in matched_person_indices:
                x1, y1, x2, y2, conf = pi
                results_lines.append(f"{frame_id},-1,{x1:.2f},{y1:.2f},{x2:.2f},{y2:.2f},{conf:.2f},0\n")  # 0 = person, frameid, trackid, xxyy, conf

        # Save cars
        for ci in cars:
            x1, y1, x2, y2, conf = ci
            results_lines.append(f"{frame_id},-1,{x1:.2f},{y1:.2f},{x2:.2f},{y2:.2f},{conf:.2f},2\n")      # 2 = car

        frame_id += 1

# Save filtered detections
with open(output_det_file, "w") as f:
    f.writelines(results_lines)
