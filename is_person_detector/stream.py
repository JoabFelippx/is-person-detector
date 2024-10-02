from is_msgs.image_pb2 import Image
from is_wire.core import Logger, Subscription, Message, Tracer
from opencensus.trace.span import Span

from detector import personDetector
import cv2

def main() -> None:
    service_name = 'Person.Detector'
    log = Logger(name=service_name)
    person_detector = personDetector()
    
img = cv2.imread(img_path)

# image = person_detector.to_np(img)

annotations = person_detector.detect(img)

detections = annotations[0].boxes

print(len(detections))

if __name__ == '__main__':
    main()
