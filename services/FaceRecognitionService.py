import cv2
import os
import time
import logging
from threading import Thread, Event
from queue import Queue
from picamera2 import Picamera2

class FaceRecognitionService:
    def __init__(self, 
                 cascade_path="face_recognition/haarcascade_frontalface_default.xml", 
                 debug_output_dir="detected_faces", 
                 callback = None,
                 config= {
                     "scaleFactor": 1.2,
                     "minNeighbors": 8,
                     "minSize": (50, 50)
                 }):
        self.config = config
        self.debug_output_dir= debug_output_dir
        self.face_tracks = {}
        self.track_id = 0
        self.frame_count_to_forget = 30
        self.camera = None
        self.face_detector = cv2.CascadeClassifier(cascade_path)
        self.face_queue = Queue()
        self.stop_event = Event()
        self.thread = None
        self.callback = callback

        os.makedirs(self.debug_output_dir, exist_ok=True)
        logging.info("FaceRecognitionService initialized")

    def start_camera(self, resolution=(640, 480)):
        self.camera = Picamera2()
        self.camera.configure(
            self.camera.create_preview_configuration(
                main= {
                    "size": resolution
                }
            )
        )
        self.camera.start()
        logging.info("Camera started with resolution %s", resolution)

    def stop_camera(self):
        if self.camera:
            self.camera.stop()
            logging.info("Camera stopped")

    def detect_faces(self, frame):
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)

        detected_faces = self.face_detector.detectMultiScale(gray, **self.config)

        updated_tracks = {}
        for (x, y, w, h) in detected_faces:
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

                timestamp = int(time.time())
                filename = os.path.join(self.debug_output_dir, f"face_{matched_id}_{timestamp}.jpg")
                cv2.imwrite(filename, frame[y:y + h, x:x + w])
            
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {matched_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)


        for fid, (fx, fy, fw, fh, last_seen) in self.face_tracks.items():
            if fid not in updated_tracks:
                updated_tracks[fid] = (fx, fy, fw, fh, last_seen + 1)

        self.face_tracks = {
            fid: data for fid, data in updated_tracks.items() if data[4] < self.frame_count_to_forget
        }

        if len(detected_faces) > 0:
            """ self.callback() """
            self.face_queue.put((detected_faces, matched_id))

    def show_video(self, frame):
        cv2.imshow("Camera", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.stop_event.set()

    def run_in_background(self):
        def target():
            while not self.stop_event.is_set():
                frame = self.camera.capture_array()
                self.detect_faces(frame)
                self.show_video(frame)
                """ time.sleep(0.1) #for better performance """

        self.thread = Thread(target=target, daemon=True)
        self.thread.start()
        logging.info("FaceRecognitionService running in the background")

    def stop_service(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join()
        self.stop_camera()
        logging.info("FaceRecognitionService stopped")

    def get_detected_faces(self):
        try:
            return self.face_queue.get_nowait()
        except Exception:
            return None

