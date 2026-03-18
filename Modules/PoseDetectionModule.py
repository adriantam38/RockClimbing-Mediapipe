import time
import cv2
import mediapipe as mp
import datetime
import csv

import numpy as np

from Models.Path import Path
from Models.Enums.Camera import CAMERA_ORIENTATION
from Modules.CalculationModule import *
from Modules.SoundModule import SoundModule
from Utilities.Constants import *
from Utilities.open_file import open_file
from PIL import Image, ImageTk

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


class PoseDetectionModule:

    # Methods for Recording Data

    def toggle_record_video(self, record):
        self.is_recording = record
        if self.is_recording:
            self.start_time = datetime.datetime.now()
            file_date_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            csv_file_name = open_file(f"{VIDEO_FILES_LOCATION}pose_test{file_date_time}.csv")
            self.csv_file = open(csv_file_name, "w", encoding='UTF8', newline='')
            self.writer = csv.writer(self.csv_file)
            video_file_name = open_file(f"{VIDEO_FILES_LOCATION}pose_test{file_date_time}.mp4")
            fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
            if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                resolution = (self.true_camera_height, self.true_camera_width)
            else:
                resolution = (self.true_camera_width, self.true_camera_height)
            self.out_video = cv2.VideoWriter(video_file_name, fourcc, RECORDING_FPS, resolution)
            self.saved_data = []
            print("Start Recording: " + file_date_time)
        else:
            try:
                self.out_video.release()
                for frame in self.saved_data:
                    if len(frame) == 1:
                        self.writer.writerow([f"{frame[0][0]}"])
                        self.writer.writerow(["None"])
                    else:
                        for part in frame:
                            self.writer.writerow(part)
                    self.writer.writerow("")
                self.csv_file.close()
                print("Finish Recording")
            except:
                print("csv_file and outVideo are not defined")

    def createPoint(self, result):
        x = result.x * self.camera_view_width
        y = result.y * self.camera_view_height
        return (x, y)

    def createFrameData(self, name, pt):
        frame_data = [name, "{:.2f}".format(pt[0]), "{:.2f}".format(pt[1])]
        return frame_data
    
    def findAngle(self, pt1, pt2, pt3):
        a = np.array([pt1[0], pt1[1]])
        b = np.array([pt2[0], pt2[1]])
        c = np.array([pt3[0], pt3[1]])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return "{:.2f}".format(np.degrees(angle))


    # Methods for Tapping on Screen and Calculate Angle

    def toggle_pause_video(self, pause):
        self.is_pause = pause
        if self.is_pause:
            self.cal_angle_module = CalculationModule(self.pause_image)
        else:
            self.cal_angle_module = None

    def tapOnScreen(self, x, y):
        self.image, distance, angle = self.cal_angle_module.calculate(x, y)
        return distance, angle

    def clearAllDots(self):
        self.image = self.cal_angle_module.clearAllDots()


    # Methods for Setting up and Stopping Camera

    def test_and_set_camera_resolutions(self, camera_number=None):
        self.settings = SaveLoadModule().load_settings()
        if camera_number is None:
            camera_number = self.settings.camera_number
        self.cap = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
        print(f"Start Camera (Number: {camera_number})")

        try:
            _, frame = self.cap.read()
            cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Camera is detected
            if DEBUG_MODE:
                if CAMERA_RESOLUTION_WIDTH is not None:
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION_WIDTH)
                if CAMERA_RESOLUTION_HEIGHT is not None:
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION_HEIGHT)

            self.true_camera_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.true_camera_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            if DEBUG_MODE:
                print(f"Camera Resolution: {self.true_camera_width}x{self.true_camera_height}")

            # Exchange width & height if portrait mode
            if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                return True, self.true_camera_height, self.true_camera_width
            else:
                return True, self.true_camera_width, self.true_camera_height

        except:
            # No camera is detected
            self.stop_camera_input()
            return False, None, None


    def set_camera_input(self, view, width, height, show_danger_alert=None):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.true_camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.true_camera_height)
        self.update_camera_view(view, width, height)
        self.sound_module = SoundModule()
        self.show_danger_alert = show_danger_alert
        self.pose = mp_pose.Pose(
            min_detection_confidence=0.5,   
            min_tracking_confidence=0.5
        )
        self.is_pause = False
        self.is_recording = False
        self.is_game_mode = False
        self.path = None
        self.debug_body_point = None


    def update_settings(self, settings):
        self.settings = settings


    def update_camera_view(self, view, width, height):
        self.camera_view = view
        self.camera_view_width = width
        self.camera_view_height = height


    def stop_camera_input(self):
        try:
            if DEBUG_MODE:
                print("Stop Camera")
            self.cap.release()
        except:
            print()

    
    def map_to_camera_point(self, point):
        width, height = self.camera_view_width, self.camera_view_height
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            width, height = height, width
        x, y = int(point[0] * width), int(point[1] * height)
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            x, y = y, width - x
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            x, y = height - y, x
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            x, y = width - x, height - y
        if self.settings.mirror_camera:
            x = self.camera_view_width - x
        return (x, y)

    def map_to_spelling_point(self, point_sequence):
        width, height = self.camera_view_width / 10, self.camera_view_height * 9 / 10
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT or self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            width, height = height, width
        width, height = int(width + 50*point_sequence), int(height)
        return (width, height)


    def map_to_universal_point(self, point):
        x, y = float(point[0]), float(point[1])
        width, height = self.camera_view_width, self.camera_view_height
        if self.settings.mirror_camera:
            x = width - x
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            x, y = height - y, x
            width, height = height, width
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            x, y = y, width - x
            width, height = height, width
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            x, y = width - x, height - y
        x, y = x / width, y / height
        return (x, y)


    # Game Mode Methods

    def start_game_mode(self, path_id, points, is_settings, progress_callback=None):
        self.is_game_mode = True
        self.is_settings = is_settings
        self.is_good_points_shown = is_settings
        self.is_bad_points_shown = is_settings
        self.progress_callback = progress_callback
        self.spelling_point_list = []
        self.point_index = 0
        self.foot_touch_ground_time = 0
        self.time_threshold = 100
        self.path_id = path_id
        self.universal_points = points
        self.universal_points_history = [self.universal_points.copy()]
        self.redo_history = []
        self.then = time.time_ns() // 1_000_000
        self.test_frames = []
        self.test_frame_rate()

    def toggle_show_good_points(self, is_shown):
        self.is_good_points_shown = is_shown

    def toggle_show_bad_points(self, is_shown):
        self.is_bad_points_shown = is_shown


    def finish_game_mode(self):
        result = self.path.evaluate_result()
        gamemode = self.universal_points[0][5]
        self.toggle_record_video(False)
        return result, gamemode

    def test_frame_rate(self):
        if self.cap.isOpened():                
            # Read the webcam input from openCV
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                return

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False

            # Setting the image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
                image = cv2.rotate(image, cv2.ROTATE_180)
            if self.settings.mirror_camera:
                image = cv2.flip(image, 1)

            # Process the image with Mediapipe AI Model
            results = self.pose.process(image)

            # Mark the pose with landmarks
            image.flags.writeable = True

            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=results.pose_landmarks,
                connections=[
                    (11,12),                                # Head
                    (11,23), (12,24), (23,24),              # Core Body
                    (11,13), (13,15), (15,19),              # Left Arm
                    (12,14), (14,16), (16,20),              # Right Arm
                    (23,25), (25,27), (27,29), (29,31),     # Left Leg
                    (24,26), (26,28), (28,30), (30,32)      # Right Leg
                ],
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=LANDMARK_COLOR,
                    thickness=LANDMARK_THICKNESS,
                    circle_radius=LANDMAKR_CIRCLE_RADIUS
                ),
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=CONNECTION_COLOR,
                    thickness=CONNECTION_THICKNESS,
                    circle_radius=CONNECTION_CIRCLE_RADIUS
                ))

            # Resize image to fit camera view size
            self.resized_image = cv2.resize(image.copy(), (self.camera_view_width, self.camera_view_height))
            self.image = self.resized_image.copy()

            # Send the image back to tkinter class (MetaHub)
            pilImg = Image.fromarray(self.image)
            imgtk = ImageTk.PhotoImage(image=pilImg)
            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)

            # Calculate time between frames
            self.now = time.time_ns() // 1_000_000 # time in milliseconds
            delta = self.now - self.then # time difference between current frame and previous frame
            self.then = self.now
            self.test_frames.append(delta/1000)

            if len(self.test_frames) < 10:
                self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.test_frame_rate)
            else:
                self.test_frames.pop(0)
                average_time_between_frames = sum(self.test_frames) / len(self.test_frames)
                if DEBUG_MODE:
                    print("average_time_between_frames:", average_time_between_frames)
                self.path = Path(self.path_id, self.universal_points, average_time_between_frames)
                if not self.is_settings:
                    self.sound_module.countdown()


    # Setting Game Path Methods

    def setting_game_screen_pressed(self, point, is_good, point_squence, alphabet, gamemode):
        universal_point = self.map_to_universal_point(point)
        self.universal_points.append((universal_point[0], universal_point[1], is_good, point_squence, alphabet, gamemode))
        self.path.update_points(self.universal_points)
        self.universal_points_history.append(self.universal_points.copy())
        self.redo_history.clear()
        self.setting_draw_points_for_pause_image()


    def setting_path_undo(self):
        if len(self.universal_points_history) > 1:
            self.redo_history.append(self.universal_points.copy())
            self.universal_points_history.pop()
            self.universal_points = self.universal_points_history[-1].copy()
            self.path.update_points(self.universal_points)
            self.setting_draw_points_for_pause_image()


    def setting_path_redo(self):
        if len(self.redo_history) > 0:
            self.universal_points = self.redo_history.pop()
            self.universal_points_history.append(self.universal_points.copy())
            self.path.update_points(self.universal_points)
            self.setting_draw_points_for_pause_image()


    def setting_path_clear_all_points(self, is_good):
        delete_points = []
        for point in self.universal_points:
            if point[2] == is_good:
                delete_points.append(point)
        if len(delete_points) > 0:
            self.universal_points = list(set(self.universal_points.copy()) - set(delete_points))
            self.path.update_points(self.universal_points)
            self.universal_points_history.append(self.universal_points.copy())
            self.redo_history.clear()
            self.setting_draw_points_for_pause_image()


    def setting_path_done(self):
        self.image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)
        if self.settings.mirror_camera:
            self.image = cv2.flip(self.image, 1)
        if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            self.image = cv2.rotate(self.image, cv2.ROTATE_180)
        return self.universal_points, self.image


    def setting_draw_points_for_pause_image(self):
        self.image = self.pause_image_no_dots.copy()
        if self.is_pause:
            for point in self.path.good_points:
                cv2.circle(self.image, (point[0], point[1]), DOT_RADIUS, GOOD_POINTS_COLOR, -1)
            for point in self.path.touching_good_points:
                cv2.circle(self.image, (point[0], point[1]), DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
            for point in self.path.touched_good_points:
                cv2.circle(self.image, (point[0], point[1]), DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
            for point in self.path.bad_points:
                cv2.circle(self.image, (point[0], point[1]), DOT_RADIUS, BAD_POINTS_COLOR, -1)


    # Start webcam input & pose detection (Call Repeatedly)

    def cameraInput(self):
        if self.cap.isOpened():
            if self.is_recording:
                time_delta_second = (datetime.datetime.now() - self.start_time).total_seconds()
                self.frame_data = [[str(datetime.timedelta(seconds=time_delta_second)), "x", "y"]]
                
            # Read the webcam input from openCV
            success, image = self.cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                return

            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False

            # Setting the image
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if self.settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            elif self.settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
                image = cv2.rotate(image, cv2.ROTATE_180)
            if self.settings.mirror_camera:
                image = cv2.flip(image, 1)

            # Process the image with Mediapipe AI Model
            results = self.pose.process(image)

            # Mark the pose with landmarks
            image.flags.writeable = True

            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=results.pose_landmarks,
                connections=[
                    (11,12),                                # Head
                    (11,23), (12,24), (23,24),              # Core Body
                    (11,13), (13,15), (15,19),              # Left Arm
                    (12,14), (14,16), (16,20),              # Right Arm
                    (23,25), (25,27), (27,29), (29,31),     # Left Leg
                    (24,26), (26,28), (28,30), (30,32)      # Right Leg
                ],
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=LANDMARK_COLOR,
                    thickness=LANDMARK_THICKNESS,
                    circle_radius=LANDMAKR_CIRCLE_RADIUS
                ),
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=CONNECTION_COLOR,
                    thickness=CONNECTION_THICKNESS,
                    circle_radius=CONNECTION_CIRCLE_RADIUS
                ))

            # For danger alert
            if self.show_danger_alert is not None:
                if self.settings.danger_alert and results.pose_landmarks:
                    left_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
                    right_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
                    left_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
                    right_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
                    if left_index < left_ankle and right_index > right_ankle:
                        self.sound_module.danger_alert()
                        self.show_danger_alert(True)
                    else:
                        self.show_danger_alert(False)
                else:
                    self.show_danger_alert(False)

            self.ground_screen_ratio = self.settings.ground_ratio_calibration_actual_value

            if self.is_game_mode:
                if len(self.universal_points) > 0:
                    if self.universal_points[0][5] == 2:
                        if results.pose_landmarks:
                            left_foot = self.createPoint(
                                results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX])
                            right_foot = self.createPoint(
                                results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX])
                            print(left_foot, right_foot)
                            print(self.camera_view_height * self.ground_screen_ratio, self.ground_screen_ratio)
                            if self.camera_view_height * self.ground_screen_ratio <= left_foot[
                                1] <= self.camera_view_height and self.camera_view_height * self.ground_screen_ratio <= \
                                    right_foot[1] <= self.camera_view_height:
                                self.foot_touch_ground_time += 1
                                print(self.foot_touch_ground_time)
                                if self.foot_touch_ground_time > self.time_threshold:
                                    self.progress_callback(len(self.path.player_input_alphabets),
                                                           -1,
                                                           self.universal_points[0][5])
                                    self.foot_touch_ground_time = 0




            # For recording pose information
            if self.is_recording:
                if results.pose_landmarks:
                    nose = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE])
                    left_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
                    right_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
                    left_elbow = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW])
                    right_elbow = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW])
                    left_shoulder = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER])
                    right_shoulder = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER])
                    left_hip = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP])
                    right_hip = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP])
                    left_knee = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE])
                    right_knee = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE])
                    left_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
                    right_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
                    self.frame_data.append(self.createFrameData("Head", nose))
                    self.frame_data.append(self.createFrameData("Left Hand", left_index))
                    self.frame_data.append(self.createFrameData("Right Hand", right_index))
                    self.frame_data.append(self.createFrameData("Left Elbow", left_elbow))
                    self.frame_data.append(self.createFrameData("Right Elbow", right_elbow))
                    self.frame_data.append(self.createFrameData("Left Shoulder", left_shoulder))
                    self.frame_data.append(self.createFrameData("Right Shoulder", right_shoulder))
                    self.frame_data.append(self.createFrameData("Left Hip", left_hip))
                    self.frame_data.append(self.createFrameData("Right Hip", right_hip))
                    self.frame_data.append(self.createFrameData("Left Knee", left_knee))
                    self.frame_data.append(self.createFrameData("Right Knee", right_knee))
                    self.frame_data.append(self.createFrameData("Left Ankle", left_ankle))
                    self.frame_data.append(self.createFrameData("Right Ankle", right_ankle))
                    self.frame_data.append(["Angles"])
                    self.frame_data.append(["Left Hand - Left Elbow - Left Shoulder", self.findAngle(left_index, left_elbow, left_shoulder)])
                    self.frame_data.append(["Right Hand - Right Elbow - Right Shoulder", self.findAngle(right_index, right_elbow, right_shoulder)])
                    self.frame_data.append(["Left Elbow - Left Shoulder - Left Hip", self.findAngle(left_elbow, left_shoulder, left_hip)])
                    self.frame_data.append(["Right Elbow - Right Shoulder - Right Hip", self.findAngle(right_elbow, right_shoulder, right_hip)])
                    self.frame_data.append(["Left Hip - Left Knee - Left Ankle", self.findAngle(left_hip, left_knee, left_ankle)])
                    self.frame_data.append(["Right Hip - Right Knee - Right Ankle", self.findAngle(right_hip, right_knee, right_ankle)])
                try:
                    record_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    self.out_video.write(record_image)
                    self.saved_data.append(self.frame_data)
                except:
                    print("outVideo can't write")

            # Resize image to fit camera view size
            self.resized_image = cv2.resize(image.copy(), (self.camera_view_width, self.camera_view_height))

            if not self.is_pause:
                self.pause_image_no_dots = self.resized_image.copy()

            # Detect pose in Game Mode
            if self.is_game_mode and self.path is not None:
                if not self.is_settings:
                    if results.pose_landmarks:
                        left_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX])
                        right_index = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX])
                        left_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE])
                        right_ankle = self.createPoint(results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE])
                        for body_point in [left_index, right_index, left_ankle, right_ankle]:
                            universal_point = self.map_to_universal_point(body_point)
                            self.path.evaluate_body_point(universal_point)

                    if self.progress_callback is not None:
                        if self.universal_points[0][5] == 2:
                            self.progress_callback(len(self.path.player_input_alphabets), 0, self.universal_points[0][5])
                        else:
                            self.progress_callback(len(self.path.touched_good_points), len(self.path.good_points), self.universal_points[0][5])

                if DEBUG_MODE:
                    if self.debug_body_point is not None:
                        cv2.circle(self.resized_image, self.debug_body_point, DOT_RADIUS, (0, 0, 255), -1)
                        universal_point = self.map_to_universal_point(self.debug_body_point)
                        self.path.evaluate_body_point(universal_point)

                if self.is_good_points_shown:
                    if self.path.player_input_alphabets is not None and len(self.universal_points) > 0:
                        if self.universal_points[0][5] == 2:
                            for point in self.path.player_input_alphabets:
                                if self.point_index < len(self.path.player_input_alphabets):
                                    spelling_point = self.map_to_spelling_point(self.point_index)
                                    if spelling_point not in self.spelling_point_list:
                                        self.spelling_point_list.append(spelling_point)
                                    cv2.putText(self.resized_image, str(point[1][4]),
                                                org=self.spelling_point_list[point[0]],
                                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(0, 255, 255),
                                                thickness=3)
                                    self.point_index += 1
                                else:
                                    self.point_index = 0
                                    spelling_point = self.map_to_spelling_point(self.point_index)
                                    if spelling_point not in self.spelling_point_list:
                                        self.spelling_point_list.append(spelling_point)
                                    cv2.putText(self.resized_image, str(point[1][4]),
                                                org=self.spelling_point_list[point[0]],
                                                fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=(0, 255, 255),
                                                thickness=3)
                                    self.point_index += 1


                    for point in self.path.good_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, GOOD_POINTS_COLOR, -1)
                        if self.universal_points[0][5] == 1:
                            cv2.putText(self.resized_image, str(point[3]+1), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)
                        elif self.universal_points[0][5] == 2:
                            cv2.putText(self.resized_image, str(point[4]), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)

                    for point in self.path.touching_good_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHING_GOOD_POINTS_COLOR, -1)
                        if self.universal_points[0][5] == 1:
                            cv2.putText(self.resized_image, str(point[3] + 1), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)
                        elif self.universal_points[0][5] == 2:
                            cv2.putText(self.resized_image, str(point[4]), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)

                    for point in self.path.touched_good_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHED_GOOD_POINTS_COLOR, -1)
                        if self.universal_points[0][5] == 1:
                            cv2.putText(self.resized_image, str(point[3] + 1), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)
                        elif self.universal_points[0][5] == 2:
                            cv2.putText(self.resized_image, str(point[4]), org=camera_point,
                                        fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 0, 255), thickness=3)

                if self.is_bad_points_shown:
                    for point in self.path.bad_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, BAD_POINTS_COLOR, -1)
                    for point in self.path.touching_bad_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHING_BAD_POINTS_COLOR, -1)
                    for point in self.path.touched_bad_points:
                        camera_point = self.map_to_camera_point(point)
                        cv2.circle(self.resized_image, camera_point, DOT_RADIUS, TOUCHED_BAD_POINTS_COLOR, -1)

            #default ground level is 1/5 of the screen
            self.ground_screen_ratio = self.settings.ground_ratio_calibration_actual_value

            if not self.is_game_mode and not self.is_recording:
                # If Calibration is on, show a yellow horizontal line with CALIBRATION_PIXELS (default: 100)
                if self.settings.distance_calibration_shown:
                    cv2.line(self.resized_image, (int(self.camera_view_width/2-CALIBRATION_PIXELS/2), int(self.camera_view_height/2)), (int(self.camera_view_width/2+CALIBRATION_PIXELS/2), int(self.camera_view_height/2)), (255, 255, 0), 5)
                    print(self.ground_screen_ratio)
                    print(self.camera_view_height)
                    ground_level = self.camera_view_height * self.ground_screen_ratio
                    cv2.line(self.resized_image, (int(0), int(ground_level)),
                              (int(self.camera_view_width), int(ground_level)), (255, 255, 255), 2)
                    # if self.ground_level_copy != self.ground_level:
                    #     cv2.line(self.resized_image, (int(0), int(self.ground_level)),
                    #              (int(self.camera_view_width), int(self.ground_level)), (255, 255, 255), 2)
                    #     self.ground_level_copy = self.ground_level

            if not self.is_pause:
                self.pause_image = self.resized_image.copy()
                self.image = self.resized_image.copy()

            # Send the image back to tkinter class (CameraView or SettingsView)
            pilImg = Image.fromarray(self.image)
            imgtk = ImageTk.PhotoImage(image=pilImg)
            self.camera_view.imgtk = imgtk
            self.camera_view.configure(image=imgtk)
            self.camera_view.after(int(1000 / SET_CAMERA_FPS), self.cameraInput)

    def update_ground_level(self):
        time.sleep(1)
        self.resized_image = None

    # Debug Methods

    def simulate_body_point(self, point=None):
        if point is not None:
            self.debug_body_point = point
        else:
            self.debug_body_point = None
