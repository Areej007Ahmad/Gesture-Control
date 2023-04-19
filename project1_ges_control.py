import cv2
import time
import mediapipe as mp
import numpy as np
import Hand_tracking_module as htm
import math
# Volume Control Library
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#####################
# Camera resolution set
wCam, hCam = 640, 480
#####################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0


detector = htm.handDetector(detectionCon=0.7)

# Volume control modules taken from pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]
volBar = 0
vol = 400
volPer = 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)

    lmList = detector.findPosition(img, draw=False)
    if len(lmList) != 0:
        # print(lmList[4], lmList[8])

        x1,y1 = lmList[4][1], lmList[4][2]  # Thumb Tip
        x2,y2 = lmList[8][1], lmList[8][2]  # Finger Tip
        cx, cy = (x1+x2)//2, (y1+y2)//2  # center of finger and thumb tip

        # Drawing circle at tips of finger and thumb
        cv2.circle(img, (x1, y1), 5, (255, 255, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 5, (255, 255, 0), cv2.FILLED)

        # Drawing lone b/w thumb and fingertip
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

        # Drawing circle at center of line
        cv2.circle(img, (cx, cy), 5, (255, 255, 0), cv2.FILLED)

        # Calculating the length of line or distance b/w finger and thumb tip
        length = math.hypot(x2-x1, y2-y1)
        # print(length)

        # Hand Range 30 - 250
        # Volume range -65 to 0

        # Converting the range in more suitable form
        vol = np.interp(length, [50,300], [minVol, maxVol])
        volBar = np.interp(length, [50,300], [400, 150])
        volPer = np.interp(length, [50,300], [0, 100])
        print(vol)

        volume.SetMasterVolumeLevel(vol, None)
        # Changing color of center circle if length is less than 50
        if length < 50:
            cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)


    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 150, 50), 3)

    cv2.imshow("Img", img)
    key = cv2.waitKey(1)
    if key == 27:
        break