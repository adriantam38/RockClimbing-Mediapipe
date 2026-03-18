import PIL
import i18n
from datetime import timedelta
from tkinter import *
from Models.ControlBarButton import ControlBarButton
from Models.Enums.View import VIEW
from Modules.CalculationModule import CalculationModule
from Modules.VideoPlayerModule import VideoPlayerModule
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *


class VideoView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        # Default video speed is 1x (0.5x, 1x, 2x)
        self.video_speed = 1.0

        self.gui_calculate_values()

        self.background_view = Label(self, bg='black')
        self.video_player = VideoPlayerModule(self, video_info_loaded=self.video_info_loaded, second_update=self.second_update, video_end=self.video_ended)
        self.bottom_bar = Label(self, bg=THEME_COLOR_BLUE)
        
        # This image view appears when video player pause (and disappears)
        self.image_view = Label(self)
        self.image_view.bind("<ButtonRelease-1>", self.create_dot)
        self.distance_angle_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE))

        self.progress_slider = Scale(self.bottom_bar, showvalue=0, from_=0, to=0, orient="horizontal", bg=THEME_COLOR_BLUE, command=self.progress_bar_pressed)
        self.time_label = Label(self.bottom_bar, font=(FONT_FAMILY, LABEL_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.gui_set()


    # Navigation Methods

    def launch(self, file_path, video_title):
        if DEBUG_MODE:
            print("1 VideoView launch")
        i18n.set('locale', SaveLoadModule().load_settings().locale)
        self.change_title(video_title)
        self.buttons = {
            0: ControlBarButton(i18n.t('t.play'), lambda: self.play_pause_video(play=True)),
            2: ControlBarButton("1.0x", self.toggle_speed),
            9: ControlBarButton(i18n.t('t.leave'), lambda: self.navigate(VIEW.RECORDINGS), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)
        self.progress_slider.set(0)
        self.video_player.get_video(file_path)


    def video_info_loaded(self, frame_size, duration):
        if DEBUG_MODE:
            print("5 VideoView video_info_loaded")
        self.gui_video_view_set(video_width=frame_size[0], video_height=frame_size[1])
        self.video_player.set_video_size(self.video_view_width, self.video_view_height)
        self.duration = str(timedelta(seconds=round(duration, 0)))
        self.current_duration = str(timedelta(seconds=0))
        self.time_label.config(text=f"{self.current_duration} / {self.duration}")
        self.progress_slider.config(to=duration)
        self.play_pause_video(play=False)


    def second_update(self):
        """ update when each second played """
        print("second_update")
        self.progress_slider.set(self.video_player.current_duration())

    
    def video_ended(self):
        """ handle video ended """
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_video(play=False)
        # self.buttons[0] = ControlBarButton("Reset", lambda: self.play_pause_video(play=False, reset=True))
        # self.change_buttons(self.buttons)


    # Button Actions

    def play_pause_video(self, play=False, reset=False):
        if DEBUG_MODE:
            print("8 VideoView play_pause_video", play, reset)
        """ pauses and plays """
        if self.video_player.loaded():
            self.clear_play_pause_video()
            if reset:                                       # If in the end of the video, set to the beginning
                self.progress_slider.set(0)
            if play:
                self.buttons[0] = ControlBarButton(i18n.t('t.pause'), lambda: self.play_pause_video(play=False))
                self.video_player.place(relx=0.5, width=self.video_view_width, height=self.video_view_height, anchor=N)
                self.video_player.play()
            else:
                self.buttons[0] = ControlBarButton(i18n.t('t.play'), lambda: self.play_pause_video(play=True))
                self.current_imgtk = self.video_player.get_current_image()
                self.image_view.configure(image=self.current_imgtk)
                self.image_view.place(relx=0.5, width=self.video_view_width, height=self.background_view_height, anchor=N)
                self.buttons[4] = ControlBarButton(i18n.t('t.clear'), self.clear_btn_pressed)
                self.cal_angle_module = CalculationModule(image=self.video_player.get_current_image_array(), vid_player=True)
            self.change_buttons(self.buttons)


    def clear_play_pause_video(self):
        if DEBUG_MODE:
            print("9 VideoView clear_play_pause_video")
        self.buttons.pop(0, None)
        self.buttons.pop(4, None)
        self.distance_angle_label.place_forget()
        self.image_view.place_forget()
        self.video_player.place_forget()
        self.video_player.pause()
        self.cal_angle_module = None


    def toggle_speed(self):
        """ toggle video speed (0.5x, 1x, 2x) """
        if self.video_speed == 0.5:
            self.video_speed = 1.0
        elif self.video_speed == 1.0:
            self.video_speed = 2.0
        elif self.video_speed == 2.0:
            self.video_speed = 0.5
        self.buttons[2] = ControlBarButton(f"{self.video_speed}x", self.toggle_speed)
        self.change_buttons(self.buttons)
        self.video_player.set_video_speed(self.video_speed)


    def clear_btn_pressed(self):
        self.image_with_angle = self.cal_angle_module.clearAllDots()
        self.current_imgtk = PIL.Image.fromarray(self.image_with_angle[:, :, [2, 1, 0]])
        self.current_imgtk = PIL.ImageTk.PhotoImage(image=self.current_imgtk)
        self.image_view.configure(image=self.current_imgtk)
        self.distance_angle_label.place_forget()


    # Other Methods

    def progress_bar_pressed(self, value):
        """ used to seek a specific timeframe """
        self.current_duration = str(timedelta(seconds=int(value)))
        self.time_label.config(text=f"{self.current_duration} / {self.duration}")
        self.video_player.seek(int(value))


    def create_dot(self, event):
        if DEBUG_MODE:
            print("B1 VideoView create_dot")
        self.image_with_angle, distance, angle = self.cal_angle_module.calculate(event.x, event.y)
        self.current_imgtk = PIL.Image.fromarray(self.image_with_angle[:, :, [2, 1, 0]])
        self.current_imgtk = PIL.ImageTk.PhotoImage(image=self.current_imgtk)
        self.image_view.configure(image=self.current_imgtk)
        if distance:
            self.distance_angle_label.config(text=i18n.t('t.distance')+": {:.2f} m".format(distance))
            self.distance_angle_label.place(relx=0.5, y=15, anchor=N)
        elif angle:
            self.distance_angle_label.config(text=i18n.t('t.angle')+": {:.2f}".format(angle))
            self.distance_angle_label.place(relx=0.5, y=15, anchor=N)
        else:
            self.distance_angle_label.place_forget()


    # GUI Methods

    def gui_calculate_values(self):
        self.background_view_width = self.view_width
        self.background_view_height = self.view_height - VIDEO_VIEW_BOTTOM_BAR_HEIGHT


    def gui_video_view_set(self, video_width, video_height):
        if DEBUG_MODE:
            print("6 VideoView gui_video_view_set")
        background_view_ratio = self.background_view_width / self.background_view_height
        video_view_ratio = video_width / video_height

        if background_view_ratio > video_view_ratio:
            # The width of background_view is larger than the width of video_view
            self.video_view_height = int(self.background_view_height)
            self.video_view_width = int(self.background_view_height * video_view_ratio)
        else:
            # The height of background_view is larger than the height of video_view
            self.video_view_width = int(self.background_view_width)
            self.video_view_height = int(self.background_view_width / video_view_ratio)


    def gui_set(self):
        self.background_view.place(width=self.background_view_width, height=self.background_view_height)
        self.bottom_bar.place(y=self.background_view_height, width=self.view_width, height=VIDEO_VIEW_BOTTOM_BAR_HEIGHT)
        self.progress_slider.place(relx=0.05, rely=0.5, relwidth=0.75, anchor=W)
        self.time_label.place(relx=0.8, rely=0.5, relwidth=0.2, height=VIDEO_VIEW_BOTTOM_BAR_HEIGHT, anchor=W)