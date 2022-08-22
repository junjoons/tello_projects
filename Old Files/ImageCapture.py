# from djitellopy import tello
from time import sleep
import cv2

# me = tello.Tello()
# me.connect()

# print(me.get_battery())

#me.takeoff()
# me.streamon()
#me.send_rc_control(0, 50, 0, 0)

def image_capture():
    # img = me.get_frame_read().frame
    # img = cv2.resize(img, (360, 240))
    # cv2.imshow("Captured Image", img)
    # cv2.waitKey(1)
    pass


if __name__ == "__main__":
    cap = cv2.VideoCapture('Moving Weird Face.mkv')
    while True:
        if cap.isOpened():
            suc, img = cap.read()
            cv2.imshow("IMG", img)
            cv2.waitKey(1)