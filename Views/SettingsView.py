import i18n
import copy
from tkinter import *
from Models.Enums.Camera import CAMERA_ORIENTATION
from Models.Enums.View import VIEW
from Models.ControlBarButton import ControlBarButton
from Modules.PoseDetectionModule import PoseDetectionModule
from Modules.SoundModule import SoundModule
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *

class SettingsView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, change_keypad, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.navigate_without_stop_camera = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons
        self.change_keypad = change_keypad

        self.background_view_width = self.view_width * 0.7
        self.page = 0

        self.save_load_module = SaveLoadModule()

        self.background_view = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), fg='white', bg='black')
        self.camera_view = Label(self)
        self.label_view = Label(self, bg=THEME_COLOR_BLUE)

        self.danger_alert_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.sensitivity_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.change_language_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.camera_number_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.camera_orientation_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)        
        self.camera_mirror_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.distance_calibration_actual_value_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.ground_calibration_actual_position_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        self.reverse_keypad_label = Label(self.label_view, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)
        
        self.gui_set()


    # Navigation Methods

    def launch(self, path_data=None, rename_paths=[], path_images=[]):
        self.path_images = path_images
        self.page = 0

        self.old_settings = self.save_load_module.load_settings()
        self.new_settings = copy.deepcopy(self.old_settings)
        i18n.set('locale', self.old_settings.locale)
            
        self.restart_camera()
        if path_data is not None:
            self.path_data = path_data
        else:
            self.path_data = self.save_load_module.load_path_data()

        self.rename_paths = rename_paths
        self.gui_update()


    def navigate(self, view, **kwargs):
        if self.is_camera_detected:
            self.pose_detection.stop_camera_input()
        self.navigate_without_stop_camera(view, **kwargs)


    def restart_camera(self, camera_number=None):
        try:
            self.pose_detection.stop_camera_input()
        except:
            print("")
        self.pose_detection = PoseDetectionModule()
        if camera_number is not None:
            self.is_camera_detected, camera_width, camera_height = self.pose_detection.test_and_set_camera_resolutions(camera_number)
        else:
            self.is_camera_detected, camera_width, camera_height = self.pose_detection.test_and_set_camera_resolutions(self.new_settings.camera_number)
        if self.is_camera_detected:
            self.camera_width, self.camera_height = camera_width, camera_height
            self.gui_camera_view_set()
            self.pose_detection.set_camera_input(self.camera_view, self.camera_view_width, self.camera_view_height)
            self.pose_detection.cameraInput()
        return self.is_camera_detected


    # Button Actions (Page 0)

    def danger_alert_btn_pressed(self):
        self.new_settings.update(danger_alert=not self.new_settings.danger_alert)
        self.gui_update()


    def test_sound_btn_pressed(self):
        SoundModule().test_sound()


    def set_game_path_btn_pressed(self):
        self.navigate(VIEW.PATHS, is_settings=True, path_data=self.path_data)


    def sensitivity_btn_pressed(self):
        if self.new_settings.sensitivity == 0:
            self.new_settings.sensitivity = 1
        elif self.new_settings.sensitivity == 1:
            self.new_settings.sensitivity = 2
        elif self.new_settings.sensitivity == 2:
            self.new_settings.sensitivity = 3
        elif self.new_settings.sensitivity == 3:
            self.new_settings.sensitivity = 4
        elif self.new_settings.sensitivity == 4:
            self.new_settings.sensitivity = 0
        self.gui_update()


    def change_language_btn_pressed(self):
        if self.new_settings.locale == 'en':
            self.new_settings.locale = 'ch'
        else:
            self.new_settings.locale = 'en'
        i18n.set('locale', self.new_settings.locale)
        self.gui_update()


    # Button Actions (Page 1)

    def change_camera_btn_pressed(self):
        if not self.is_camera_detected:
            if self.restart_camera(0):
                self.new_settings.update(camera_number=0)
        else:
            if self.restart_camera(self.new_settings.camera_number+1):
                self.new_settings.update(camera_number=self.new_settings.camera_number+1)
            elif self.restart_camera(0):
                self.new_settings.update(camera_number=0)
        self.gui_update()


    def camera_orientation_btn_pressed(self):
        if self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.LANDSCAPE:
            self.new_settings.update(camera_orientation_mode=CAMERA_ORIENTATION.LEFT)
        elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
            self.new_settings.update(camera_orientation_mode=CAMERA_ORIENTATION.INVERTED)
        elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
            self.new_settings.update(camera_orientation_mode=CAMERA_ORIENTATION.RIGHT)
        elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
            self.new_settings.update(camera_orientation_mode=CAMERA_ORIENTATION.LANDSCAPE)
        self.gui_camera_view_rotate()
        self.gui_update()


    def mirror_camera_btn_pressed(self):
        self.new_settings.update(mirror_camera=not self.new_settings.mirror_camera)
        self.gui_update()


    def distance_calibration_btn_pressed(self):
        self.new_settings.update(distance_calibration_shown=True)
        self.gui_update()


    def distance_calibration_up_btn_pressed(self):
        self.new_settings.update(distance_calibration_actual_value=self.new_settings.distance_calibration_actual_value+0.05)
        self.gui_update()


    def distance_calibration_down_btn_pressed(self):
        if self.new_settings.distance_calibration_actual_value > 0.05:
            self.new_settings.update(distance_calibration_actual_value=self.new_settings.distance_calibration_actual_value-0.05)
        self.gui_update()

    def ground_calibration_up_btn_pressed(self):
        self.pose_detection.update_ground_level()
        if self.pose_detection.ground_screen_ratio > 0.01:
            self.new_settings.update(ground_ratio_calibration_actual_value=self.new_settings.ground_ratio_calibration_actual_value-0.1)
        self.gui_update()

    def ground_calibration_down_btn_pressed(self):
        self.pose_detection.update_ground_level()
        if self.pose_detection.ground_screen_ratio < 1:
            self.new_settings.update(ground_ratio_calibration_actual_value=self.new_settings.ground_ratio_calibration_actual_value+0.1)
        self.gui_update()


    def distance_calibration_confirm_btn_pressed(self):
        self.new_settings.update(distance_calibration_shown=False)
        self.gui_update()

    
    def reverse_keypad_btn_pressed(self):
        self.new_settings.update(reverse_keypad=not self.new_settings.reverse_keypad)
        self.change_keypad(self.new_settings.reverse_keypad)
        self.gui_update()


    def toggle_page_btn_pressed(self):
        if self.page == 0:
            self.page = 1
        elif self.page == 1:
            self.page = 0
        self.gui_update()


    def cancel_btn_pressed(self):
        self.save_load_module.save_settings(self.old_settings)
        self.change_keypad(self.old_settings.reverse_keypad)
        self.navigate(VIEW.HOME)


    def confirm_btn_pressed(self):
        self.save_load_module.save_settings(self.new_settings)
        self.save_load_module.save_path_data(self.path_data, self.rename_paths, self.path_images)
        self.change_keypad(self.new_settings.reverse_keypad)
        self.navigate(VIEW.HOME)


    # GUI Methods

    def gui_camera_view_set(self):
        if self.is_camera_detected:
            self.background_view_ratio = self.background_view_width / self.view_height
            self.camera_view_ratio = self.camera_width / self.camera_height
            if self.background_view_ratio > self.camera_view_ratio:
                # The width of background_view is larger than the width of camera_view
                self.camera_view_height = int(self.view_height)
                self.camera_view_width = int(self.view_height * self.camera_view_ratio)
            else:
                # The height of background_view is larger than the height of camera_view
                self.camera_view_width = int(self.background_view_width)
                self.camera_view_height = int(self.background_view_width / self.camera_view_ratio)
            self.camera_view.place(x=self.background_view_width/2, rely=0.5, height=self.camera_view_height, width=self.camera_view_width, anchor=CENTER)


    def gui_camera_view_rotate(self):
        if self.is_camera_detected:
            self.camera_width, self.camera_height = self.camera_height, self.camera_width
            self.gui_camera_view_set()
            self.pose_detection.update_camera_view(self.camera_view, self.camera_view_width, self.camera_view_height)


    def gui_set(self):
        self.background_view.place(width=self.background_view_width, relheight=1.0)
        self.label_view.place(x=self.background_view_width, width=self.view_width-self.background_view_width, relheight=1.0)


    def gui_update(self):
        self.gui_clear()

        self.pose_detection.update_settings(self.new_settings)

        if not self.is_camera_detected:

            self.camera_view.place_forget()
            self.background_view.config(text=i18n.t('t.no_camera_is_detected'))
            self.camera_number_label.place_forget()
            self.buttons[0] = ControlBarButton(i18n.t('t.detect_camera'), self.change_camera_btn_pressed)
            self.buttons[1] = ControlBarButton(i18n.t('t.test_sound'), self.test_sound_btn_pressed)
            self.change_language_label.config(text=i18n.t('t.change_language'))
            self.change_language_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
            self.buttons[2] = ControlBarButton(i18n.t('t.new_language'), self.change_language_btn_pressed)
            self.buttons[8] = ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)

        elif self.new_settings.distance_calibration_shown:

            actual_value_string = "{:.2f}".format(self.new_settings.distance_calibration_actual_value)
            self.distance_calibration_actual_value_label.config(text=f"""{i18n.t('t.actual_distance_of_the_yellow_line')} {actual_value_string} {i18n.t('t.metre')}""")
            self.ground_calibration_actual_position_label.config(text="actual ground level")
            self.distance_calibration_actual_value_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT*2, anchor=N)
            self.ground_calibration_actual_position_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*2, height=CONTROL_BAR_BUTTON_HEIGHT*2, anchor=N)
            self.buttons[0] = ControlBarButton("↑", self.distance_calibration_up_btn_pressed)
            self.buttons[1] = ControlBarButton("↓", self.distance_calibration_down_btn_pressed)
            self.buttons[2] = ControlBarButton("↑", self.ground_calibration_up_btn_pressed)
            self.buttons[3] = ControlBarButton("↓", self.ground_calibration_down_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.distance_calibration_confirm_btn_pressed, THEME_COLOR_PURPLE)

        else:

            if self.page == 0:

                self.danger_alert_label.config(text=f"{i18n.t('t.danger_alert')}")
                self.danger_alert_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.new_settings.danger_alert:
                    self.buttons[0] = ControlBarButton(i18n.t('t.yes'), self.danger_alert_btn_pressed)
                else:
                    self.buttons[0] = ControlBarButton(i18n.t('t.no'), self.danger_alert_btn_pressed)
                self.buttons[1] = ControlBarButton(i18n.t('t.test_sound'), self.test_sound_btn_pressed)
                self.buttons[2] = ControlBarButton(i18n.t('t.set_game_path'), self.set_game_path_btn_pressed)
                self.sensitivity_label.config(text=i18n.t('t.sensitivity'))
                self.sensitivity_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*3, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.new_settings.sensitivity == 0:
                    self.buttons[3] = ControlBarButton(i18n.t('t.very_low'), self.sensitivity_btn_pressed)
                elif self.new_settings.sensitivity == 1:
                    self.buttons[3] = ControlBarButton(i18n.t('t.low'), self.sensitivity_btn_pressed)
                elif self.new_settings.sensitivity == 2:
                    self.buttons[3] = ControlBarButton(i18n.t('t.medium'), self.sensitivity_btn_pressed)
                elif self.new_settings.sensitivity == 3:
                    self.buttons[3] = ControlBarButton(i18n.t('t.high'), self.sensitivity_btn_pressed)
                elif self.new_settings.sensitivity == 4:
                    self.buttons[3] = ControlBarButton(i18n.t('t.very_high'), self.sensitivity_btn_pressed)
                self.change_language_label.config(text=i18n.t('t.change_language'))
                self.change_language_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*4, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                self.buttons[4] = ControlBarButton(i18n.t('t.new_language'), self.change_language_btn_pressed)
                self.buttons[7] = ControlBarButton(i18n.t('t.next_page'), self.toggle_page_btn_pressed)

            elif self.page == 1:

                self.camera_number_label.config(text=f"{i18n.t('t.camera_number')}: {self.new_settings.camera_number}")
                self.camera_number_label.place(relx=0.5, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                self.buttons[0] = ControlBarButton(i18n.t('t.change_camera'), self.change_camera_btn_pressed)

                self.camera_orientation_label.config(text=f"{i18n.t('t.camera_orientation')}")
                self.camera_orientation_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.LANDSCAPE:
                    self.buttons[1] = ControlBarButton(i18n.t('t.landscape'), self.camera_orientation_btn_pressed)
                elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.LEFT:
                    self.buttons[1] = ControlBarButton(i18n.t('t.left'), self.camera_orientation_btn_pressed)
                elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.INVERTED:
                    self.buttons[1] = ControlBarButton(i18n.t('t.inverted'), self.camera_orientation_btn_pressed)
                elif self.new_settings.camera_orientation_mode == CAMERA_ORIENTATION.RIGHT:
                    self.buttons[1] = ControlBarButton(i18n.t('t.right'), self.camera_orientation_btn_pressed)
                
                self.camera_mirror_label.config(text=f"{i18n.t('t.mirror_camera')}")
                self.camera_mirror_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*2, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.new_settings.mirror_camera:
                    self.buttons[2] = ControlBarButton(i18n.t('t.yes'), self.mirror_camera_btn_pressed)
                else:
                    self.buttons[2] = ControlBarButton(i18n.t('t.no'), self.mirror_camera_btn_pressed)

                self.buttons[3] = ControlBarButton(i18n.t('t.distance_calibration'), self.distance_calibration_btn_pressed)

                self.reverse_keypad_label.config(text=f"{i18n.t('t.reverse_keypad')}")
                self.reverse_keypad_label.place(relx=0.5, y=CONTROL_BAR_BUTTON_HEIGHT*4, height=CONTROL_BAR_BUTTON_HEIGHT, anchor=N)
                if self.new_settings.reverse_keypad:
                    self.buttons[4] = ControlBarButton(i18n.t('t.yes'), self.reverse_keypad_btn_pressed)
                else:
                    self.buttons[4] = ControlBarButton(i18n.t('t.no'), self.reverse_keypad_btn_pressed)

                self.buttons[7] = ControlBarButton(i18n.t('t.previous_page'), self.toggle_page_btn_pressed)

            self.buttons[8] = ControlBarButton(i18n.t('t.cancel'), self.cancel_btn_pressed, THEME_COLOR_PINK)
            self.buttons[9] = ControlBarButton(i18n.t('t.confirm'), self.confirm_btn_pressed, THEME_COLOR_PURPLE)

        self.change_title(i18n.t('t.settings'))
        self.change_buttons(self.buttons)


    def gui_clear(self):
        self.background_view.config(text='')
        self.danger_alert_label.place_forget()
        self.sensitivity_label.place_forget()
        self.change_language_label.place_forget()
        self.camera_number_label.place_forget()
        self.camera_orientation_label.place_forget()
        self.camera_mirror_label.place_forget()
        self.distance_calibration_actual_value_label.place_forget()
        self.ground_calibration_actual_position_label.place_forget()
        self.reverse_keypad_label.place_forget()
        self.buttons = {}