import os
import cv2
import time
from collections import deque
from datetime import datetime
from threading import Lock


class VideoRecorder:
    """
    Keeps a rolling frame buffer and saves
    intrusion clips to disk.
    """

    def __init__(
        self,
        output_dir="clips",
        fps=20,
        pre_seconds=5,
        post_seconds=5,
    ):
        self.output_dir = output_dir
        self.fps = fps

        self.pre_seconds = pre_seconds
        self.post_seconds = post_seconds

        os.makedirs(self.output_dir, exist_ok=True)

        # Buffer for frames before intrusion
        self.frame_buffer = deque(
            maxlen=fps * pre_seconds
        )

        self.lock = Lock()

        self.recording = False
        self.writer = None
        self.frames_remaining = 0
        self.current_path = None

    def update(self, frame):
        """
        Call this for EVERY processed frame.
        """

        with self.lock:

            self.frame_buffer.append(
                frame.copy()
            )

            if self.recording:

                # self.writer.write(frame)

                self.frames_remaining -= 1

                if self.frames_remaining <= 0:

                    # self.writer.release()

                    self.writer = None

                    self.recording = False

    def start_recording(self):
        """
        Starts recording an intrusion clip.

        Returns:
            path to saved mp4
        """

        with self.lock:

            if self.recording:
                return self.current_path

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            filename = (
                f"intrusion_{timestamp}.mp4"
            )

            self.current_path = os.path.join(
                self.output_dir,
                filename,
            )

            if len(self.frame_buffer) == 0:
                return None

            first = self.frame_buffer[0]

            height, width = first.shape[:2]

            # fourcc = cv2.VideoWriter_fourcc(
            #     *"mp4v"
            # )

            # self.writer = cv2.VideoWriter(
            #     self.current_path,
            #     fourcc,
            #     self.fps,
            #     (width, height),
            # )

            # # Write buffered frames
            # for frame in self.frame_buffer:
            #     self.writer.write(frame)

            # Continue recording for N seconds
            self.frames_remaining = (
                self.post_seconds * self.fps
            )

            self.recording = True

            return self.current_path


# Singleton instance
recorder = VideoRecorder()