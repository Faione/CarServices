#!python3

import cv2
import subprocess
import numpy as np
import time
import struct
from pynng import Pair0
import sys

# opentracing lib
from lib.tracing import init_tracer
from opentracing.ext import tags
from opentracing.propagation import Format




def get_frame(cap):
    if cap.isOpened():
        return cap.read()
    return False, None

def get_cap_dev():
    return cv2.VideoCapture('/dev/video0')


def get_size(cap):
    #return (640, 480)
    return (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))

def resize_frame(frame):
    new_img = cv2.resize(frame, (FRAME_WIDTH, FRAME_HIGHT), interpolation=cv2.INTER_CUBIC)

    return new_img

def trace_resize_frame(frame):
    with tracer.start_active_span('resize_frame') as scope:
        new_img = resize_frame(frame)

    return new_img

def pack_data(raw_byte_data, color_channel, t2):
    data = struct.pack("iiid"+str(len(raw_byte_data))+"s", FRAME_HIGHT, FRAME_WIDTH, color_channel, t2, raw_byte_data)
    return data

def trace_pack_data(raw_byte_data, color_channel, t2):
    with tracer.start_active_span('pack_data') as scope:
        data = pack_data(raw_byte_data, color_channel, t2)
    return data

def send(sender, data):
    sender.send(data)

def trace_send(sender, data):
    with tracer.start_active_span('send') as scope:
        send(sender, data)

def main():
    cap = get_cap_dev()

    global index

    do_trace = False
    if index % CHECK_POINT == 0:
        do_trace = True

    print("cv frame size: ", cap.get(cv2.CAP_PROP_FRAME_WIDTH), "x", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("cv fps:", cap.get(cv2.CAP_PROP_FPS))
    t1 = time.time()
 
    t0 = time.time()
    with Pair0(dial=dial) as s0:
        while cap.isOpened(): 
            time.sleep(1 / FRAME_RATE)
            success, frame = get_frame(cap)
            if success:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                color_channel = frame.shape[2]

                # resize frame
                new_img = trace_resize_frame(frame) if do_trace else resize_frame(frame)
                
                img_bytes = new_img.tobytes()

                data = trace_pack_data(img_bytes, color_channel, t2) if do_trace else pack_data(img_bytes, color_channel, t2)
                trace_send(s0, data) if do_trace else send(s0, data)

                print("all fps:", 1.0/(time.time() - t1), " pack fps:", 1.0/(time.time()-t2))

                index = index + 1

    cap.release()


if __name__ == "__main__":
    # configs
    dial = 'tcp://10.118.0.35:13131'
    FRAME_HIGHT, FRAME_WIDTH, FRAME_RATE = 240, 320, 10
    TRACER_NAME = "camera_catcher"

    index = 0
    CHECK_POINT = 20

    # tracer
    tracer = init_tracer(TRACER_NAME)

    if len(sys.argv) > 1:
        dial = sys.argv[1]
    
    main()
    tracer.close()

