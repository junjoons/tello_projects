import cv2
import numpy as np
import os

from djitellopy import tello

fb_range = [6200, 6800]
pid = [0.4, 0.4, 0]
p_error = 0
width, height = 360, 240

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

while True:
    img = me.get_frame_read().frame
    print(img)
    if len(img) != 0:
        break

# me.takeoff()
# me.move_up(50)


# cap = cv2.VideoCapture(0)


def findFace(img):
    # 얼굴인식 관련 정보를 제공하는 함수
    cv2_base_dir = os.path.dirname(os.path.abspath(cv2.__file__))
    haar_model = os.path.join(cv2_base_dir, 'data/haarcascade_frontalface_default.xml')
    faceCascade = cv2.CascadeClassifier(haar_model)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(img_gray, 1.03, 4)

    my_face_list_center = []
    my_face_list_area = []
    my_face_list_basic_info = []

    for (x, y, width, height) in faces:
        cx = x + width // 2
        cy = y + height // 2
        area = width * height
        my_face_list_center.append([cx, cy])
        my_face_list_area.append(area)
        my_face_list_basic_info.append([x, y, width, height])

    if len(my_face_list_area) != 0:
        i = my_face_list_area.index(max(my_face_list_area))
        x, y, width, height = my_face_list_basic_info[i][0], my_face_list_basic_info[i][1], my_face_list_basic_info[i][
            2], my_face_list_basic_info[i][3]
        cx, cy = my_face_list_center[i][0], my_face_list_center[i][1]
        cv2.rectangle(img, (x, y), (x + width, y + height), (0, 255, 0), 4)
        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        return img, [my_face_list_center[i], my_face_list_area[i]], my_face_list_basic_info[i]
    else:
        return img, [[0, 0], 0], [0, 0, 0, 0]


def trackFace(info, width, pid, p_error):
    # info = [[얼굴 센터 x좌표, y좌표 (==가운데 원의 좌표)], 얼굴 크기(area)]
    x, y = info[0]
    area = info[1]

    # 왼쪽 오른쪽 처리부분 (yaw)
    ############################# 이해 안되는 pid부분 #############################
    error = x - width // 2
    yaw_speed = pid[0] * error + pid[1] * (error - p_error)
    yaw_speed = int(np.clip(yaw_speed, -100, 100))
    #############################################################################

    # fb_range[최소허용치, 최대허용치]
    fb_speed = 0
    status = 0

    # 거리 처리부분 (앞뒤, fb)

    fb_speed = 0
    if fb_range[0] <= area and area <= fb_range[1]:  # 만약에 감지된 얼굴 크기가 허용치 사이라면 == 적정한 거리
        fb_speed = 0
        status = 1
    elif area > fb_range[1]:  # 만약에 감지된 얼굴 크기가 최대허용치보다 크다면 == 너무 가깝다
        fb_speed -= 20
        status = 2
    elif area < fb_range[0]:  # 만약에 감지된 얼굴 크기가 최소허용치보다 작다면 == 너무 멀다
        fb_speed += 20
        status = 3

    if x == 0: yaw_speed, error, status = 0, 0, 4

    # print(fb_speed)
    # me.send_rc_control(0, fb_speed, 0, speed)
    return error, fb_speed, yaw_speed, status


while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    # _, img = cap.read()
    img = cv2.resize(img, (width, height))
    img, info, etc_info = findFace(img)
    print(etc_info)

    p_error, fb_speed, yaw_speed, status = trackFace(info, width, pid, p_error)

    if status == 1:
        drone_status = "GOOD"
    elif status == 2:
        drone_status = "TOO CLOSE"
    elif status == 3:
        drone_status = "TOO FAR"
    elif status == 4:
        drone_status = "UNDETECTED"
    print(drone_status)

    # me.send_rc_control(0, fb_speed, 0, yaw_speed)

    rec_x = etc_info[0]
    rec_y = etc_info[1]
    rec_width = etc_info[2]
    font_size = (rec_width / 200)
    rec_height = int(font_size * 30)
    rec_cx, rec_cy = rec_x + rec_width // 2, rec_y - rec_height // 2


    cv2.rectangle(img, (rec_x-2, rec_y), (rec_x + rec_width+2, rec_y - rec_height), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, drone_status, (rec_x+5, rec_y), cv2.FONT_ITALIC, font_size, (255, 255, 255), 2)
    cv2.line(img, (width // 2, 0), (width // 2, height), (0, 255, 0), 1)
    # cv2.line(img, (0, height // 2), (width, height // 2), (0, 255, 0), 1)
    cv2.line(img, (rec_cx, 0), (rec_cx, height), (255, 0, 0), 1)
    resized_img = cv2.resize(img, (720, 480))
    cv2.imshow("Output", resized_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        # me.land()
        break
