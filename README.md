---
title: Smart Intrusion Detection
emoji: 👁️
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Smart Intrusion Detection

AI-powered smart intrusion detection using FastAPI, React, OpenCV, and YOLO.

# Smart Intrusion Detection System

A production-ready AI-powered Smart Intrusion Detection System built with **FastAPI**, **React**, **YOLOv8**, **OpenCV**, **PostgreSQL**, **WebSockets**, and **Docker**.

The system performs real-time human detection, monitors restricted zones, triggers intrusion alerts, stores snapshots and video clips, and provides a live monitoring dashboard.

---

# Features

* Real-time video processing
* Human detection using YOLOv8
* Restricted zone monitoring
* Intrusion detection using polygon intersection
* Live MJPEG video streaming
* Automatic snapshot capture
* Automatic video clip recording
* PostgreSQL event storage
* WebSocket-based real-time notifications
* React monitoring dashboard
* Dockerized deployment

---

# Tech Stack

## Backend

* FastAPI
* OpenCV
* Ultralytics YOLOv8
* SQLAlchemy
* PostgreSQL
* WebSockets
* Shapely

## Frontend

* React
* Vite
* JavaScript
* HTML/CSS

## Deployment

* Docker
* Docker Compose

---

# Project Structure

```
smart_intrusion_detection/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── main.py
│   │   └── config.py
│   │
│   ├── snapshots/
│   ├── clips/
│   ├── uploads/
│   ├── requirements.txt
│   └── Dockerfile
│
├── UI/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

# Intrusion Detection Pipeline

```
Camera / CCTV
        │
        ▼
OpenCV Video Capture
        │
        ▼
YOLOv8 Person Detection
        │
        ▼
Restricted Zone Check
        │
        ▼
Intrusion Decision
        │
 ┌──────┼──────────────┐
 │      │              │
 ▼      ▼              ▼
Snapshot Video Clip  Database
 Save     Save       Storage
 │         │
 └──────┬──┘
        ▼
 WebSocket Notification
        │
        ▼
 React Dashboard
```

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
cd smart_intrusion_detection
```

---

# Start with Docker

```bash
docker compose up --build
```

---

# Backend

Runs on:

```
http://localhost:8000
```

Useful endpoints:

```
GET /
GET /video
GET /intrusions
WS  /ws
```

---

# Frontend

Runs on:

```
http://localhost:5173
```

---

# API Endpoints

## Health Check

```
GET /
```

Returns:

```json
{
  "status": "running"
}
```

---

## Live Video Feed

```
GET /video
```

Streams MJPEG video with annotations.

---

## Intrusion Events

```
GET /intrusions
```

Returns all stored intrusion events.

---

## WebSocket

```
ws://localhost:8000/ws
```

Example event:

```json
{
  "type": "intrusion",
  "event_id": 15,
  "camera": "Main Gate",
  "snapshot": "snapshots/intrusion_20260618_120000.jpg",
  "video": "clips/intrusion_20260618_120000.mp4",
  "timestamp": "2026-06-18T12:00:00"
}
```

---

# How Intrusion Detection Works

1. Capture a frame from the camera.
2. Detect humans using YOLOv8.
3. Compare detected person bounding boxes with the configured restricted zone.
4. If any overlap is detected:

   * Draw a red bounding box.
   * Display an "INTRUSION DETECTED" banner.
   * Save a snapshot.
   * Record a video clip.
   * Store the event in PostgreSQL.
   * Broadcast a WebSocket notification.

---

# Restricted Zone

The restricted polygon is configured in:

```
backend/app/utils/zone_utils.py
```

Modify the polygon coordinates to match your camera view.

---

# Models

Default model:

```
yolov8n.pt
```

You may replace it with larger YOLO variants depending on hardware capabilities.

---

# Generated Files

Snapshots:

```
backend/snapshots/
```

Video clips:

```
backend/clips/
```

These directories are automatically created if they do not exist.

---

# Docker

Start:

```bash
docker compose up --build
```

Stop:

```bash
docker compose down
```

---

# Future Improvements

* Multi-camera support
* RTSP stream integration
* Email notifications
* SMS alerts
* Push notifications
* Face recognition
* Weapon detection
* PPE compliance detection
* Object tracking analytics
* Grafana dashboards
* Kubernetes deployment
* Cloud storage for evidence

---

# License

This project is intended for educational and research purposes. Review applicable privacy, surveillance, and data protection regulations before deploying in production.
