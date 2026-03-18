import tkinter.messagebox
from tkinter.simpledialog import askstring

import i18n
import ctypes
from tkinter import *
from Models.ControlBarButton import ControlBarButton
from Models.Enums.Camera import CAMERA_STATE
from Models.Enums.View import VIEW
from Models.Timer import Timer
from Modules.PoseDetectionModule import PoseDetectionModule
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *

class CameraView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.navigate_without_stop_camera = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.point_sequence = 0
        self.alphabet = ''
        self.gamemode = 0
        self.is_obstacle_course = False
        self.is_sequence_course = False
        self.is_alphabet_course = False

        self.countdown = None
        self.timer = None

        self.background_view = Label(self, bg='black')
        self.camera_view = Label(self)

        if DEBUG_MODE:
            self.camera_view.bind("<B1-Motion>", self.screen_moved)

        self.camera_view.bind("<ButtonRelease-1>", self.screen_pressed_left)
        self.camera_view.bind("<ButtonRelease-3>", self.screen_pressed_right)

        self.distance_angle_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.status_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.countdown_label = Label(self, font=(FONT_FAMILY, COUNTDOWN_FONT_SIZE), borderwidth=5, relief='solid', bg=THEME_COLOR_BLUE)
        self.timer_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.progress_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.reminder_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.pose_detection = PoseDetectionModule()

        self.gui_set()


    # Navigation Methods

    def launch(self, is_game=False, is_settings=False, path_id=None, path_name=None, points=[], path_data=None, path_images=[]):
        save_load_module = SaveLoadModule()
        i18n.set('locale', save_load_module.load_settings().locale)
        self.change_title(i18n.t('t.camera'))
        self.is_game = is_game
        self.is_settings = is_settings
        self.path_id = path_id
        self.path_name = path_name
        self.path_data = path_data
        self.path_images = path_images

        isCameraDetected, self.camera_width, self.camera_height = self.pose_detection.test_and_set_camera_resolutions()
        if not isCameraDetected:
            isCameraDetected, self.camera_width, self.camera_height = self.pose_detection.test_and_set_camera_resolutions(0)
            if not isCameraDetected:
                # If there is no camera detected, go back to home view
                ctypes.windll.user32.MessageBoxW(0, i18n.t('t.no_camera_is_detected'), i18n.t('t.camera_is_unavailable'), 0)
                self.navigate_without_stop_camera(VIEW.HOME)
                return
            else:
                # If there is another camera detected, save this camera number
                save_load_module = SaveLoadModule()
                settings = save_load_module.load_settings()
                settings.update(camera_number=0)
                save_load_module.save_settings(settings)

        self.gui_camera_view_set()
        self.pose_detection.set_camera_input(self.camera_view, self.camera_view_width, self.camera_view_height, show_danger_alert=self.show_danger_alerts)

        if is_game or is_settings:

            points_copy = []
            for point in points:
                points_copy.append((point[0], point[1], point[2], point[3], point[4],point[5]))

            #edit
            try:
                if points_copy[0][5] == 1:
                    self.change_title(path_name + ' (' + i18n.t('t.game_mode_1') + ') ')
                elif points_copy[0][5] == 2:
                    self.change_title(path_name + ' (' + i18n.t('t.game_mode_2') + ') ')
                else:
                    self.change_title(path_name + ' (' + i18n.t('t.game_mode_0') + ') ')
            except:
                self.change_title(path_name + ' (' + i18n.t('t.game_mode_0') + ') ')
            self.path_name = path_name

            if is_game:
                for point in points_copy:
                    if point[2] == True:
                        self.have_good_points = True
                        break
                    else:
                        self.have_good_points = False
                if self.have_good_points:
                    self.good_points_is_shown = True
                    if points_copy[0][5] == 0:
                        self.bad_points_is_shown = True
                    else:
                        self.bad_points_is_shown = False
                    self.pose_detection.start_game_mode(path_id, points_copy, False, self.progress_update)
                    self.pose_detection.toggle_show_good_points(is_shown=self.good_points_is_shown)
                    self.pose_detection.toggle_show_bad_points(is_shown=self.bad_points_is_shown)
                else:
                    self.navigate(VIEW.PATHS)
                    tkinter.messagebox.showerror(title=i18n.t('t.error'), message=i18n.t('t.error_path'))

            if is_settings:
                self.pose_detection.start_game_mode(path_id, points_copy, True)

        self.pose_detection.cameraInput()
        self.clear_labels()
        
        if self.is_game:
            if self.have_good_points:
                self.buttons = {
                    0: ControlBarButton(i18n.t('t.finish'), self.finish_btn_pressed),
                    2: ControlBarButton(i18n.t('t.hide_touch_points'), self.good_points_button_pressed),
                    3: ControlBarButton(i18n.t('t.hide_avoid_points'), self.bad_points_button_pressed),
                    5: ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING)),
                    9: ControlBarButton(i18n.t('t.leave'), lambda: self.navigate(VIEW.PATHS), THEME_COLOR_PINK)
                }
                self.countdown = Timer(self.countdown_update, True, 6, self.countdown_finish)
                self.countdown.start()
                self.countdown_label.place(relx=0.5, rely=0.5, width=400, height=400, anchor=CENTER)
                self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")
                self.change_buttons(self.buttons)
                self.change_camera_state(CAMERA_STATE.NORMAL)

                # A new window is created in a separate monitor for projector to project on the surface of rock climbing wall


                # projector_view = Toplevel(self)
                # projector_view.overrideredirect(True)
                # projector_view.geometry('%dx%d+%d+%d'%(1920,1080,0,-1080))
                # projector_view.attributes('-fullscreen', False)
                # projector_view.title("New Window")
                # print(WINDOW_HEIGHT, WINDOW_WIDTH)
                # projector_view.pose_detection.cameraInput()


        elif self.is_settings:
            if self.gamemode == 0:
                self.buttons = {
                    0: ControlBarButton(i18n.t('t.change_game_mode'), self.change_game_mode_btn_pressed),
                    1: ControlBarButton(i18n.t('t.pause'), lambda: self.change_camera_state(CAMERA_STATE.PAUSE)),
                    2: ControlBarButton(i18n.t('t.undo'), self.undo_btn_pressed),
                    3: ControlBarButton(i18n.t('t.redo'), self.redo_btn_pressed),
                    5: ControlBarButton(i18n.t('t.clear_all_touch_points'), self.clear_all_touch_points_btn_pressed),
                    6: ControlBarButton(i18n.t('t.clear_all_avoid_points'), self.clear_all_avoid_points_btn_pressed),
                    8: ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK),
                    9: ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)
                }
            self.reminder_label.config(text=f"""{i18n.t('t.press_left_mouse_button_for_new_touch_point')}
{i18n.t('t.press_right_mouse_button_for_new_avoid_point')}""")
            self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)
            self.point_sequence = 0
            self.alphabet = ''
            self.gamemode = 0
            self.is_obstacle_course = True
            self.is_alphabet_course = False
            self.is_sequence_course = False
            self.change_buttons(self.buttons)
            self.change_camera_state(CAMERA_STATE.NORMAL)

        else:
            self.buttons = {
                0: ControlBarButton(i18n.t('t.pause'), lambda: self.change_camera_state(CAMERA_STATE.PAUSE)),
                1: ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING)),
                9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(VIEW.HOME), THEME_COLOR_PINK)
            }
            self.reminder_label.config(text=f"{i18n.t('t.DANGER_ALERT_Two_hands_are_outside_feet_area')}")
            self.change_buttons(self.buttons)
            self.change_camera_state(CAMERA_STATE.NORMAL)

    
    def navigate(self, view, **kwargs):
        self.pose_detection.stop_camera_input()
        if self.countdown is not None:
            self.countdown.reset()
        if self.timer is not None:
            self.timer.reset()
        self.navigate_without_stop_camera(view, **kwargs)


    # Camera Methods

    def change_camera_state(self, state):
        self.clear_camera_state()
        if state == CAMERA_STATE.NORMAL:
            self.pose_detection.toggle_pause_video(pause=False)
            self.pose_detection.toggle_record_video(record=False)
            if self.is_game:
                self.buttons[5] = ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING))
            elif self.is_settings:
                self.buttons[0] = ControlBarButton(i18n.t('t.change_game_mode'), self.change_game_mode_btn_pressed)
            else:
                self.buttons[1] = ControlBarButton(i18n.t('t.pause'), lambda: self.change_camera_state(CAMERA_STATE.PAUSE))
                if not self.is_settings:
                    self.buttons[1] = ControlBarButton(i18n.t('t.record'), lambda: self.change_camera_state(CAMERA_STATE.RECORDING))
        elif state == CAMERA_STATE.PAUSE:
            self.pose_detection.toggle_pause_video(pause=True)
            if not self.is_game:
                self.buttons[1] = ControlBarButton(i18n.t('t.play'), lambda: self.change_camera_state(CAMERA_STATE.NORMAL))
            if not self.is_game and not self.is_settings:
                self.buttons[1] = ControlBarButton(i18n.t('t.clear'), lambda: self.clear_btn_pressed())
            self.status_label.config(text=f"{i18n.t('t.pause')}...")
            self.status_label.place(x=15, y=15)
        elif state == CAMERA_STATE.RECORDING:
            self.pose_detection.toggle_record_video(record=True)
            if self.is_game:
                self.buttons[5] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.change_camera_state(CAMERA_STATE.NORMAL))
            elif not self.is_settings:
                self.buttons[1] = ControlBarButton(i18n.t('t.stop_recording'), lambda: self.change_camera_state(CAMERA_STATE.NORMAL))
            self.status_label.config(text=f"{i18n.t('t.recording')}...")
            self.status_label.place(x=15, y=15)
        self.camera_state = state
        self.change_buttons(self.buttons)


    def clear_camera_state(self):
        if self.is_game:
            self.buttons.pop(5, None)
        else:
            self.buttons.pop(0, None)
            self.buttons.pop(1, None)
        self.status_label.place_forget()
        self.distance_angle_label.place_forget()

    def change_game_mode_btn_pressed(self):
        self.clear_all_touch_points_btn_pressed()
        self.clear_all_avoid_points_btn_pressed()
        self.alphabet = ''
        # Sequence course = gamemode 1
        if self.gamemode == 0:
            self.change_title(self.path_name + ' (' + i18n.t('t.game_mode_1') + ') ')
            self.is_sequence_course = True
            self.is_obstacle_course = False
            self.is_alphabet_course = False
            self.gamemode += 1
        # Alphabet course = gamemode 2
        elif self.gamemode == 1:
            self.change_title(self.path_name + ' (' + i18n.t('t.game_mode_2') + ') ')
            self.is_alphabet_course = True
            self.is_sequence_course = False
            self.is_obstacle_course = False
            self.gamemode += 1
        # Obstacle course = gamemode 0
        elif self.gamemode == 2:
            self.change_title(self.path_name + ' (' + i18n.t('t.game_mode_0') + ') ')
            self.is_obstacle_course = True
            self.is_alphabet_course = False
            self.is_sequence_course = False
            self.gamemode = 0


    # Timer Methods

    def countdown_update(self, time):
        self.countdown_label.config(text=time[-1])

    
    def countdown_finish(self):
        self.countdown_label.place_forget()
        self.timer = Timer(self.timer_update)
        self.timer.start()
        self.timer_label.place(relx=1.0, width=200, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=NE)
        self.progress_label.place(y=CONTROL_BAR_BUTTON_HEIGHT, relx=1.0, width=200, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=NE)


    def timer_update(self, time):
        self.timer_label.config(text=time)

    # ending gamemode
    def progress_update(self, touched, all, gamemode):
        if gamemode == 2:
            self.progress_label.config(text=f"{touched}")
        else:
            self.progress_label.config(text=f"{touched}/{all}")
            if touched == all:
                self.finish_btn_pressed()


    # Button Actions

    def clear_btn_pressed(self):
        self.pose_detection.clearAllDots()
        self.distance_angle_label.place_forget()


    def screen_pressed_left(self, event):
        if not self.is_settings:
            if self.camera_state == CAMERA_STATE.PAUSE:
                distance, angle = self.pose_detection.tapOnScreen(x=event.x, y=event.y)
                if distance:
                    self.distance_angle_label.config(text=i18n.t('t.distance')+": {:.2f} m".format(distance))
                    self.distance_angle_label.place(relx=0.5, y=15, anchor=N)                
                elif angle:
                    self.distance_angle_label.config(text=i18n.t('t.angle')+":{:.2f}".format(angle))
                    self.distance_angle_label.place(relx=0.5, y=15, anchor=N)
                else:
                    self.distance_angle_label.place_forget()
        else:
            if self.is_alphabet_course == True:
                self.alphabet = askstring('Alphabet', 'Please input alphabet')
            else:
                self.alphabet = ''
            self.pose_detection.setting_game_screen_pressed(point=(event.x, event.y), is_good=True, point_squence=self.point_sequence, alphabet=self.alphabet, gamemode= self.gamemode)
            if self.is_sequence_course  == True or self.is_alphabet_course == True:
                self.point_sequence += 1
            else:
                self.point_sequence = 0
        if DEBUG_MODE:
            self.pose_detection.simulate_body_point()


    def screen_pressed_right(self, event):
        if self.is_settings & self.is_obstacle_course:
            self.pose_detection.setting_game_screen_pressed(point=(event.x, event.y), is_good=False, point_squence=0, alphabet=self.alphabet, gamemode= self.gamemode)


    # Button Actions (Game)

    def finish_btn_pressed(self):
        result, gamemode = self.pose_detection.finish_game_mode()
        result.update_time(self.timer_label['text'])
        self.pose_detection.stop_camera_input()
        self.navigate(VIEW.RESULT, result=result, gamemode=gamemode)


    def return_btn_pressed(self):
        self.pose_detection.stop_camera_input()
        self.navigate(VIEW.PATHS)


    def good_points_button_pressed(self):
        self.good_points_is_shown = not self.good_points_is_shown
        self.pose_detection.toggle_show_good_points(is_shown=self.good_points_is_shown)
        self.reset_toggle_buttons()


    def bad_points_button_pressed(self):
        self.bad_points_is_shown = not self.bad_points_is_shown
        self.pose_detection.toggle_show_bad_points(is_shown=self.bad_points_is_shown)
        self.reset_toggle_buttons()


    def reset_toggle_buttons(self):
        if self.good_points_is_shown:
            self.buttons[2] = ControlBarButton(f"{i18n.t('t.hide_touch_points')}", self.good_points_button_pressed)
        else:
            self.buttons[2] = ControlBarButton(f"{i18n.t('t.show_touch_points')}", self.good_points_button_pressed)
        if self.bad_points_is_shown:
            self.buttons[3] = ControlBarButton(f"{i18n.t('t.hide_avoid_points')}", self.bad_points_button_pressed)
        else:
            self.buttons[3] = ControlBarButton(f"{i18n.t('t.show_avoid_points')}", self.bad_points_button_pressed)
        self.change_buttons(self.buttons)


    # Button Actions (Settings)

    def undo_btn_pressed(self):
        self.pose_detection.setting_path_undo()


    def redo_btn_pressed(self):
        self.pose_detection.setting_path_redo()


    def clear_all_touch_points_btn_pressed(self):
        self.point_sequence = 0
        self.pose_detection.setting_path_clear_all_points(is_good=True)


    def clear_all_avoid_points_btn_pressed(self):
        self.pose_detection.setting_path_clear_all_points(is_good=False)


    def cancel_btn_pressed(self):
        self.navigate(VIEW.PATHS, is_settings=True, path_data=self.path_data)


    def confirm_btn_pressed(self):
        new_path_data = self.path_data.copy()
        for row in self.path_data:
            if row[0] == self.path_id:
                new_path_data.remove(row)
        new_points, new_image = self.pose_detection.setting_path_done()
        self.path_images.append((self.path_id, new_image))
        for point in new_points:
            new_path_data.append([self.path_id, self.path_name, point[0], point[1], point[2], point[3], point[4], self.gamemode])
        print(new_path_data)
        self.navigate(VIEW.PATHS, is_settings=True, path_data=new_path_data, path_images=self.path_images)


    # Other Methods

    def clear_labels(self):
        self.countdown_label.place_forget()
        self.reminder_label.place_forget()
        self.timer_label.place_forget()
        self.progress_label.place_forget()


    def show_danger_alerts(self, show):
        if show:
            self.reminder_label.place(relx=0.5, rely=1.0, y=-10, width=600, anchor=S)
        else:
            self.reminder_label.place_forget()


    # GUI Methods

    def gui_camera_view_set(self):
        self.background_view_ratio = self.view_width / self.view_height
        self.camera_view_ratio = self.camera_width / self.camera_height
        if self.background_view_ratio > self.camera_view_ratio:
            # The width of background_view is larger than the width of camera_view
            self.camera_view_height = self.view_height
            self.camera_view_width = int(self.view_height * self.camera_view_ratio)
        else:
            # The height of background_view is larger than the height of camera_view
            self.camera_view_width = self.view_width
            self.camera_view_height = int(self.view_width / self.camera_view_ratio)
        self.camera_view.place(relx=0.5, rely=0.5, height=self.camera_view_height, width=self.camera_view_width, anchor=CENTER)


    def gui_set(self):
        self.background_view.place(relwidth=1.0, relheight=1.0)


    # Debug Methods

    def screen_moved(self, event):
        self.pose_detection.simulate_body_point((event.x, event.y))