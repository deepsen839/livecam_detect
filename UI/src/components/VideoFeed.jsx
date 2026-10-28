import { useEffect, useRef } from "react";

function VideoFeed() {
    const videoRef = useRef(null);
    const socketRef = useRef(null);
const API = import.meta.env.DEV
    ? "http://localhost:8000"
    : "";    useEffect(() => {

        let interval;

        async function startCamera() {

            const stream =
                await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: 640,
                        height: 480,
                    },
                });

            const video = videoRef.current;

            video.srcObject = stream;

            try {
                await video.play();
            } catch (err) {
                if (err.name !== "AbortError") {
                    console.error(err);
                }
            }

            // -------------------------
            // WebSocket
            // -------------------------

            // const API = import.meta.env.VITE_API_URL;

            // const wsUrl = API
            //     .replace("http://", "ws://")
            //     .replace("https://", "wss://");

            // socketRef.current = new WebSocket(`${wsUrl}/camera`);
            const wsUrl = import.meta.env.DEV
                ? "ws://localhost:8000"
                : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}`;

        socketRef.current = new WebSocket(`${wsUrl}/camera`);
                    socketRef.current.onopen = () => {

                console.log("Camera websocket connected");

                const canvas =
                    document.createElement("canvas");

                const ctx =
                    canvas.getContext("2d");

                interval = setInterval(() => {

                    if (!videoRef.current) return;

                    canvas.width =
                        videoRef.current.videoWidth;

                    canvas.height =
                        videoRef.current.videoHeight;

                    ctx.drawImage(
                        videoRef.current,
                        0,
                        0
                    );

                    canvas.toBlob(blob => {

                        if (!blob) return;

                        const reader =
                            new FileReader();

                        reader.onloadend = () => {

                            const base64 =
                                reader.result.split(",")[1];

                            if (
                                socketRef.current.readyState ===
                                WebSocket.OPEN
                            ) {
                                socketRef.current.send(
                                    base64
                                );
                            }

                        };

                        reader.readAsDataURL(blob);

                    }, "image/jpeg", 0.8);

                }, 100);

            };

        }

        startCamera();

        return () => {
                clearInterval(interval);

                if (socketRef.current)
                    socketRef.current.close();

                const stream = videoRef.current?.srcObject;

                if (stream) {
                    stream.getTracks().forEach(track => track.stop());
                }
            };

    }, []);

    return (

        <div
            style={{
                display: "flex",
                gap: "20px",
            }}
        >

            {/* Hidden webcam */}

            <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                style={{
                    display: "none",
                }}
            />

            {/* Processed video */}

           <img src={`${API}/video`} />


        </div>

    );
}

export default VideoFeed;