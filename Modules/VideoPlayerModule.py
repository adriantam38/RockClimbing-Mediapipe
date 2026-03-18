import av
import time
import threading
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
from typing import Tuple
from Utilities.Constants import *

class VideoPlayerModule(tk.Label):

    def __init__(self, *args, video_info_loaded, second_update, video_end, **kwargs):
        super(VideoPlayerModule, self).__init__(*args, **kwargs)

        self.video_info_loaded = video_info_loaded
        self.second_update = second_update
        self.video_end = video_end

        self.reset_all()


    # Initialization

    def get_video(self, file_path):
        """ loads the video and generates callback event after loading """
        if DEBUG_MODE:
            print("2 VideoPlayerModule get_video")
        self.reset_all()
        self._loading_thread = threading.Thread(target=self.loading, args=(file_path,), daemon=True)
        self._loading_thread.start()


    def reset_all(self):
        """ stop removes the loaded video and reset the frame_number"""
        if DEBUG_MODE:
            print("3 VideoPlayerModule reset")
        self._playing = False
        self._paused = True
        self._loaded = False

        self._playing_thread = None
        self._loading_thread = None

        self._video_frames = []
        self._frame_rate = 1
        self._frame_size = (1280, 720)
        self._frame_total = 0

        self._video_duration = 0
        self._video_speed = 1.0
        
        self._current_frame_number = 0


    def loading(self, file_path: str):
        """ loads the frames from a thread """
        if DEBUG_MODE:
            print("4 VideoPlayerModule loading")
        current_thread = threading.current_thread()
        try:
            with av.open(file_path) as container:
                self._frame_rate = int(container.streams.video[0].average_rate)
                self._frame_size = (container.streams.video[0].width, container.streams.video[0].height)
                self._video_duration = float(container.streams.video[0].duration * container.streams.video[0].time_base)
                self._frame_total = container.streams.video[0].frames
                for frame in container.decode(video=0):
                    if self._loading_thread != current_thread:
                        return
                    self._video_frames.append(frame.to_image())
                self._loaded = True
                self.video_info_loaded(self._frame_size, self._video_duration)
        except Exception as e:
            raise e


    def set_video_size(self, video_view_width, video_view_height):
        """ tell video_player its size for resizing image """
        if DEBUG_MODE:
            print("7 VideoPlayerModule set_video_size")
        self.video_view_width = video_view_width
        self.video_view_height = video_view_height

    def loaded(self) -> bool:
        """ returns whether the video has been loaded """
        return self._loaded


    # Get Frame Methods

    def get_current_image(self) -> Image.Image:
        # Convert from RGB to BGR and numpy array to Image
        if DEBUG_MODE:
            print("10 VideoPlayerModule get_current_image")
        if self._loaded:
            current_image = self._video_frames[self._current_frame_number].copy().resize((self.video_view_width, self.video_view_height))
            image_array = np.array(current_image)[:, :, ::-1].copy()
            converted_image = Image.fromarray(image_array[:, :, [2, 1, 0]])
            converted_imagetk = ImageTk.PhotoImage(image=converted_image)
            return converted_imagetk
        else:
            return None


    def get_current_image_array(self) -> np.array:
        # Convert to numpy array for Calculation Module
        if DEBUG_MODE:
            print("11 VideoPlayerModule get_current_image_array")
        if self._loaded:
            current_image = self._video_frames[self._current_frame_number].copy().resize((self.video_view_width, self.video_view_height))
            image_array = np.array(current_image)[:, :, ::-1].copy()
            return image_array
        else:
            return None


    def play(self):
        """ plays the loaded video """

        self._paused = False
        if self._current_frame_number == len(self._video_frames):
            self._current_frame_number = 0

        if not self._playing:
            self._playing = True
            self._playing_thread = threading.Thread(target=self._update_frames, daemon=True)
            self._playing_thread.start()


    def is_paused(self) -> bool:
        """ returns if the video is paused """
        return self._paused

    def pause(self):
        """ pauses the video """
        self._paused = True

    def seek(self, time_stamp: float):

        if 0 < time_stamp < self._video_duration:
            self._current_frame_number = time_stamp * self._frame_rate

    def skip_sec(self, sec: int):
        """ skip by seconds """
        if 0 < self._current_frame_number + (sec * self._frame_rate) < self._frame_total:
            self._current_frame_number = self._current_frame_number + (sec * self._frame_rate)

        elif self._current_frame_number + (sec * self._frame_rate) < 0:
            self._current_frame_number = 0

        elif self._current_frame_number + (sec * self._frame_rate) > self._frame_total:
            self._current_frame_number = self._frame_total - 1

    def skip_frames(self, number_of_frames: int):
        """ skip by how many frames +ve or -ve """

        if number_of_frames < 0 and (self._current_frame_number - number_of_frames) > 0:
            self._current_frame_number -= number_of_frames

        elif number_of_frames > 0 and (self._current_frame_number + number_of_frames) > len(self._video_frames):
            self._current_frame_number += number_of_frames

    def current_duration(self) -> float:
        """ returns current playing duration in sec"""
        return self._current_frame_number / self._frame_rate

    def set_video_speed(self, speed):
        """ change the video speed """
        self._video_speed = 1 / speed

    def _update_frames(self):
        """ updates frame from thread """

        now = time.time_ns() // 1_000_000  # time in milliseconds
        sthen = now

        while self._playing:

            if self._loaded and self._current_frame_number >= len(self._video_frames):
                break

            if not self._paused and self._current_frame_number < len(self._video_frames):

                # Find the current time
                before = time.time_ns() // 1_000_000 # time in milliseconds

                # Copy the image of this frame to current_img variable
                self._current_img = self._video_frames[self._current_frame_number].copy()
                self._current_img_resized = self._current_img.resize((self.video_view_width, self.video_view_height))

                # Tell the video player to show this image
                self.display_frame()

                # Propagate to next frame
                self._current_frame_number += 1

                # Save the current time to next frame
                after = time.time_ns() // 1_000_000 # time in milliseconds

                # Calculate time difference between current frame and previous frame
                delta = after - before 

                # if DEBUG_MODE:
                #     print(self._current_frame_number, " : ", delta / 1000)

                if delta / 1000 < self._video_speed * SLEEP_DELTA / self._frame_rate:
                    time.sleep((self._video_speed * SLEEP_DELTA / self._frame_rate - delta / 1000))

                if self._current_frame_number % self._frame_rate == 0:
                    snow = time.time_ns() // 1_000_000 # time in milliseconds
                    sdelta = snow - sthen  # time difference between current frame and previous frame
                    sthen = snow
                    if DEBUG_MODE:
                        print("*************second:", sdelta/1000, "**************")
                        print()
                    self.second_update()

            if not self._loaded:
                time.sleep(0.0015)

        self._current_frame_number = 0
        self._playing = False
        self._paused = True
        self.video_end()


    def display_frame(self):
        """ updates the image in the label """
        self._current_imgtk = ImageTk.PhotoImage(self._current_img_resized)
        self.config(image=self._current_imgtk)