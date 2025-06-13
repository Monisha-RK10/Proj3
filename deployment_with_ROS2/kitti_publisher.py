import rclpy                                                                     # ROS 2 Python client library
from rclpy.node import Node                                                      # Base class to create nodes
from sensor_msgs.msg import Image                                                # Message type for publishing images
from cv_bridge import CvBridge                                                   # Converts between OpenCV images and ROS Image messages
import cv2                                                                       # OpenCV for image loading and manipulation
import os                                                                        # For file handling
import time                                                                      # (Optional here, for delays etc.)

class KittiPublisher(Node):                                                      # Custom ROS 2 node that inherits from Node (publishers, timers, loggers, etc)
    def __init__(self):
        super().__init__('kitti_publisher')                                      # Node initialization
        self.publisher_ = self.create_publisher(Image, '/camera/image_raw', 10)  # Queue size: how many messages can be stored if subscribers are slow.
        self.bridge = CvBridge()

        # Update this path based on your sequence
        self.img_dir = '/home/monisha/ros2_ws/src/mot_tracker/kitti_tracking/data_tracking_image_2/training/image_02/0000'
        self.img_files = sorted(os.listdir(self.img_dir))
        self.index = 0
        self.timer = self.create_timer(0.1, self.publish_frame)                  # Creates a timer to call publish_frame() every 0.1 seconds = 10 FPS

    # Image publishing logic
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
        msg = self.bridge.cv2_to_imgmsg(frame, encoding='bgr8')                  # Converts OpenCV BGR image to ROS2 
        msg.header.stamp = self.get_clock().now().to_msg()                       # Adds a timestamp to the message header
        self.publisher_.publish(msg)                                             # Publishes the image on the ROS topic
        self.get_logger().info(f"Published frame {self.index}: {self.img_files[self.index]}")
        self.index += 1

def main(args=None):
    rclpy.init(args=args)                                                         # Initializes the ROS 2 Python client library (rclpy), create nodes, publishers, etc.
    node = KittiPublisher()                                                       # Instantiates the node class
    rclpy.spin(node)                                                              # Keep node running, listen for callbacks
    node.destroy_node()                                                           # Cleanup
    rclpy.shutdown()                                                              # Shutdown ROS 2

if __name__ == '__main__':
    main()
