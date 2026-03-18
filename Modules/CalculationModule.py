import cv2
import numpy as np
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *

class CalculationModule:
    
    def __init__(self, image, vid_player=False):
        self.image = image.copy()
        self.image_with_drawing = image.copy()
        self.settings = SaveLoadModule().load_settings()
        self.clickedPoints = []
        if vid_player:
            self.dot_color = (DOT_COLOR[2], DOT_COLOR[1], DOT_COLOR[0])
            self.angle_color = (ANGLE_COLOR[2], ANGLE_COLOR[1], ANGLE_COLOR[0])
        else:
            self.dot_color = DOT_COLOR
            self.angle_color = ANGLE_COLOR

    def findAngleBetweenThreePoints(self, pt1, pt2, pt3):
        a = np.array([pt1[0], pt1[1]])
        b = np.array([pt2[0], pt2[1]])
        c = np.array([pt3[0], pt3[1]])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def findAngleBetweenLinesAndxAxis(self, pt1, pt2):
        a = np.array([pt1[0], pt1[1]])
        b = np.array([pt2[0], pt2[1]])
        c = np.array([10000, pt2[1]])
        ba = a - b
        bc = c - b
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        if pt1[1] < pt2[1]:
            angle = -angle
        if angle < 0:
            angle = angle + np.pi * 2
        return np.degrees(angle)

    def findDistanceBetweenTwoPoints(self, pt1, pt2):
        self.pixelsOnScreen = np.sqrt(np.square(pt1[0]-pt2[0]) + np.square(pt1[1]-pt2[1]))
        self.distance_factor = self.settings.distance_calibration_actual_value / CALIBRATION_PIXELS
        self.distance = self.pixelsOnScreen * self.distance_factor
        return self.distance

    def drawAngle(self):
        fromAngle = self.findAngleBetweenLinesAndxAxis(self.clickedPoints[0], self.clickedPoints[1])
        toAngle = self.findAngleBetweenLinesAndxAxis(self.clickedPoints[2], self.clickedPoints[1])
        if abs(toAngle-fromAngle) > 180:
            if toAngle > fromAngle:
                toAngle -= 360
            else:
                fromAngle -= 360
        cv2.ellipse(self.image_with_drawing, self.clickedPoints[1], (DOT_RADIUS*4, DOT_RADIUS*4), 0, fromAngle, toAngle, self.angle_color, -1)

    def calculate(self, x, y):
        angle = None
        distance = None
        self.clickedPoints.append((x, y))
        cv2.circle(self.image_with_drawing, (x, y), DOT_RADIUS, self.dot_color, -1)
        if len(self.clickedPoints) == 2:
            cv2.line(self.image_with_drawing, self.clickedPoints[0], self.clickedPoints[1], self.dot_color, int(DOT_RADIUS/3))
            distance = self.findDistanceBetweenTwoPoints(self.clickedPoints[0], self.clickedPoints[1])
        if len(self.clickedPoints) == 3:
            cv2.line(self.image_with_drawing, self.clickedPoints[1], self.clickedPoints[2], self.dot_color, int(DOT_RADIUS/3))
            angle = self.findAngleBetweenThreePoints(self.clickedPoints[0], self.clickedPoints[1], self.clickedPoints[2])
            self.drawAngle()
        if len(self.clickedPoints) > 3:
            self.clearAllDots()
        return self.image_with_drawing, distance, angle

    def clearAllDots(self):
        self.clickedPoints.clear()
        self.image_with_drawing = self.image.copy()
        return self.image_with_drawing
