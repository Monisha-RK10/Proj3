import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Change this to the output folder
output_dir = '/content/drive/MyDrive/kitti_scene_understanding/output_aanet/kitti_scene_understanding-aanet_sceneflow-5aa5a24e/image_2'

# Where to save visualizations
save_vis_dir = output_dir + '_vis'
os.makedirs(save_vis_dir, exist_ok=True)

# List all images (e.g., 000000_10.png)
images = sorted([f for f in os.listdir(output_dir) if f.endswith('.png')])

for img_name in images:
    path = os.path.join(output_dir, img_name)

    # Load 16-bit disparity map
    disp = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    disp = disp.astype(np.float32)

    # Normalize for visualization
    disp_norm = cv2.normalize(disp, None, 0, 255, cv2.NORM_MINMAX)
    disp_uint8 = np.uint8(disp_norm)

    # Apply color map
    disp_color = cv2.applyColorMap(disp_uint8, cv2.COLORMAP_JET)

    # Save visualized image
    save_path = os.path.join(save_vis_dir, img_name)
    cv2.imwrite(save_path, disp_color)

    print(f"Saved: {save_path}")
