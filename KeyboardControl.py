from djitellopy import tello
from time import sleep
import KeyPressModule as kp
import cv2
#import ImageCapture as ic

kp.init()
me = tello.Tello()
me.connect()
print(me.get_battery())

#me.takeoff()
me.streamon()

def image_capture():
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow("Captured Image", img)
    cv2.waitKey(1)

def getKeyboardInput():
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 75

    if kp.getKey("a"): lr = -speed
    elif kp.getKey("d"): lr = speed

    if kp.getKey("w"): fb = speed
    elif kp.getKey("s"): fb = -speed

    #if kp.getKey("SPACE"): ud = speed
    #elif kp.getKey("LSHIFT"): ud = -speed

    if kp.getKey("UP"): ud = speed
    elif kp.getKey("DOWN"): ud = -speed

    if kp.getKey("LEFT"): yv = -speed
    elif kp.getKey("RIGHT"): yv= speed

    if kp.getKey("e"): me.takeoff()
    if kp.getKey("q"): me.land()

    return [lr, fb, ud, yv]

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    image_capture()
    sleep(0.05)


