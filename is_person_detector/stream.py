from is_msgs.image_pb2 import Image
from is_wire.core import Logger, Subscription, Message, Tracer, AsyncTransport
from opencensus.trace.span import Span
from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
from detector import personDetector

from streamChannel import StreamChannel
from utils import get_topic_id, to_np, to_image, create_exporter, span_duration_ms

import re
import time
import socket
import json

def main() -> None:

    config = json.load(open('../etc/conf/options.json'))
    broker_uri = config['broker_uri']
    zipkin_host = config['zipkin_uri']

    service_name = 'Person.Detector'

    person_detector = personDetector()

    log = Logger(name=service_name)
    channel = StreamChannel()
    log.info(f'Connected to broker {broker_uri}')

    exporter = create_exporter(service_name, zipkin_host, log)

    subscription = Subscription(channel=channel, name=service_name)
    subscription.subscribe('CameraGateway.*.Frame')

    while True:

        msg = channel.consume_last()

        if msg.topic != "CameraGateway.5.Frame": #Camera 5 doesn't have "inject_tracing"

            timestamp_rcvd = time.time()

            msg_contrace = (
                f'{{"timestamp_send": "{int(msg.created_at*1000000)}", '
                f'"timestamp_rcvd": "{int(timestamp_rcvd*1000000)}", '
                f'"x-b3-flags": "{msg.metadata["x-b3-flags"]}", '
                f'"x-b3-parentspanid": "{msg.metadata["x-b3-parentspanid"]}", '
                f'"x-b3-sampled": "{msg.metadata["x-b3-sampled"]}", '
                f'"x-b3-spanid": "{msg.metadata["x-b3-spanid"]}", '
                f'"x-b3-traceid": "{msg.metadata["x-b3-traceid"]}", '
                f'"spanname": "frame"}}'
            )
            print(msg_contrace)
            bytesToSend = str.encode(msg_contrace)

            serverAddressPort = (config['conmtrace_host'], config['conmtrace_port'])
            bufferSize = 2048

            UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
            log.info("Enviando mensagem para Contrace")
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)
            log.info("Mensagem para Contrace: {}", msg_contrace)

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

            bounding_boxes = detections[0].boxes.xyxy
            obj_annotations = person_detector.to_object_annotations(bounding_boxes, detections[0].orig_shape) 
            channel.publish(person_msg)

        with tracer.span(name='render_pack_publish'):

            image_with_bounding = person_detector.bounding_box(im_np, obj_annotations)
            rendered_msg = Message()
            rendered_msg.topic = f'PersonDetector.{camera_id}.Rendered'
            rendered_msg.inject_tracing(span)

            rendered_msg.pack(to_image(image_with_bounding))
            rendered_msg.created_at = time.time()
            print(rendered_msg.created_at)
            channel.publish(rendered_msg)

        span.add_attribute('Detections', len(detections[0].boxes))
        tracer.end_span()

        info = {
            'detections': len(detections[0].boxes),
               'took_ms': {
                'detection': round(span_duration_ms(detection_span), 2),
                'service': round(span_duration_ms(span), 2),
            },
        }
        log.info('{}', str(info).replace("'", '"'))

if __name__ == '__main__':
    main()
