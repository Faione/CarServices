#!python3

import cv2
import subprocess
#import matplotlib.pyplot as plt
import numpy as np
import time
import struct
from pynng import Pair0


# configs
dial = 'tcp://10.118.0.35:13131'
F_R = 10

def get_frame(cap):
    if cap.isOpened():
        return cap.read()
    return False, None

def get_cap_dev():
    return cv2.VideoCapture('/dev/video0')


def get_size(cap):
    #return (640, 480)
    return (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))


def main():
    import sys
    if len(sys.argv) > 1:
        dial = sys.argv[1]
    cap = get_cap_dev()
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 80)
    #cap.set(cv2.CAP_PROP_FPS, 30)
    print("cv frame size: ", cap.get(cv2.CAP_PROP_FRAME_WIDTH), "x", cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("cv fps:", cap.get(cv2.CAP_PROP_FPS))
    t1 = time.time()
    index = 0
    t0 = time.time()
    with Pair0(dial=dial) as s0:
        print("Pair0")
        while cap.isOpened(): 
            time.sleep(1/F_R)
            success, frame = get_frame(cap)
            print("success: ", success)
            if success:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                t2 = time.time()
                h, w, c = frame.shape
                h =  240
                w = 320
                new_img = cv2.resize(frame, (w, h), interpolation=cv2.INTER_CUBIC)
                dd = new_img.tobytes()
                #print("byte:", len(dd))
                #print("tt",t2)
                #print("resize t: ", time.time() - t2)
                index= t2-t0
                data = struct.pack("iiid"+str(len(dd))+"s",h,w,c,t2,dd)
                print("before sending")
                #s0.send(data)
                print("all fps:", 1.0/(time.time() - t1), " pack fps:", 1.0/(time.time()-t2))
                t1 = time.time()
                #print("send time:", t1 - t2)
    cap.release()


if __name__ == "__main__":
    main()

