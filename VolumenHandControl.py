import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480
thumbTip, indexFingerTip = 4, 8
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
prevTime = 0

handDetector = htm.handDetector(detectionCon = 0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400-3
volPer = 0
showFPS = False
showFingerLine = False

while True:
    success, img = cap.read()
    img = handDetector.findHands(img, draw=False)

    lmList = handDetector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # fingers position
        thumbXPos, thumbYPos = lmList[thumbTip][1], lmList[thumbTip][2]
        indexFingerXPos, indexFingerYPos = lmList[indexFingerTip][1], lmList[indexFingerTip][2]
        if showFingerLine:
            cv2.circle(img, (thumbXPos, thumbYPos), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (indexFingerXPos, indexFingerYPos), 15, (255, 0, 255), cv2.FILLED)

        # middle position between finger
        cx, cy = (thumbXPos + indexFingerXPos) // 2, (thumbYPos + indexFingerYPos) // 2
        if showFingerLine:
            cv2.line(img, (thumbXPos, thumbYPos), (indexFingerXPos, indexFingerYPos), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)


        length = math.hypot(indexFingerXPos-thumbXPos, indexFingerYPos-thumbYPos)
        vol = np.interp(length, [50, 300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])
        volPer = np.interp(length, [50, 300], [0, 100])

        volume.SetMasterVolumeLevel(vol, None)

        if length < 50 and showFingerLine:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (53, int(volBar)+3), (85-3, 400-3), (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (30, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    if showFPS:
        currTime = time.time()
        fps = 1 / (currTime - prevTime)
        prevTime = currTime
        cv2.putText(img, f'FPS: {int(fps)}', (30,50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    cv2.waitKey(1)