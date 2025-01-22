import cv2
import os
import time
import logging
from picamera2 import Picamera2
from sensors.BaseSensor import BaseSensor
from dataclass.FaceRecognitionConfig import FaceRecognitionConfig

logger = logging.getLogger(__name__)

class FaceRecognition(BaseSensor):
    def __init__(self,
                 service_name = "FaceRecognitionService",
                 cascade_path = "config/haarcascade_frontalface_default.xml",
                 debug_output_dir = "logs/detected_faces",
                 debug = False,
                 config: FaceRecognitionConfig = None):
        config = config or FaceRecognitionConfig()
        super().__init__(service_name = service_name, config = config, debug = debug)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.config = config
        self.debug_output_dir = debug_output_dir
        self.cascade_path = cascade_path 
        
    def setup(self):
        self.face_tracks = {}
        self.track_id = 0
        self.frame_count_to_forget = 30
        os.makedirs(self.debug_output_dir, exist_ok=True)
        self.camera = Picamera2()
        self.camera.configure(
            self.camera.create_preview_configuration(
                main={
                    "size": (640, 480)
                }
            )
        )
        self.camera.start()
        self.face_detector = cv2.CascadeClassifier(self.cascade_path)
        logger.info("Camera and face detector initialized")

    def loop(self):
        frame = self.camera.capture_array()

        self._update_face_tracks(frame)
        if self.debug:
            cv2.imshow("Camera", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            cv2.waitKey(3)

    def cleanup(self):
        if self.camera:
            self.camera.stop()
            logger.info("Camera stopped and resources released")

    def _update_face_tracks(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.config.downscale_factor, fy=self.config.downscale_factor)

        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        detected_faces = self.face_detector.detectMultiScale(gray, 
                                                             scaleFactor = self.config.scale_factor, 
                                                             minNeighbors = self.config.min_neighbors, 
                                                             minSize = self.config.min_size
                                                            )

        updated_tracks = {}
        for (x, y, w, h) in detected_faces:
            # Scale the bounding box back to the original resolution
            x, y, w, h = int(x / self.config.downscale_factor), int(y / self.config.downscale_factor), int(w / self.config.downscale_factor), int(h / self.config.downscale_factor)
            cx, cy = x + w // 2, y + h //2
            matched_id = None

            for fid, (fx, fy, fw, fh, last_seen) in self.face_tracks.items():
                if abs(fx + fw // 2 - cx) < w and abs(fy + fh // 2 - cy) < h:
                    matched_id = fid
                    updated_tracks[fid] = (x, y, w, h, 0)
                    break
            
            if matched_id is None:
                updated_tracks[self.track_id] = (x, y, w, h, 0)
                matched_id = self.track_id
                self.track_id += 1

                if self.debug:
                    timestamp = int(time.time())
                    filename = os.path.join(self.debug_output_dir, f"face_{matched_id}_{timestamp}.jpg")
                    cv2.imwrite(filename, frame[y:y + h, x:x + w])
            
            if self.debug:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"ID {matched_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


        for fid, (fx, fy, fw, fh, last_seen) in self.face_tracks.items():
            if fid not in updated_tracks:
                updated_tracks[fid] = (fx, fy, fw, fh, last_seen + 1)

        self.face_tracks = {
            fid: data for fid, data in updated_tracks.items() if data[4] < self.frame_count_to_forget
        }

        if len(detected_faces) > 0:
            logger.info(f"Face detected: {detected_faces}")

            self.send_message(service_name = self.service_name,
                                data = {
                                    "time": self.config.restoration_duration,
                                    "level_steps": self.config.level_steps
                                },
                                queue=self.outgoing_queue)
            time.sleep(self.config.restoration_duration)
