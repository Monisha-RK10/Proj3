# ROS2 Deployment for Real-Time Tracking

This folder contains ROS2 nodes used to deploy the real-time multi-object tracking pipeline (YOLOv8 + BYTETrack) on KITTI dataset images.

---

## Nodes

### 1. `kitti_publisher.py`
- Reads KITTI left camera images (`image_02/`)
- Publishes them as `sensor_msgs/msg/Image` on topic `/camera/image_raw`

### 2. `tracker_node.py`
- Subscribes to `/camera/image_raw`
- Runs:
  - YOLOv8 detection
  - Cyclist filtering (IoU between `person` and `bicycle`)
  - BYTETrack for tracking
  - Assigns class IDs back using IoU
  - Visualizes tracked objects with bounding boxes and IDs.
- Publishes tracked images (e.g., `/tracker/output_image`)

---

## How to Run

```bash
# Source your ROS2 workspace
source install/setup.bash

# Terminal 1 - Publish KITTI images
ros2 run mot_tracker kitti_publisher

# Terminal 2 - Run tracking node
ros2 run mot_tracker tracker_node

# Terminal 3 - Visualize in Rviz2
rviz2

