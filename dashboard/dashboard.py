from fastapi import FastAPI, HTTPException
from fastapi.response import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy,ext.decalarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json

DB_PATH = os.getenv("DB_PATH", "/data/detections.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Detection(Base):
    __tablename__ = "detections"
    id = Column(Integer, primary_key=True)
    frame_name = Column(String)
    object_class = Column(String)
    confidence = Column(Float)
    bbox = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)


class BBoxModel(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class ObjectModel(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]

class DetectionPayload(BaseModel):
    frame: str
    objects: List[ObjectModel]

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/detections")
async def receieve_detections(payload: DetectionPayload):
    """ Receive detections from detector and store in SQLite"""
    session = SessionLocal()
    for obj in payload.objects:
        det = Detection(
                frame_name=payload.frame,
                object_class=obj.class_name,
                confidence=obj.confidence
                bbox=json.dumps(obj.bbox)

            )
            session.add(det)
    session.commit()
    session.close()
    return {"status", "received", "count": len(payload.objects)}

@app.get("/api/detections")
def get_detections(limit: int = 50):
    """ Retrieve latest detections for the dashboard"""
    session = SessionLocal()
    rows = session.query(Detection).order_by(Detection.timestamp.desc()).limit(limit).all()
    session.close()
    return [
        {
            "frame": r.frame_name,
            "class": r.object_class,
            "confidence", r.confidence,
            "bbox", json.loads(r.bbox),
            "time": r.timestamp.isoformat()
        }
        for r in rows
    ]

@app.get("/", response_class=HTMLResponse)
def dashboard_html():
    """Simple live dashboard that polls the API every 2 seconds"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traffic Detection Dashboard</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body {font-family: sans-serif; background: #1a1a2e; color: #eee; margin: 20px; }
            table {border-collapse: collapse; width: 100%; }
            th, td {border: 1px solid #333; padding: 8px; text-align: left; }
            th { background: #16213e; }
            tr:nth-child(even) { background: #0f3460; }
        <\style>
    </head>
    <body>
        <h1>Traffic Camera pipeline - Live Detections</h1>
        <table id="detection">
            <tr><th>Time</th><th>Frame</th><th>Object</th><th>Confidence</th></tr>
            <tr><td colspan="4">Loading...</td></tr>
        </table>
        <script>
            async function load() {
                const resp = await fetch('/api/detections?limit=30');
                const data = await resp.json();
                const table = document.getElementById('detections');
                table.innerHTML = `<tr><th>Time</th><th>Frame</th><th>Object</th><th>Confidence</th></tr>`;
                for (let row of data) {
                    let tr = table.insertRow()
                    tr.insertCell(0).innerText = new.Date(row.time).toLocaleTimeString();
                    tr.insertCell(1).innerText = row.frame;
                    tr.insertCell(2).innerText = row.class;
                    tr.insertCell(3).innserText = row.confidence.toFixed(3);
                }
            }
            setInterval(load, 2000);
            load()
        </script>
    </body>
    </html>
    """
