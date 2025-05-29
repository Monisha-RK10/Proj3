# AT_CHECK to TORCH_CHECK

!CUDA_VISIBLE_DEVICES=0 python /content/aanet/inference.py \
--mode test \
--data_dir /content/drive/MyDrive/kitti_scene_understanding \ #  Left and Right stereo images.
--dataset_name KITTI2015 \
--pretrained_aanet /content/drive/MyDrive/kitti_scene_understanding/aanet_sceneflow-5aa5a24e.pth \
--batch_size 1 \
--img_height 384 \
--img_width 1248 \
--feature_type ganet \ # Feature extraction: Extracts deep features from both views.
--feature_pyramid \
--refinement_type hourglass \ # Cost volume, for each disparity level, match left features with shifted right features
--no_intermediate_supervision \
--output_dir /content/drive/MyDrive/kitti_scene_understanding/output_aanet

#  Soft-argmax is applied to get final disparity.
# During training:Loss compares predicted disparity with GT (disp_noc_0.png) via L1 or smooth loss.
