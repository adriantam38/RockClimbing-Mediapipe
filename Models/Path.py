import numpy as np
from Models.Result import Result
from Modules.SaveLoadModule import SaveLoadModule
from Modules.SoundModule import SoundModule
from Utilities.Constants import *

class Path:
    def __init__(self, path_id, points, average_time_between_frames):
        self.update_points(points)
        self.touching_good_points = []
        self.touching_bad_points = []  
        self.touched_good_points = []
        self.touched_bad_points = []
        self.touched_points_reset = []
        self.player_input_alphabets = []
        self.good_points_touch_order = 0
        self.bad_points_touch_order = 0
        self.result = Result(path_id)
        self.sound_module = SoundModule()
        self.load_sensitivity(average_time_between_frames)


    def load_sensitivity(self, average_time_between_frames):
        sensitivity = SaveLoadModule().load_settings().sensitivity
        if sensitivity == 0:
            self.touch_distance = 0.01
            self.count_second = 4
        elif sensitivity == 1:
            self.touch_distance = 0.02
            self.count_second = 3.5
        elif sensitivity == 2:
            self.touch_distance = 0.03
            self.count_second = 3
        elif sensitivity == 3:
            self.touch_distance = 0.04
            self.count_second = 2.5
        elif sensitivity == 4:
            self.touch_distance = 0.05
            self.count_second = 2
        self.count_threshold = int(self.count_second / average_time_between_frames)
        if DEBUG_MODE:
            print("count_threshold:", self.count_threshold)
            print("count_second:", self.count_second)
            print("touch_distance_pixel:", self.touch_distance)


    def evaluate_body_point(self, body_point):
        untouched_good_points = list(set(self.good_points) - set(self.touched_good_points))
        for point in untouched_good_points:
            if point[5] == 1:
                if point[3] == self.good_points_touch_order:
                    if self.distance_between(body_point, point) < self.touch_distance:
                        # Append this point (with duplicates)
                        self.touching_good_points.append(point)
                        # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                        if self.touching_good_points.count(point) > self.count_threshold:
                            self.sound_module.good_point()
                            self.touched_good_points.append(point)
                            self.good_points_touch_order += 1
                            self.touching_good_points = list(filter((point).__ne__, self.touching_good_points))

            elif point[5] == 2:
                if self.distance_between(body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_good_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_good_points.count(point) > self.count_threshold:
                        self.sound_module.good_point()
                        self.touched_good_points.append(point)
                        self.touching_good_points = list(filter((point).__ne__, self.touching_good_points))
                        self.player_input_alphabets.append((self.good_points_touch_order, point))
                        self.good_points_touch_order += 1

                for point in self.touched_good_points:
                    if self.distance_between(body_point, point) > self.touch_distance:
                        self.touched_points_reset.append(point)
                        if self.touched_points_reset.count(point) > self.count_threshold * 10:
                            self.touched_good_points.remove(point)
                            self.touched_points_reset = list(filter((point).__ne__, self.touched_points_reset))


            else:
                if self.distance_between(body_point, point) < self.touch_distance:
                    # Append this point (with duplicates)
                    self.touching_good_points.append(point)
                    # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                    if self.touching_good_points.count(point) > self.count_threshold:
                        self.sound_module.good_point()
                        self.touched_good_points.append(point)
                        self.touching_good_points = list(filter((point).__ne__, self.touching_good_points))



        untouched_bad_points = list(set(self.bad_points) - set(self.touched_bad_points))
        for point in untouched_bad_points:
            if self.distance_between(body_point, point) < self.touch_distance:
                # Append this point (with duplicates)
                self.touching_bad_points.append(point)
                # If this point exceed count_threshold in touching_list, add this point to touched_list (without duplicates)
                if self.touching_bad_points.count(point) > self.count_threshold:
                    self.sound_module.bad_point()
                    self.touched_bad_points.append(point)
                    self.touching_bad_points = list(filter((point).__ne__, self.touching_bad_points))


    def distance_between(self, pt1, pt2):
        return np.sqrt(np.square(pt1[0]-pt2[0]) + np.square(pt1[1]-pt2[1]))


    def evaluate_result(self):
        if self.good_points[0][5] == 2:
            self.result.evaluate(0,0,0,0,self.player_input_alphabets)
        else:
            untouched_bad_points = list(set(self.bad_points) - set(self.touched_bad_points))
            untouched_good_points = list(set(self.good_points) - set(self.touched_good_points))
            self.result.evaluate(self.touched_good_points, untouched_good_points, self.touched_bad_points,
                                 untouched_bad_points,None)
        return self.result


    # Settings Method

    def update_points(self, points):
        self.points = points
        self.good_points = []
        self.bad_points = []
        print(points)
        for point in points:
            if point[2] == True:
                self.good_points.append((point[0], point[1], point[2], point[3], point[4], point[5]))
            else:
                self.bad_points.append((point[0], point[1], point[2], point[3], point[4], point[5]))