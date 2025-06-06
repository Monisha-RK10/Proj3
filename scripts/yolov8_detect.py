"""
Step 1: Object Detection using YOLOv8 for Multi-Object Tracking on KITTI

- Uses a pretrained YOLOv8s model (COCO classes) to detect 'car', 'person', and 'bicycle'.
- Reads KITTI image sequence.
- Saves detections in BYTETrack-compatible format:
  Format: frame_id, -1, x1, y1, x2, y2, confidence, class_id
"""

import os
from PIL import Image
from ultralytics import YOLO

def run_yolo_detection(input_folder: str,
                       output_det_file: str,
                       model_path: str = "yolov8s.pt",
                       confidence_threshold: float = 0.3,
                       wanted_classes: dict = {'car': 2, 'person': 0, 'bicycle': 1}):
    """
    Runs YOLOv8 on KITTI images and saves results in BYTETrack format.

    Args:
        input_folder (str): Path to KITTI image sequence folder.
        output_det_file (str): Path to output text file for BYTETrack.
        model_path (str): Path to YOLOv8 model weights.
        confidence_threshold (float): Minimum confidence threshold for detections.
        wanted_classes (dict): Mapping of class names to YOLO COCO class IDs.
    """
    model = YOLO(model_path)

    # Invert dictionary for name mapping
    id_to_name = {v: k for k, v in wanted_classes.items()}

    results_lines = []
    frame_id = 0

    image_files = sorted([f for f in os.listdir(input_folder) if f.endswith(".png")])

    for filename in image_files:
        frame_path = os.path.join(input_folder, filename)
        frame = Image.open(frame_path)

        detections = model.predict(source=frame, conf=confidence_threshold, verbose=False)[0]

        for det in detections.boxes.data:             # To iterate easily over individual detection rows (torch.Tensor of shape (N, 6))
            x1, y1, x2, y2, conf, cls = det.tolist()  # Converts from PyTorch tensor to Python list (for writing to a file)
            cls = int(cls)
            if cls in id_to_name:
                results_lines.append(f"{frame_id},-1,{x1:.2f},{y1:.2f},{x2:.2f},{y2:.2f},{conf:.2f},{cls}\n")  # track_id: initially set to -1 (meaning “no tracking ID yet”)
        frame_id += 1

    with open(output_det_file, "w") as f:
        f.writelines(results_lines)
    print(f"Detections written to {output_det_file}")

if __name__ == "__main__":
    run_yolo_detection(
        input_folder="/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000",
        output_det_file="/content/0000.txt"
    )
