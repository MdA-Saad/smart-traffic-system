import os
import glob
import time
import requests
from ultralytics import YOLO

MODEL_NAME = os.environ("MODEL", "yolo8n.pt")
CONF_THRESH = float(os.getenv("CONF_THRESH", 0.5)) 
FRAME_DIR = "/frames"
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://dashboard:8080/api/detections") 
model = YOLO(MODEL_NAME)
processed = set()


def send_detections(frame_path, detections):
    """ send detection results to dashboard API"""
    payload = {
            "frame": os.path.basename(frame_path),
            "objects": [
                {"class": cls, "confidence": float(conf), "bbox": box}
                for cls, conf, box in detections
            ]
        }
    try:
        requests.post(DASHBOARD_URL, json=payload, timeout=1)
    except Exception as e:
        print(f"Failed to send: {e}")

while True:
    all_frames = sorted(glob.glob(f"{FRAME_DIR}/frame.jpg"))
    for path in all_frames:
        if path in processed:
            continue
        
        results = model(path, conf=CONF_THRESH)
        boxes = results[0].boxes
        detections = []
        for box in boxes:
            cls = model.names[int(box.cls)]
            conf = box.conf.item()
            bbox = box.xyxy.tolist()[0]
            detections.append((cls, conf, bbox))
        print(f"Processed {path}: {len(detections)} objects")
        send_detections(path, detections)
        processed.add(path)

    if len(processed) > 1000:
        processed = set(list(processed)[-1000:])

    time.sleep(0.1)


