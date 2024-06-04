import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import subprocess
import os
import logging
import time

class EyeMonitor:
    def __init__(self, device_id, device_key, device_ip, service_running_flag, eye_ar_thresh, eye_ar_consec_frames, fps=30):
        self.COUNTER = 0
        self.device_id = device_id
        self.device_key = device_key
        self.device_ip = device_ip
        self.service_running_flag = service_running_flag
        self.eye_ar_thresh = eye_ar_thresh
        self.eye_ar_consec_frames = eye_ar_consec_frames
        self.fps = fps

        # Load dlib's face detector and shape predictor
        self.detector = dlib.get_frontal_face_detector()
        predictor_path = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")
        self.predictor = dlib.shape_predictor(predictor_path)

        # Grab the indexes of the facial landmarks for the left and right eye
        (self.lStart, self.lEnd) = (42, 48)
        (self.rStart, self.rEnd) = (36, 42)

    def eye_aspect_ratio(self, eye):
        # Compute the euclidean distances between the two sets of vertical eye landmarks
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # Compute the euclidean distance between the horizontal eye landmark
        C = dist.euclidean(eye[0], eye[3])

        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear

    def monitor_eyes(self):
        # Start the video stream
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        is_debug = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

        # Start time for FPS calculation
        start_time = time.time()
        frame_count = 0

        while self.service_running_flag.is_set():
            frame_start_time = time.time()  # Frame start time for manual FPS control

            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                break

            # Increment frame count
            frame_count += 1

            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the grayscale frame
            rects = self.detector(gray, 0)

            for rect in rects:
                shape = self.predictor(gray, rect)
                shape = np.array([[p.x, p.y] for p in shape.parts()])

                # Extract the left and right eye coordinates
                leftEye = shape[self.lStart:self.lEnd]
                rightEye = shape[self.rStart:self.rEnd]

                # Compute the eye aspect ratio for both eyes
                leftEAR = self.eye_aspect_ratio(leftEye)
                rightEAR = self.eye_aspect_ratio(rightEye)

                # Average the eye aspect ratio together for both eyes
                ear = (leftEAR + rightEAR) / 2.0

                # Compute the convex hull for the left and right eye and visualize it
                if is_debug:
                    leftEyeHull = cv2.convexHull(leftEye)
                    rightEyeHull = cv2.convexHull(rightEye)
                    cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                    cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

                # Check if the eye aspect ratio is below the blink threshold
                if ear < self.eye_ar_thresh:
                    self.COUNTER += 1
                    if self.COUNTER >= self.eye_ar_consec_frames:
                        logging.info("Eyes Closed for 10 seconds, turning off the TV")
                        subprocess.run(["python", "socket_control/control_device.py", "turn_off", "-d", self.device_id, "-l", self.device_key, "-i", self.device_ip])
                        if is_debug:
                            cv2.putText(frame, "Eyes Closed", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        self.COUNTER = 0  # Reset counter after turning off the TV
                else:
                    self.COUNTER = 0

            # Display the resulting frame
            if is_debug:
                cv2.imshow("Frame", frame)

            # Calculate elapsed time for this frame
            frame_elapsed_time = time.time() - frame_start_time

            # Calculate sleep time to maintain the desired FPS
            sleep_time = max(0, (1.0 / self.fps) - frame_elapsed_time)
            time.sleep(sleep_time)

            # Break the loop on 'q' key press
            if is_debug and cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Calculate and print FPS
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time
        print(f"Approximate FPS: {fps}")

        # When everything is done, release the capture
        cap.release()
        if is_debug:
            cv2.destroyAllWindows()
