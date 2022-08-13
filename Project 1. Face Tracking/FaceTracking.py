import time
import cv2
import numpy as np
# import os
import mediapipe as mp
from djitellopy import tello

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

fb_range = [35000, 50000]
pid = [0.4, 0.4, 0]
p_error = 0
width, height = 960, 540

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

while True:
    # cap = cv2.VideoCapture(0)
    cap = me.get_frame_read().frame
    # success, img = cap.read()
    print(cap)
    if len(cap) != 0:
        break

time.sleep(3)
# me.takeoff()
time.sleep(3)
# 여기서 비동기처리가 안돼서 에러날수 있음

# cap = cv2.VideoCapture(0)


def findFaces(img):
    with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.5) as face_detection:

        # success, img = cap.read()
        # if not success:
        #     print("Video Input not available")
        #     continue
        img.flags.writeable = False
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = face_detection.process(img)
        # img.flags.writeable = True
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        face_list = []
        max_face = []
        max_area = -1

        if results.detections:
            for detection in results.detections:
                xpos = int(width * detection.location_data.relative_bounding_box.xmin)
                ypos = int(height * detection.location_data.relative_bounding_box.ymin)
                real_width = int(width * detection.location_data.relative_bounding_box.width)
                real_height = int(height * detection.location_data.relative_bounding_box.height)
                face_list.append([xpos, ypos, real_width, real_height])
                img.flags.writeable = True
                mp_drawing.draw_detection(img, detection)

            for i in face_list:
                area = i[2] * i[3]
                if area > max_area:
                    max_area = area
                    max_face = [i[0], i[1], i[2], i[3]]
            cx = (max_face[0] + max_face[2]) // 2  # (xpos + real_width) // 2
            cy = (max_face[1] + max_face[3]) // 2  # (ypos + real_height) // 2
            area = max_face[2] * max_face[3]  # width * height

            return img, max_face

        if not results.detections:
            return img, [0, 0, 0, 0]


def trackFace(info, width, pid, p_error):
    xpos, ypos = info[0], info[1]
    area = info[2] * info[3]
    cx = (xpos + info[2]) // 2
    cy = (ypos + info[3]) // 2

    error = xpos - width // 2
    yaw_speed = pid[0] * error + pid[1] * (error - p_error)
    yaw_speed = int(np.clip(yaw_speed, -100, 100))
    print(area)
    fb_speed = 0

    if fb_range[0] <= area <= fb_range[1]:  # 적정거리
        fb_speed = 0
        status = "적정 거리"
    elif area >= fb_range[0]:  # 너무 가깝다
        fb_speed -= 20
        status = "너무 가깝다"
    elif 0 < area <= fb_range[1]:  # 너무 멀다
        fb_speed += 20
        status = "너무 멀다"
    else:  # 감지 못함
        fb_speed = 0
        yaw_speed, error = 0, 0
        status = "감지 못함"

    return error, fb_speed, yaw_speed, status


while True:
    # cap = cv2.VideoCapture(0)
    # success, img = cap.read()
    img = me.get_frame_read().frame
    # print(img)
    # if len(img) == 0:
    #     continue
    # if not cap.isOpened():
    #     continue

    # img = me.get_frame_read().frame
    img, face = findFaces(img)
    print(face)
    cv2.imshow("Face Detection", cv2.flip(img, 1))

    p_error, fb_speed, yaw_speed, status = trackFace(face, width, pid, p_error)
    print(status)
    me.send_rc_control(0, fb_speed, 0, yaw_speed)

    if cv2.waitKey(5) & 0xFF == 27:
        me.land()
        break
# cap.release()
