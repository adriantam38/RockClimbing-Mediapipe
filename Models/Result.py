import cv2
from Utilities.Constants import *
from Utilities.open_file import open_file

class Result:
    def __init__(self, path_id):
        self.path_id = path_id
        self.score = 0
        self.time = ''
        self.touched_good_points = []
        self.untouched_good_points = []
        self.touched_bad_points = []
        self.untouched_bad_points = []

    def evaluate(self, touched_good_points, untouched_good_points, touched_bad_points, untouched_bad_points, alphabet_list):
        if alphabet_list is None:
            self.add_points = len(set(touched_good_points)) * TOUCHED_GOOD_POINT_WEIGHT
            self.minus_points = len(set(untouched_good_points)) * UNTOUCHED_GOOD_POINT_WEIGHT + len(
                set(touched_bad_points)) * TOUCHED_BAD_POINT_WEIGHT
            self.score = self.add_points - self.minus_points
        else:
            self.add_points = 0
            self.minus_points = 0
            self.score = 0
        self.touched_good_points = touched_good_points
        self.untouched_good_points = untouched_good_points
        self.touched_bad_points = touched_bad_points
        self.untouched_bad_points = untouched_bad_points
        self.alphabet_list = alphabet_list
        
    def update_time(self, time):
        self.time = time

    def get_path_id(self):
        return self.path_id

    def get_score(self):
        return self.add_points, self.minus_points, self.score

    def get_good_points(self):
        return len(self.touched_good_points), len(self.touched_good_points)+len(self.untouched_good_points)

    def get_bad_points(self):
        return len(self.touched_bad_points), len(self.touched_bad_points)+len(self.untouched_bad_points)

    def get_word(self):
        word = ''.join(str(alphabets[1][4]) for alphabets in self.alphabet_list)
        return word

    def get_time(self):
        return self.time

    def get_image_and_points(self):
        self.image = cv2.imread(open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{self.get_path_id()}.jpg"), -1)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        return self.image, self.touched_good_points, self.untouched_good_points, self.touched_bad_points, self.untouched_bad_points