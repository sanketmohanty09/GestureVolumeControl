import cv2 as cv
import mediapipe as mp
import time
import numpy as np
import HandTrackingModule as htm
import math
import pycaw
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

cap = cv.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
pTime=0

detector =htm.handDetector(detectionCon=0.7)
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volumeRange = volume.GetVolumeRange()
#volume.SetMasterVolumeLevel(-20.0, None)
minVol = volumeRange[0]
maxVol = volumeRange[1]
vol = 0
volBar = 400
volPec = 0

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) !=0:
        #print(lmList[4],lmList[8])
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy= (x1+x2)//2, (y1+y2)//2
        cv.circle(img, (x1, y1), 10, (255, 0, 0), cv.FILLED)
        cv.circle(img, (x2, y2), 10, (255, 0, 0), cv.FILLED)
        cv.circle(img, (cx, cy), 10, (255, 0, 255), cv.FILLED)
        cv.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        length = math.hypot(x2-x1, y2-y1)
        #print(length)
        # Hand Range 50-300
        # Volume Range 0-(-96)
        vol = np.interp(length, [50,250], [minVol,maxVol])
        volBar = np.interp(length, [50, 250], [400, 150])
        volPec = np.interp(length, [50, 250], [0,100])
        print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)
        cv.putText(img, f'{int(volPec)}%', (40, 450), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)


        if length < 50:
            cv.circle(img,(cx,cy),10,(0,255,0),cv.FILLED)

    cv.rectangle(img,(50,150),(85,400),(0,255,0),3)
    cv.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv.FILLED)




    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime
    cv.putText(img, f'FPS:{str(int(fps))}', (10, 70), cv.FONT_HERSHEY_COMPLEX, 3, (255, 0, 0), 3)

    cv.imshow("IMG", img)

    cv.waitKey(1)
