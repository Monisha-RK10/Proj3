# Step 1: Inference (get all detecttions for tracker)

from ultralytics import YOLO

def run_yolov8_on_frames(frames, model_path="yolov8n.pt"):
    model = YOLO(model_path)
    all_detections = []

    for i, frame_path in enumerate(frames):
        results = model(frame_path)[0]
        detections = []
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            detections.append([x1, y1, x2, y2, conf, cls])
        all_detections.append(detections)

    return all_detections
