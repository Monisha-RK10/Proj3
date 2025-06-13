# Step 4: Visualization (video or plots)
# This piece of code does the following:
# For each video frame, draw the GT and predicted bounding boxes with different colors and labels.
# Save these frames into an output video file.
# Convert the video to a GIF for easy preview.

import os
import cv2
from collections import defaultdict                                                                   # Automatically initializes an empty list for new keys (similar to setDefault xyz.setdefault(abc, []).append(d)).
from moviepy.editor import VideoFileClip                                                              # Converts the output video into a GIF

# Config
image_dir = '/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000'
gt_file = '/content/drive/MyDrive/kitti_tracking/data_tracking_label_2/training/label_02/0000.txt'
pred_file = '/content/drive/MyDrive/kitti_tracking/tracks_bytetrack/0000.txt'
output_video_path = '/content/kitti_tracking_output.mp4'

# Class ID to Name Mapping (YOLO format)
class_id_to_name = {0: "Pedestrian", 2: "Car"}
allowed_classes = list(class_id_to_name.values())

# Load GT boxes
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
            bbox = list(map(float, fields[6:10]))                                                     # [left, top, right, bottom]
            data[frame].append((track_id, label, bbox))                                               # Dictionary keyed by frame number             
    return data

# Load predictions (YOLO + BYTETrack format)
def load_predictions(file_path):
    data = defaultdict(list)
    with open(file_path, 'r') as f:
        for line in f:
            fields = line.strip().split()
            frame = int(fields[0])
            track_id = int(fields[1])
            cls_id = int(fields[2])
            x1, y1, x2, y2 = map(float, fields[6:10])                                               # KITTI uses [x1, y1, x2, y2]
            conf = float(fields[5]) if len(fields) > 5 else 1.0                                     # fallback if no score
            label = class_id_to_name.get(cls_id, "Unknown")                                         # Store label & unknown (default)
            data[frame].append((track_id, label, (x1, y1, x2, y2), conf))
    return data

# Colors for GT & predictions
CLASS_COLORS = {
    "Car": (0, 255, 255),                                                                           # Yellow for GT Car
    "Pedestrian": (0, 0, 255),                                                                      # Red for GT Pedestrian
    "Pred_Car": (0, 255, 0),                                                                        # Green for predicted Car
    "Pred_Pedestrian": (255, 0, 0),                                                                 # Blue for predicted Pedestrian
    "Unknown": (100, 100, 100)                                                                      # Grey for fallback
}

# Video generation
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
        cv2.putText(img, f"GT: {label} ID: {track_id}", (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Draw predicted boxes
    for track_id, label, box, conf in pred_boxes.get(frame_idx, []):
        x1, y1, x2, y2 = map(int, box)
        color = CLASS_COLORS.get(f"Pred_{label}", CLASS_COLORS["Unknown"])                          # If label, then color of that label else unknown class' color i.e., grey
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(img, f"Pred: {label} ID: {track_id}", (int(x1), int(y2) + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    out.write(img)

out.release()
print(f" Video saved to: {output_video_path}")

# Convert the MP4 video to GIF
mp4_path = "/content/kitti_tracking_output.mp4"
gif_path = "/content/kitti_tracking_output.gif"

clip = VideoFileClip(mp4_path)
clip.subclip(0, 10).resize(0.5).write_gif(gif_path, fps=10)                                         # Resize to avoid large GIFs

print(f"GIF saved to: {gif_path}")
