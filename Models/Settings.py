from Models.Enums.Camera import CAMERA_ORIENTATION
from Utilities.Constants import *

class Settings:

    # Default Settings
    def __init__(self):
        self.danger_alert = True
        self.camera_number = 0
        self.camera_orientation_mode = CAMERA_ORIENTATION.LANDSCAPE
        self.mirror_camera = False
        self.distance_calibration_shown = False
        self.distance_calibration_actual_value = 1.0
        self.ground_ratio_calibration_actual_value = 0.8
        self.reverse_keypad = False
        self.locale = 'ch'
        self.sensitivity = 2

    def update(self, danger_alert=None, camera_number=None, camera_orientation_mode=None, mirror_camera=None, distance_calibration_shown=None, distance_calibration_actual_value=None, ground_ratio_calibration_actual_value=None, reverse_keypad=None, locale=None, sensitivity=None):
        if danger_alert is not None:
            self.danger_alert = danger_alert
        if camera_number is not None:
            self.camera_number = camera_number
        if camera_orientation_mode is not None:
            self.camera_orientation_mode = camera_orientation_mode
        if mirror_camera is not None:
            self.mirror_camera = mirror_camera
        if distance_calibration_shown is not None:
            self.distance_calibration_shown = distance_calibration_shown
        if distance_calibration_actual_value is not None:
            self.distance_calibration_actual_value = distance_calibration_actual_value
        if ground_ratio_calibration_actual_value is not None:
            self.ground_ratio_calibration_actual_value = ground_ratio_calibration_actual_value
        if reverse_keypad is not None:
            self.reverse_keypad = reverse_keypad
        if locale is not None:
            self.locale = locale
        if sensitivity is not None:
            self.sensitivity = sensitivity

    def convert_to_variables(self):
        variables = {
            MIRROR_CAMERA: self.mirror_camera,
            CAMERA_NUMBER: self.camera_number,
            CAMERA_ORIENTATION_MODE: self.camera_orientation_mode,
            DANGER_ALERT: self.danger_alert,
            DISTANCE_CALIBRATION_SHOWN: self.distance_calibration_shown,
            DISTANCE_CALIBRATION_ACTUAL_VALUE: self.distance_calibration_actual_value,
            GROUND_RATIO_CALIBRATION_ACTUAL_VALUE: self.ground_ratio_calibration_actual_value,
            REVERSE_KEYPAD: self.reverse_keypad,
            LOCALE: self.locale,
            SENSITIVITY: self.sensitivity
        }
        return variables
    
    def convert_from(self, variables):
        self.update(
            danger_alert=variables[DANGER_ALERT],
            camera_number=variables[CAMERA_NUMBER],
            camera_orientation_mode=variables[CAMERA_ORIENTATION_MODE],
            mirror_camera=variables[MIRROR_CAMERA],
            distance_calibration_shown=variables[DISTANCE_CALIBRATION_SHOWN],
            distance_calibration_actual_value=variables[DISTANCE_CALIBRATION_ACTUAL_VALUE],
            ground_ratio_calibration_actual_value=variables[GROUND_RATIO_CALIBRATION_ACTUAL_VALUE],
            reverse_keypad=variables[REVERSE_KEYPAD],
            locale=variables[LOCALE],
            sensitivity=variables[SENSITIVITY]
        )
