import cv2
import mediapipe as mp
import numpy as np
from scipy.spatial import distance as dist
import os
import logging
import threading
import time

# Suppress TensorFlow Lite and other warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.ERROR)
logging.getLogger('absl').setLevel(logging.ERROR)
logging.getLogger('google.protobuf').setLevel(logging.ERROR)

class EyeMonitor:
    def __init__(self, eye_ar_thresh, eye_closed_duration_thresh):
        self.eye_ar_thresh = eye_ar_thresh
        self.eye_closed_duration_thresh = eye_closed_duration_thresh
        self.start_time = None

        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Indexes for the left and right eyes in the MediaPipe Face Mesh
        self.lStart, self.lEnd = 362, 382
        self.rStart, self.rEnd = 33, 133

    def eye_aspect_ratio(self, eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # Compute the euclidean distance between the horizontal eye landmark
        C = dist.euclidean(eye[0], eye[3])

        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

    def monitor_eyes(self, service_running_flag):
        # Start the video stream
        cap = cv2.VideoCapture(0)
        # is_debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

        while service_running_flag.is_set():
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame with MediaPipe Face Mesh
            results = self.face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    left_eye = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(self.lStart, self.lEnd + 1)]
                    right_eye = [(face_landmarks.landmark[i].x, face_landmarks.landmark[i].y) for i in range(self.rStart, self.rEnd + 1)]

                    left_eye = np.array(left_eye) * [frame.shape[1], frame.shape[0]]
                    right_eye = np.array(right_eye) * [frame.shape[1], frame.shape[0]]

                    # Compute the eye aspect ratio for both eyes
                    leftEAR = self.eye_aspect_ratio(left_eye)
                    rightEAR = self.eye_aspect_ratio(right_eye)

                    # Average the eye aspect ratio together for both eyes
                    ear = (leftEAR + rightEAR) / 2.0

                    # Print EAR values for debugging
                    print(f"EAR: {ear:.2f}")

                    if ear >= self.eye_ar_thresh:
                        if self.start_time is None:
                            self.start_time = time.time()
                        elif time.time() - self.start_time >= self.eye_closed_duration_thresh:
                            logging.info("Eyes Closed for more than 5 seconds")
                            print("Eyes Closed for more than 5 seconds")
                            self.start_time = None  # Reset the timer after printing
                    else:
                        self.start_time = None

                    # if is_debug:
                    #     if ear >= self.eye_ar_thresh:
                    #         cv2.putText(frame, "Eyes Closed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    #     for point in left_eye:
                    #         cv2.circle(frame, tuple(point.astype(int)), 1, (0, 255, 0), -1)
                    #     for point in right_eye:
                    #         cv2.circle(frame, tuple(point.astype(int)), 1, (0, 255, 0), -1)

            # # Display the resulting frame
            # if is_debug:
            #     cv2.imshow("Frame", frame)

            # Break the loop on 'q' key press
            # if is_debug and cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        # When everything is done, release the capture
        cap.release()
        # if is_debug:
        #     cv2.destroyAllWindows()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    service_running_flag = threading.Event()
    service_running_flag.set()

    eye_monitor = EyeMonitor(eye_ar_thresh=1.49, eye_closed_duration_thresh=5)  # Adjusted threshold based on observations
    eye_monitor.monitor_eyes(service_running_flag)
