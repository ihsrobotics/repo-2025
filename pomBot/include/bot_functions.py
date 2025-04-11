# import numpy as np
# import cv2 as cv
from time import time
from statistics import mean
from ctypes import CDLL
from config_loader import *

kipr = "/usr/lib/libkipr.so"
k = CDLL(kipr)

epoch = time()
end_time = epoch + 2

hues = []
sats = []

def setup_camera_old(port):
    cap = cv.VideoCapture(port, cv.CAP_V4L2)
    cap.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()
        return
    return cap

def setup_camera():
    k.camera_open()
    k.camera_load_config("pom_sort.conf")


# while time() < end_time: #time() < end_time
def read_color_old(cap):
    # Capture frame-by-frame
    ret, frame = cap.read()
    hsv_frame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    height, width, _ = frame.shape

    cx = int(width/2)
    cy = int(height/2)

    center = hsv_frame[cy, cx]
    hue = center[0]
    sat = center[1]
    # hues.append(hue)
    # sats.append(sat)

    if sat < 80:
        color = "BACKGROUND"
    elif hue < 22:
        color = "ORANGE"
    elif hue < 50:
        color = "YELLOW"
    elif hue < 120:
        color = "BACKGROUND"
    else:
        color = "RED"

    # print(f"{center}, {color}")
    cv.circle(frame, (cx, cy), 5, (255, 255, 255), 3)


    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        # break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv.imshow('frame', frame)
    if cv.waitKey(1) == ord('q'):
        return
    return color
    
def read_color():
    setup_camera()
    k.camera_update()

    red_area = k.get_object_area(2, 0)
    orange_area = k.get_object_area(0, 0)
    yellow_area = k.get_object_area(1, 0)
    print("red:",red_area)
    print("orange:",orange_area)
    print("yellow:",yellow_area)
    
    if red_area > orange_area and red_area > yellow_area and red_area > 100000:
        print("red:",red_area)
        return "RED"
    elif orange_area > red_area and orange_area > yellow_area and orange_area > 100000:
        print("orange:",orange_area)
        return "ORANGE"
    elif yellow_area > red_area and yellow_area > orange_area and yellow_area > 100000:
        print("yellow:",yellow_area)
        return "YELLOW"
    else:
        return "BACKGROUND"
    close_camera()
    k.msleep(100)


# When everything done, release the capture
def close_camera_old(cap):
    cap.release()
    cv.destroyAllWindows()

def close_camera():
    k.camera_close()

# hue = mean(hues)
# sat = mean(sats)
# #Determine Color
# if sat < 80:
#     color = "BACKGROUND"
# elif hue < 22:
#     color = "ORANGE"
# elif hue < 50:
#     color = "YELLOW"
# elif hue < 120:
#     color = "BACKGROUND"
# else:
#     color = "RED"

# print(f"Average Hue: {hue}")
# print(f"Average Saturation: {sat}")
# print(color)

#Run unset GTK_PATH

pom_color = ["RED", "YELLOW", "ORANGE"]

def most_common(lst):
    return max(set(lst), key=lst.count)

def on_tape(tophat=FRONT_TOPHAT):
    return k.analog(tophat) > BLACK

def drive(left_speed, right_speed, duration = 0):
    k.mav(LEFT_WHEEL, left_speed)
    k.mav(RIGHT_WHEEL, right_speed)
    k.msleep(duration)

def brake():
    drive(0, 0)

def line_follow(slow, fast, direction=FORWARD, side="LEFT"):
    tophat = FRONT_TOPHAT
    
    if direction == BACKWARD:
        tophat = BACK_TOPHAT
    
    slow *= direction
    fast *= direction

    if side == "LEFT":
        if on_tape(tophat):
            drive(slow, fast)
        if not on_tape(tophat):
            drive(fast, slow)
            
    elif side == "RIGHT":
        if on_tape(tophat):
            drive(fast, slow)
        if not on_tape(tophat):
            drive(slow, fast)

def run_conveyor_and_wheel(speed):
    k.mav(CONVEYOR, speed)
    k.mav(WHEEL, speed)

def sweep_arm(speed=1):
    for i in range(k.get_servo_position(SWEEP_ARM), ARM_MAX, speed):
        k.set_servo_position(SWEEP_ARM, i)
        k.msleep(1)
    
    for i in range(k.get_servo_position(SWEEP_ARM), ARM_MIN, speed):
        k.set_servo_position(SWEEP_ARM, i)
        k.msleep(1)
