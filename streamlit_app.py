import os
import tempfile
import threading
import time
from datetime import datetime

import av
import cv2
import pandas as pd
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer

st.set_page_config(page_title="Smart Intrusion Detection", page_icon="🛡️", layout="wide")


class LiveIntrusionProcessor(VideoProcessorBase):
    """Processes browser webcam frames and stores intrusion events safely."""
    def __init__(self, model_name, confidence, zone_pct, cooldown, event_store, event_lock):
        self.model = load_model(model_name)
        self.confidence = confidence
        self.zone_pct = zone_pct
        self.cooldown = cooldown
        self.event_store = event_store
        self.event_lock = event_lock
        self.last_alert = 0.0
        self.frame_count = 0
        self.intrusion_active = False

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        height, width = image.shape[:2]
        x1p, y1p, x2p, y2p = self.zone_pct
        zx1, zy1 = int(width*x1p/100), int(height*y1p/100)
        zx2, zy2 = int(width*x2p/100), int(height*y2p/100)

        # Draw a translucent restricted area.
        overlay = image.copy()
        cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), (0, 0, 255), -1)
        image = cv2.addWeighted(overlay, 0.12, image, 0.88, 0)
        cv2.rectangle(image, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
        cv2.putText(image, "RESTRICTED ZONE", (zx1, max(22, zy1-8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)

        result = self.model.predict(image, classes=[0], conf=self.confidence,
                                    verbose=False, device="cpu", imgsz=640)[0]
        intrusion = False
        if result.boxes is not None:
            for box in result.boxes:
                bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                score = float(box.conf.item())
                overlap = bx1 < zx2 and bx2 > zx1 and by1 < zy2 and by2 > zy1
                intrusion = intrusion or overlap
                color = (0, 0, 255) if overlap else (0, 200, 0)
                label = "INTRUSION" if overlap else "Person"
                cv2.rectangle(image, (bx1, by1), (bx2, by2), color, 2)
                cv2.putText(image, f"{label} {score:.2f}", (bx1, max(20, by1-8)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                if overlap:
                    now = time.time()
                    if now - self.last_alert >= self.cooldown:
                        with self.event_lock:
                            self.event_store.append({
                                "Event": len(self.event_store) + 1,
                                "Timestamp": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
                                "Frame": self.frame_count,
                                "Confidence": round(score, 3),
                                "Severity": "High",
                                "Status": "Intrusion detected",
                            })
                        self.last_alert = now
        if intrusion:
            cv2.rectangle(image, (0, 0), (width, 40), (0, 0, 220), -1)
            cv2.putText(image, "INTRUSION DETECTED", (10, 27),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
        self.frame_count += 1
        return av.VideoFrame.from_ndarray(image, format="bgr24")

st.title("🛡️ Smart Intrusion Detection")
st.caption("Detect people entering a restricted zone in an uploaded video or live webcam feed.")

@st.cache_resource
def load_model(model_name: str):
    return YOLO(model_name)

with st.sidebar:
    st.header("Detection settings")
    mode = st.radio("Detection mode", ["Live webcam", "Upload video"], index=0)
    model_name = st.selectbox("YOLO model", ["yolov8n.pt", "yolov8s.pt"], index=0,
                              help="Nano is faster on CPU; Small may be more accurate but slower.")
    confidence = st.slider("Confidence threshold", 0.10, 0.90, 0.35, 0.05)
    st.subheader("Restricted zone (percentage of frame)")
    x1_pct = st.slider("Left", 0, 95, 20, 1)
    y1_pct = st.slider("Top", 0, 95, 20, 1)
    x2_pct = st.slider("Right", 5, 100, 75, 1)
    y2_pct = st.slider("Bottom", 5, 100, 80, 1)
    cooldown = st.slider("Alert cooldown (seconds)", 0, 30, 5, 1)
    max_frames = st.number_input("Maximum frames to process (0 = all)", min_value=0, max_value=100000, value=0, step=100)

if x2_pct <= x1_pct or y2_pct <= y1_pct:
    st.error("The restricted zone's right edge must be greater than its left edge, and bottom must be greater than top.")
    st.stop()

if mode == "Live webcam":
    st.subheader("Live webcam monitoring")
    st.info("Click START and allow camera access when your browser asks. Camera access works on localhost or an HTTPS website; it usually will not work on a plain HTTP remote IP.")
    if "live_events" not in st.session_state:
        st.session_state.live_events = []
    if "live_event_lock" not in st.session_state:
        st.session_state.live_event_lock = threading.Lock()

    rtc_ctx = webrtc_streamer(
        key="smart-intrusion-live-camera",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False},
        video_processor_factory=lambda: LiveIntrusionProcessor(
            model_name, confidence, (x1_pct, y1_pct, x2_pct, y2_pct), cooldown,
            st.session_state.live_events, st.session_state.live_event_lock
        ),
        async_processing=True,
    )
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Intrusion events", len(st.session_state.live_events))
    with col_b:
        st.metric("Camera", "Running" if rtc_ctx.state.playing else "Stopped")
    with st.expander("Live event log", expanded=True):
        with st.session_state.live_event_lock:
            event_snapshot = list(st.session_state.live_events)
        if event_snapshot:
            df_live = pd.DataFrame(event_snapshot)
            st.dataframe(df_live, use_container_width=True, hide_index=True)
            st.download_button("Download event log (CSV)", df_live.to_csv(index=False).encode("utf-8"),
                               file_name="live_intrusion_events.csv", mime="text/csv")
            if st.button("Clear event log"):
                with st.session_state.live_event_lock:
                    st.session_state.live_events.clear()
                st.rerun()
        else:
            st.caption("No intrusion events recorded yet.")
    st.warning("Keep this page open while monitoring. Browser camera permission is required. This demo runs detection on the server CPU and may have latency; test zone placement before relying on it.")
    st.stop()

video = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi", "mkv"])
if not video:
    st.info("Upload an MP4/MOV/AVI/MKV video to begin. For best performance, start with a short clip.")
    st.markdown("**How it works:** YOLO detects people (class 0), and an alert is recorded when a person's bounding box overlaps the restricted zone.")
    st.stop()

if st.button("Run intrusion detection", type="primary"):
    temp_input = None
    temp_output = None
    try:
        suffix = os.path.splitext(video.name)[1] or ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(video.getvalue())
            temp_input = f.name

        cap = cv2.VideoCapture(temp_input)
        if not cap.isOpened():
            st.error("Could not open this video. Try converting it to MP4 (H.264) and upload again.")
            st.stop()

        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps <= 0 or fps > 120:
            fps = 20.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if width <= 0 or height <= 0:
            cap.release()
            st.error("Could not read the video's dimensions.")
            st.stop()

        zone = (int(width*x1_pct/100), int(height*y1_pct/100),
                int(width*x2_pct/100), int(height*y2_pct/100))
        out_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_output = out_file.name
        out_file.close()
        writer = cv2.VideoWriter(temp_output, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
        if not writer.isOpened():
            cap.release()
            st.error("Could not create the annotated video.")
            st.stop()

        model = load_model(model_name)
        events = []
        seen_last_alert = {}
        frame_count = 0
        limit = int(max_frames) if max_frames else None
        progress = st.progress(0)
        status = st.empty()
        preview = st.empty()

        while True:
            ok, frame = cap.read()
            if not ok or (limit is not None and frame_count >= limit):
                break

            zx1, zy1, zx2, zy2 = zone
            overlay = frame.copy()
            cv2.rectangle(overlay, (zx1, zy1), (zx2, zy2), (0, 0, 255), -1)
            frame = cv2.addWeighted(overlay, 0.16, frame, 0.84, 0)
            cv2.rectangle(frame, (zx1, zy1), (zx2, zy2), (0, 0, 255), 2)
            cv2.putText(frame, "RESTRICTED ZONE", (zx1, max(25, zy1-8)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)

            result = model.predict(frame, classes=[0], conf=confidence, verbose=False, device="cpu")[0]
            frame_intrusion = False
            if result.boxes is not None:
                for box in result.boxes:
                    bx1, by1, bx2, by2 = map(int, box.xyxy[0].tolist())
                    conf = float(box.conf.item())
                    overlap = bx1 < zx2 and bx2 > zx1 and by1 < zy2 and by2 > zy1
                    color = (0, 0, 255) if overlap else (0, 200, 0)
                    label = "INTRUSION" if overlap else "Person"
                    cv2.rectangle(frame, (bx1, by1), (bx2, by2), color, 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (bx1, max(20, by1-8)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                    if overlap:
                        frame_intrusion = True
                        last = seen_last_alert.get("person", -10**9)
                        if (frame_count / fps) - last >= cooldown:
                            ts = frame_count / fps
                            events.append({
                                "Event": len(events) + 1,
                                "Video time": f"{int(ts//60):02d}:{int(ts%60):02d}",
                                "Frame": frame_count,
                                "Confidence": round(conf, 3),
                                "Severity": "High",
                                "Status": "Intrusion detected",
                            })
                            seen_last_alert["person"] = ts

            if frame_intrusion:
                cv2.rectangle(frame, (0, 0), (width, 42), (0, 0, 220), -1)
                cv2.putText(frame, "INTRUSION DETECTED", (12, 29),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            writer.write(frame)
            frame_count += 1
            if total > 0:
                progress.progress(min(frame_count / (limit or total), 1.0))
            if frame_count % max(1, int(fps*2)) == 0:
                status.write(f"Processed {frame_count:,} frames" + (f" of {total:,}" if total else ""))
                preview.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Live processing preview", use_container_width=True)

        cap.release()
        writer.release()
        progress.progress(1.0)
        status.success(f"Finished processing {frame_count:,} frames.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Frames processed", f"{frame_count:,}")
        col2.metric("Intrusion alerts", len(events))
        col3.metric("Video duration processed", f"{frame_count/fps:.1f} sec")

        if events:
            st.subheader("Intrusion events")
            df = pd.DataFrame(events)
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("Download event log (CSV)", df.to_csv(index=False).encode("utf-8"),
                               file_name="intrusion_events.csv", mime="text/csv")
        else:
            st.success("No restricted-zone intrusion was detected in the processed frames.")

        with open(temp_output, "rb") as f:
            st.download_button("Download annotated video", f.read(),
                               file_name=f"annotated_{datetime.now():%Y%m%d_%H%M%S}.mp4",
                               mime="video/mp4", type="primary")
        st.video(temp_output)
        st.warning("This is an offline video-analysis demo. Results depend on camera angle, lighting, model confidence, and zone placement; validate before operational use.")
    except Exception as exc:
        st.exception(exc)
    finally:
        for path in (temp_input,):
            if path and os.path.exists(path):
                try: os.remove(path)
                except OSError: pass
