import cv2
import os
import time

CAMER_ID=int(os.getenv("CAMERA_ID", 0))
FPS = float(os.getenv("FPS", 5))
FRAME_DIR = "/frames"

os.makedirs(FRAME_DIR, exits_ok=True)

cap = cv2.VideoCapture(CAMER_ID)
if not cap.isOpened():
    raise RuntimeError(f"ERROR: Cannot open camera {CAMER_ID}")

frame_counter=0
while True:
    ret, frame = cap.read()
    if ret:
        filename = f"{FRAME_DIR}/frame_{frame_counter:06d}.jpg"
        cv2.imwrite(filename, frame)
        frame_counter += 1
    else:
        print("Warning: failed to grab frame")
    time.sleep(1 / FPS)
cap.release()
