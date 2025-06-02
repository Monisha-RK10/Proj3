Phase 1: Core MOT 
Input: Left camera images
YOLOv8 → BYTETrack → KITTI format
Visualize & evaluate with KITTI

Phase 2: Add Stereo Vision
Use KITTI right images and camera calibration
Run a stereo depth model like AANet or PSMNet
Compute disparity maps → convert to depth maps
Use calibration to compute 3D coordinates → pointcloud (optional)
