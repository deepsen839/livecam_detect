# Smart Intrusion Detection — Streamlit edition

A Streamlit-ready interface for the Smart Intrusion Detection project. It accepts a video upload, lets you configure a restricted rectangular zone, detects people with YOLO, produces an annotated MP4, and exports an intrusion event CSV.

## Run locally

Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run streamlit_app.py
```

On first run, Ultralytics downloads `yolov8n.pt` if it is not already available. Keep internet access enabled for that first run. CPU inference is used, so processing speed depends on your machine and video resolution.

## Deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository (do not commit `.env`, API keys, or secrets).
2. In Streamlit Community Cloud, choose **Create app** and select the repository/branch.
3. Set **Main file path** to `streamlit_app.py`.
4. Deploy. The dependencies are in the root `requirements.txt`.

Use a short video first; cloud CPU and memory limits can make long/high-resolution videos slow. The app processes uploaded videos rather than accessing a server-side webcam. Browser-camera/live streaming from the original FastAPI + React app is a separate workflow.

## Notes

- The restricted zone is a rectangle defined as percentages of the uploaded video's dimensions.
- Alerts are rate-limited using the configured cooldown; the event log records alert timestamps within the processed clip.
- Video processing runs on CPU.
- The existing FastAPI/React source is retained in this bundle, but the Streamlit app is standalone and does not require the backend or PostgreSQL.
- Validate detections and zone placement before using this for real security decisions.

## Live webcam mode

The app opens in **Live webcam** mode. Click **START** in the camera panel and allow browser camera permission. Select **Upload video** in the sidebar to use the original offline video workflow.

Live webcam uses `streamlit-webrtc`; camera access generally requires `localhost` or HTTPS. For a remote deployment, use HTTPS and ensure WebRTC traffic is permitted by the hosting/network environment. YOLO inference runs on CPU by default and may be slower on low-resource hosts.
