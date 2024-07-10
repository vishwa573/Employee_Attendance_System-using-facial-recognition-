import cv2

cap=cv2.VideoCapture(0)

if not cap.isOpened():
    print("camera access unavailable")
else:
    while True:
        ret , frame = cap.read()
        print('ret:',ret)
        cv2.imshow("video",frame)