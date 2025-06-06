# Step 4: Visualization (video or plots)

import os
import cv2
from collections import defaultdict

# === CONFIG ===
image_dir = '/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000'
gt_file = '/content/drive/MyDrive/kitti_tracking/data_tracking_label_2/training/label_02/0000.txt'
pred_file = '/content/drive/MyDrive/kitti_tracking/tracks_bytetrack/0000.txt'
output_video_path = '/content/kitti_tracking_output.mp4'
allowed_classes = ["Car", "Pedestrian", "Cyclist"]

# === LOAD GT BOXES ===
def load_kitti_labels(file_path, allowed_classes):
    data = defaultdict(list)
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split()
            frame = int(fields[0])
            track_id = int(fields[1])
            label = fields[2]
            if label not in allowed_classes:
                continue
            bbox = list(map(float, fields[6:10]))  # [left, top, right, bottom]
            data[frame].append((track_id, label, bbox))
    return data

# === LOAD TRACKER OUTPUT ===
def load_predictions(file_path):
    data = defaultdict(list)
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split()
            frame = int(fields[0])
            track_id = int(fields[1])
            cls_id = int(fields[2])  # Use this to optionally color-code per class
            bbox = list(map(float, fields[6:10]))
            data[frame].append((track_id, bbox))
    return data

# === COLORS ===
CLASS_COLORS = {
    "Car": (0, 255, 0),         # Green for GT Car
    "Pedestrian": (255, 0, 0),  # Blue for GT Pedestrian
    "Cyclist": (0, 0, 255),     # Red for GT Cyclist
    "Pred": (0, 255, 255)       # Yellow for Prediction
}

# === MAIN: DRAW AND SAVE VIDEO ===
gt_boxes = load_kitti_labels(gt_file, allowed_classes)
pred_boxes = load_predictions(pred_file)

img_files = sorted(os.listdir(image_dir))
h, w = cv2.imread(os.path.join(image_dir, img_files[0])).shape[:2]
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video_path, fourcc, 10.0, (w, h))

for frame_idx, img_name in enumerate(img_files):
    img_path = os.path.join(image_dir, img_name)
    img = cv2.imread(img_path)

    # Draw GT boxes
    for track_id, label, box in gt_boxes.get(frame_idx, []):
        x1, y1, x2, y2 = map(int, box)
        color = CLASS_COLORS[label]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"GT-{label}-{track_id}", (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # Draw prediction boxes
    for track_id, box in pred_boxes.get(frame_idx, []):
        x1, y1, x2, y2 = map(int, box)
        color = CLASS_COLORS["Pred"]
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        cv2.putText(img, f"Pred-{track_id}", (x1, y2 + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    out.write(img)

out.release()
print(f" Video saved to: {output_video_path}")

from moviepy.editor import VideoFileClip

# Convert the MP4 video to GIF
mp4_path = "/content/kitti_tracking_output.mp4"
gif_path = "/content/kitti_tracking_output.gif"

clip = VideoFileClip(mp4_path)
clip.subclip(0, 10).resize(0.5).write_gif(gif_path, fps=10)  # Resize to avoid large GIFs

print(f"GIF saved to: {gif_path}")
