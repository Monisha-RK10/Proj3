# Input/

This folder contains kitti label (input to YOLOv8 & evaluation), detection file (input to BYTETrack), and tracker file (input to evaluation).

The format for each of them:

## kitti format
frame id | track id | class | trunc | occ | alpha | bbox left | top | right | bottom | ...3D info...

Example: 

0 -1 DontCare -1 -1 
-10.000000 219.310000 188.490000 245.500000 218.560000 
-1000.000000 -1000.000000 -1000.000000 -10.000000 -1.000000 
-1.000000 -1.000000


## BYTETrack format
frame_id, -1, x1, y1, x2, y2, score, class_id

Example:

0,-1, 1109.93,174.78, 1200.78,
315.24, 0.85,0

## Tracker Output from BYTETrack (Which is KITTI tracking format)
frame id | track id | class | truncated | occluded | alpha | bbox left | top | right | bottom | ...

Example:

0 477 0 0 0 
-1 1109.93 174.78 1200.78 315.24 
0 0 0 0
