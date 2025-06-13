import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from ultralytics import YOLO                                                                             # Ultralytics YOLOv8 model wrapper
from shapely.geometry import box
from types import SimpleNamespace                                                                         # Helper to pass parameters to BYTETracker
from yolox.tracker.byte_tracker import BYTETracker      
#from byte_tracker import BYTETracker

np.float = float
CLASS_PEDESTRIAN = 0
CLASS_CAR = 2

class TrackerNode(Node):
    def __init__(self):
        super().__init__('tracker_node')

        self.subscription = self.create_subscription(Image, '/camera/image_raw', self.listener_callback, 10) # Subscription 
        self.bridge = CvBridge()

        # Publish result
        self.pub_image = self.create_publisher(Image, '/tracker/output_image', 10)                          # Publisher

        # Load YOLOv8 model (trained on COCO)
        self.model = YOLO("yolov8s.pt")
        self.conf_thresh = 0.3

        # Mapping COCO classes to the target classes
        self.wanted_classes = {'person': 0, 'bicycle': 1, 'car': 2}
        self.id_to_name = {v: k for k, v in self.wanted_classes.items()}

        # Initialize BYTETracker with parameters
        self.tracker = BYTETracker(SimpleNamespace(
            track_thresh=0.5,
            track_buffer=30,
            match_thresh=0.8,
            mot20=False,
            min_box_area=100
        ), frame_rate=10)

        self.image_shape = None                                                                               # Will be updated on each frame

    def compute_iou(self, box1, box2):
        # box1 and box2 are (x1, y1, x2, y2)
        b1 = box(*box1)
        b2 = box(*box2)
        if b1.area == 0 or b2.area == 0:
            return 0.0
        return b1.intersection(b2).area / b1.union(b2).area

    def listener_callback(self, msg):
        # Convert ROS Image to OpenCV image
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.image_shape = frame.shape[:2]  # (height, width)

        # Run YOLO inference
        results = self.model.predict(source=frame, conf=self.conf_thresh, verbose=False)[0]

        # Collect detections by class
        person_dets = []
        bicycle_boxes = []
        car_dets = []

        for det in results.boxes.data:
            x1, y1, x2, y2, conf, cls = det.tolist()
            cls = int(cls)
            if cls == self.wanted_classes['person']:
                person_dets.append((x1, y1, x2, y2, conf))
            elif cls == self.wanted_classes['bicycle']:
                bicycle_boxes.append((x1, y1, x2, y2))                                                              # No conf considered because KITTI does not have bicycle (check IoU between person & bicycle boxes)
            elif cls == self.wanted_classes['car']:
                car_dets.append((x1, y1, x2, y2, conf))

        # Filter out cyclists: if person overlaps bicycle above threshold, consider cyclist (discard as person)
        pedestrian_dets = []
        for px1, py1, px2, py2, pconf in person_dets:
            is_cyclist = any(self.compute_iou((px1, py1, px2, py2), b) > 0.9 for b in bicycle_boxes)
            if not is_cyclist:
                pedestrian_dets.append((px1, py1, px2, py2, pconf))

        # Prepare filtered detections for BYTETracker input
        filtered_detections = []
        # Add filtered pedestrians (class 0 for pedestrian)
        for det in pedestrian_dets:
            filtered_detections.append([*det[:4], det[4], CLASS_PEDESTRIAN])
        # Add cars (class 2 for car)
        for det in car_dets:
            filtered_detections.append([*det[:4], det[4], CLASS_CAR])

        dets_np = np.array([d[:5] for d in filtered_detections], dtype=np.float32) if filtered_detections else np.empty((0,5), dtype=np.float32)

        img_h, img_w = self.image_shape
        # BYTETracker expects (width, height)
        tracks = self.tracker.update(dets_np, img_info=(img_w, img_h), img_size=(img_w, img_h))

        tracked_results = []
        for t in tracks:
            track_box = [*t.tlbr]  # [x1, y1, x2, y2]
            best_iou = 0.0
            best_class = -1
            for det in filtered_detections:
                iou = self.compute_iou(track_box, det[:4])
                if iou > best_iou:                                                                                  # find the det box that has the max iou with the tracker box
                    best_iou = iou
                    best_class = int(det[5])                                                                        # standard greedy assignment
            # If no good match, fallback class is car (2)
            class_id = best_class if best_iou > 0.3 else 2
            tracked_results.append({
                'track_id': t.track_id,
                'class_id': class_id,
                'bbox': track_box
            })

        # Visualization
        vis_frame = frame.copy()
        for tr in tracked_results:
            x1, y1, x2, y2 = map(int, tr['bbox'])
            class_id = tr['class_id']
            track_id = tr['track_id']
            color = (0, 255, 0) if class_id == 2 else (255, 0, 0)                                                  # green for car, blue for pedestrian
            label = f"{self.id_to_name.get(class_id, 'unknown')} ID:{track_id}"
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, 2)
            label_y = max(y1 - 10, 10)
            cv2.putText(vis_frame, label, (x1, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        #cv2.imshow("YOLOv8 + BYTETrack", vis_frame)
        #cv2.waitKey(1)
        # Convert and publish as ROS Image
        out_msg = self.bridge.cv2_to_imgmsg(vis_frame, encoding='bgr8')
        self.pub_image.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
