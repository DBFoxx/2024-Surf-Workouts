import cv2
import mediapipe as mp
import math
from checkUtils import detector

stream = False
camera = cv2.VideoCapture('fs.mp4')
# camera = cv2.VideoCapture(0); stream = True
chk = detector()

while camera.isOpened():
    success, img = camera.read()
    if success:
        if stream == True:
            img = cv2.flip(img, 1)
        ov = chk.process_frame(img)
        print(ov)
        cv2.imshow('Video', img)
    else:
        break
    k=cv2.waitKey(1)
    if k == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()