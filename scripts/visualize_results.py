# Step 4: Visualization (video or plots)

import cv2
import os
import numpy as np

# === Paths ===
image_dir = "/content/drive/MyDrive/kitti_tracking/data_tracking_image_2/training/image_02/0000"
pred_file = "/content/ByteTrack/results/0000.txt"
output_video = "output_yolo_bytetrack.mp4"

# === Load predictions ===
track_data = {}
with open(pred_file, 'r') as f:
    for line in f:
        fields = line.strip().split()
        frame_id = int(fields[0])
        track_id = int(fields[1])
        bbox = list(map(float, fields[6:10]))  # left, top, right, bottom
        if frame_id not in track_data:
            track_data[frame_id] = []
        track_data[frame_id].append((track_id, bbox))

# === Setup Video Writer ===
image_files = sorted(os.listdir(image_dir))
first_img = cv2.imread(os.path.join(image_dir, image_files[0]))
h, w, _ = first_img.shape
fps = 10
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))

def get_color(track_id):
    np.random.seed(track_id)
    return tuple(int(x) for x in np.random.randint(0, 255, 3))

# === Draw and Write Frames ===
for frame_idx, img_file in enumerate(image_files):
    img_path = os.path.join(image_dir, img_file)
    frame = cv2.imread(img_path)

    if frame_idx in track_data:
        for tid, (left, top, right, bottom) in track_data[frame_idx]:
            #color = (0, 255, 0)
            color = get_color(tid)
            cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), color, 2)
            cv2.putText(frame, f'ID: {tid}', (int(left), int(top)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    out.write(frame)

out.release()
print(f" Video saved to {output_video}")

!ffmpeg -i output_yolo_bytetrack.mp4 -vf "fps=10,scale=700:-1" -c:v gif output_yolo_bytetrack.gif
