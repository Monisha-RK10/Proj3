import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os
import time

class KittiPublisher(Node):
    def __init__(self):
        super().__init__('kitti_publisher')
        self.publisher_ = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()

        # Update this path based on your sequence
        self.img_dir = '/home/monisha/ros2_ws/src/mot_tracker/kitti_tracking/data_tracking_image_2/training/image_02/0000'
        self.img_files = sorted(os.listdir(self.img_dir))
        self.index = 0
        self.timer = self.create_timer(0.1, self.publish_frame)  # 10 FPS

    def publish_frame(self):
        if self.index >= len(self.img_files):
            self.get_logger().info("All KITTI images published.Restarting sequence.")
            self.index = 0  # Restart from beginning
           # rclpy.shutdown()
           # return

        img_path = os.path.join(self.img_dir, self.img_files[self.index])
        frame = cv2.imread(img_path)

        if frame is None:
            self.get_logger().warn(f"Could not read: {img_path}")
            return

        # Converts to ROS Image message with timestamp
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')
        msg.header.stamp = self.get_clock().now().to_msg()
        self.publisher_.publish(msg)
        self.get_logger().info(f"Published frame {self.index}: {self.img_files[self.index]}")
        self.index += 1

def main(args=None):
    rclpy.init(args=args)   # Initializes the ROS 2 Python client library (rclpy), create nodes, publishers, etc.
    node = KittiPublisher() # Instantiates the node class
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
