import ctypes
import i18n
from Modules.SaveLoadModule import SaveLoadModule
from tkinter import *
from Models.Enums.View import VIEW
from Utilities.Constants import *
from Utilities.open_file import open_file
from Views.PathsView import PathsView
from Views.SubViews.TopBar import TopBar
from Views.SubViews.ControlBar import ControlBar
from Views.HomeView import HomeView
from Views.CameraView import CameraView
from Views.ResultView import ResultView
from Views.RecordingsView import RecordingsView
from Views.SettingsView import SettingsView
from Views.VideoView import VideoView

class RockClimbing:
    def __init__(self):
        self.root = Tk()
        self.root.attributes("-fullscreen", True)
        self.root.bind("<KeyRelease>", self.key_up)
        self.window_width, self.window_height = get_fullscreen_size()
        if DEBUG_MODE:
            self.root.attributes("-fullscreen", False)
            self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            self.root.resizable(False, False)
            self.window_width, self.window_height = WINDOW_WIDTH, WINDOW_HEIGHT
        set_locale()

        self.gui_calculate_values()

        self.top_bar = TopBar(self.root, bg=THEME_COLOR_BLUE)
        self.control_bar = ControlBar(self.root, bg=THEME_COLOR_BLUE)

        self.home_view = HomeView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, exit=self.root.destroy, bg=THEME_COLOR_BLUE)
        self.camera_view = CameraView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, bg=THEME_COLOR_BLUE)
        self.paths_view = PathsView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, bg=THEME_COLOR_BLUE)
        self.result_view = ResultView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, bg=THEME_COLOR_BLUE)
        self.recordings_view = RecordingsView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, bg=THEME_COLOR_BLUE)
        self.video_view = VideoView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, bg=THEME_COLOR_BLUE)
        self.settings_view = SettingsView(self.root, view_width=self.view_width, view_height=self.view_height, navigate=self.navigate, change_title=self.change_title, change_buttons=self.change_buttons, change_keypad=self.change_keypad, bg=THEME_COLOR_BLUE)

        self.is_keypad_reverse = SaveLoadModule().load_settings().reverse_keypad

        if DEBUG_MODE:
            self.navigate(VIEW.HOME)
        else:
            self.navigate(VIEW.HOME)

    
    # Navigation Methods

    def navigate(self, view_to, **kwargs):
        self.reset_view()
        if view_to == VIEW.HOME:
            self.current_view = self.home_view
        elif view_to == VIEW.CAMERA:
            self.current_view = self.camera_view
        elif view_to == VIEW.PATHS:
            self.current_view = self.paths_view
        elif view_to == VIEW.RESULT:
            self.current_view = self.result_view
        elif view_to == VIEW.RECORDINGS:
            self.current_view = self.recordings_view
        elif view_to == VIEW.VIDEO:
            self.current_view = self.video_view
        elif view_to == VIEW.SETTINGS:
            self.current_view = self.settings_view
        self.current_view.launch(**kwargs)
        self.gui_set()


    def reset_view(self):
        self.home_view.place_forget()
        self.camera_view.place_forget()
        self.paths_view.place_forget()
        self.result_view.place_forget()
        self.recordings_view.place_forget()
        self.video_view.place_forget()
        self.settings_view.place_forget()


    def change_title(self, title):
        self.top_bar.change_title(title)


    def change_buttons(self, buttons):
        self.control_bar.change_buttons(buttons)


    # Key Press Actions

    def key_up(self, e):
        self.control_bar.invoke_button(e.char, self.is_keypad_reverse)


    def change_keypad(self, is_reverse):
        self.is_keypad_reverse = is_reverse
        self.root.bind("<KeyRelease>", self.key_up)


    # GUI Methods

    def gui_calculate_values(self):
        self.view_width = self.window_width - CONTROL_BAR_WIDTH
        self.view_height = self.window_height - TOP_BAR_HEIGHT


    def gui_set(self):
        self.top_bar.place(width=self.window_width, height=TOP_BAR_HEIGHT)
        self.control_bar.place(x=self.window_width-CONTROL_BAR_WIDTH, y=TOP_BAR_HEIGHT, width=CONTROL_BAR_WIDTH, height=self.window_height-TOP_BAR_HEIGHT)
        self.current_view.place(y=TOP_BAR_HEIGHT, width=self.window_width-CONTROL_BAR_WIDTH, height=self.window_height-TOP_BAR_HEIGHT)


def get_fullscreen_size():
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize


def set_locale():
    i18n.set('file_format', 'json')
    i18n.load_path.append(open_file(TRANSLATION_FILES_LOCATION))
    i18n.set('fallback', 'ch')


if __name__ == '__main__':
    rockClimbing = RockClimbing()
    mainloop()