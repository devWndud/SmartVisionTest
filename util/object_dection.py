from ctypes import *
import math
import random
import os
import numpy as np
import time
import cv2

# Darknet import 시도 (없으면 경고만 출력)
try:
    from darknet import darknet
    DARKNET_AVAILABLE = True
except ImportError:
    print("Warning: Darknet not found. Object detection will be disabled.")
    print("Install Darknet to enable object detection functionality.")
    DARKNET_AVAILABLE = False
    darknet = None

netMain = None
metaMain = None
altNames = None

# Darknet 초기화 (사용 가능한 경우에만)
if DARKNET_AVAILABLE:
    configPath = "./darknet/cfg/obj.cfg"
    # 가중치 파일 경로: obj_last_yolov3.weights 또는 yolov3_obj.weights 중 하나 사용
    weightPath = "./darknet/obj_last_yolov3.weights"
    if not os.path.exists(weightPath):
        weightPath = "./darknet/yolov3_obj.weights"  # 대체 경로
    metaPath = "./darknet/cfg/obj.data"
    
    if os.path.exists(configPath) and os.path.exists(weightPath) and os.path.exists(metaPath):
        try:
            if netMain is None:
                netMain = darknet.load_net_custom(configPath.encode(
                        "utf-8"), weightPath.encode("utf-8"), 0, 1)  # batch size = 1
            if metaMain is None:
                metaMain = darknet.load_meta(metaPath.encode("ascii"))
        except Exception as e:
            print(f"Warning: Failed to load Darknet model: {e}")
            DARKNET_AVAILABLE = False
    else:
        print("Warning: Darknet config/weight files not found. Object detection disabled.")
        DARKNET_AVAILABLE = False

# altNames 초기화 (Darknet 사용 가능한 경우에만)
if DARKNET_AVAILABLE and altNames is None:
    try:
        metaPath = "./darknet/cfg/obj.data"
        if os.path.exists(metaPath):
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                   re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                     if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
    except Exception:
        pass

# Create an image we reuse for each detect (Darknet 사용 가능한 경우에만)
if DARKNET_AVAILABLE and netMain is not None:
    darknet_image = darknet.make_image(darknet.network_width(netMain),
                                        darknet.network_height(netMain),3)
else:
    darknet_image = None

movable = ['bicycle', 'bus' ,'car' ,'carrier' ,'cat' ,'dog' ,'motorcycle' ,'movable_signage'  ,'person' ,'scooter' ,'stroller' ,'truck' ,'wheelchair']
fixed = ['barricade', 'bench' ,'bollard' ,'chair' ,'fire_hydrant' ,'kiosk' ,'parking_meter' ,'pole' ,'potted_plant' ,'power_controller' ,'stop' ,'table' ,'traffic_light' ,'traffic_light_controller' ,'traffic_sign' ,'tree_trunk']




def convertBack(x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def cvDrawBoxes(detections, img):
    detection_box = []
    moving_object = []
    fixed_object = []
    for detection in detections:
        color = ()
        if detection[0].decode() in movable:
            color = (100, 255 ,255)
        else:
            color = (255, 100 ,255)

        x, y, w, h = detection[2][0],\
            detection[2][1],\
            detection[2][2],\
            detection[2][3]
        xmin, ymin, xmax, ymax = convertBack(
            float(x), float(y), float(w), float(h))
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)
        
        
        cv2.rectangle(img, pt1, pt2, color, 3)
        cv2.putText(img,
                    detection[0].decode(),
                    (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    color, 2)
        xmin = int(xmin*(480/416))
        ymin = int(ymin*(270/416))
        xmax = int(xmax*(480/416))
        ymax = int(ymax*(270/416))

        if xmax >= 480:
            xmax = 479
        if ymax >= 270:
            ymax = 269
        if xmin < 0:
            xmin = 0
        if ymin < 0:
            ymin = 0
        pt1 = (xmin, ymin)
        pt2 = (xmax, ymax)

        if detection[0].decode() in movable:
            moving_object.append([pt1, pt2])
        else : 
            fixed_object.append([pt1, pt2])
    return img, moving_object, fixed_object

def YOLO(frame): 
    global metaMain, netMain, altNames
    
    # Darknet이 없으면 빈 결과 반환
    if not DARKNET_AVAILABLE or netMain is None or metaMain is None:
        moving_object = []
        fixed_object = []
        return frame.copy(), moving_object, fixed_object
    
    try:
        frame_read = frame
        frame_read= np.array(frame, np.uint8)
        frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb,
                                    (darknet.network_width(netMain),
                                        darknet.network_height(netMain)),
                                    interpolation=cv2.INTER_LINEAR)

        darknet.copy_image_from_bytes(darknet_image,frame_resized.tobytes())

        detections = darknet.detect_image(netMain, metaMain, darknet_image, thresh=0.25)
        image, moving_object, fixed_object = cvDrawBoxes(detections, frame_resized)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (480,270))
    except Exception as e:
        print(f"Warning: YOLO detection failed: {e}")
        moving_object = []
        fixed_object = []
        return frame.copy(), moving_object, fixed_object
    
    return image, moving_object, fixed_object

