
from is_msgs.image_pb2 import Image
from is_wire.core import Logger, Subscription, Message, Tracer, AsyncTransport
from opencensus.trace.span import Span
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from detector import personDetector

from streamChannel import StreamChannel
from utils import get_topic_id, to_np, to_image, create_exporter, span_duration_ms

import re
import cv2



def main() -> None:
    
    broker_uri = 'amqp://'
    zipkin_host = 'zipkin'
    
    service_name = 'Person.Detector'
    re_topic = re.compile(r'CameraGateway.(\d+).Frame')
    
    person_detector = personDetector()
    
    log = Logger(name=service_name)
    channel = StreamChannel()
    log.info(f'Connected to broker {broker_uri}')
    
    exporter = create_exporter(service_name, zipkin_host, log)

    subscription = Subscription(channel=channel, name=service_name)
    subscription.subscribe('CameraGateway.*.Frame')
    
    while True:
        
        
        msg, dropped = channel.consume_last()

        tracer = Tracer(exporter=exporter, span_context=msg.extract_tracing())
        span = tracer.start_span(name='detection_and_render')
        
        detection_span = None
        
        with tracer.span(name='unpack'):
            img = msg.unpack(Image)
            im_np = to_np(img)
            
        with tracer.span(name='detection') as _span:
            camera_id = get_topic_id(msg.topic)
            detections = person_detector.detect(im_np)
            detection_span = _span
            
        with tracer.span(name='pack_and_publish_detections'):
            person_msg = Message()
            person_msg.topic = f'PersonDetector.{camera_id}.Detection'
            person_msg.inject_tracing(span)
            person_msg.pack(detections)
            channel.publish(person_msg)
        
        span.add_attribute('Detections', len(detections[0].boxes))
        tracer.end_span()
        
        info = {
            'detections': len(detections[0].boxes),
            'dropped_messages': dropped,
            'took_ms': {
                'detection': round(span_duration_ms(detection_span), 2),
                'service': round(span_duration_ms(span), 2),
            },   
        }
        log.info('{}', str(info).replace("'", '"'))        
    
        
# img = cv2.imread(img_path)

# # image = person_detector.to_np(img)

# annotations = person_detector.detect(img)

# detections = annotations[0].boxes

# print(len(detections))

if __name__ == '__main__':
    main()