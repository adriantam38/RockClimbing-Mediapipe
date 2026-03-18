import pickle
import os
import cv2
import pandas as pd
from Models.Settings import Settings
from Utilities.Constants import *
from Utilities.open_file import open_file

class SaveLoadModule:
    
    def __init__(self):
        self.settings = Settings()
        self.path_data = []
        self.path_images = []


    def load_settings(self):
        try:
            with open( open_file(f"{SETTINGS_FILE_LOCATION}Settings.pkl"), 'rb') as file:
                variables = pickle.load(file)
                self.settings.convert_from(variables)
        except:
            self.save_settings(self.settings)
        return self.settings


    def save_settings(self, settings):
        variables = settings.convert_to_variables()
        with open( open_file(f"{SETTINGS_FILE_LOCATION}Settings.pkl"), 'wb') as file:
            pickle.dump(variables, file)
        self.settings = settings


    def load_path_data(self):
        try:
            df = pd.read_csv( open_file(PATH_FILE_LOCATION), usecols=['path_id', 'path_name', 'x', 'y', 'is_good_point', 'point_sequence', 'alphabet', 'gamemode'], keep_default_na=False).sort_values(by=['path_id'])
            self.path_data = df.values.tolist()
        except:
            self.save_path_data(self.path_data)
        return self.path_data


    def save_path_data(self, path_data, rename_paths=[], path_images=[]):
        data = []
        for row in path_data:
            data.append(row)

        if len(data) > 0:
            df = pd.DataFrame(data, columns=['path_id', 'path_name', 'x', 'y', 'is_good_point', 'point_sequence', 'alphabet', 'gamemode'])
            df.to_csv( open_file(PATH_FILE_LOCATION) )
        else:
            df = pd.DataFrame([['','','','','','','','']], columns=['path_id', 'path_name', 'x', 'y', 'is_good_point', 'point_sequence', 'alphabet', 'gamemode'])
            # df = pd.read_csv( open_file(PATH_FILE_LOCATION), usecols=['path_id', 'path_name', 'x', 'y', 'is_good_point', 'point_sequence', 'alphabet'])
            df = df[df.path_id != '']
            df.to_csv( open_file(PATH_FILE_LOCATION) )

        # Save path images
        for image in path_images:
            cv2.imwrite(open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{image[0]}.jpg"), image[1])
        
        # Delete old files
        old_path_ids = []
        for row in self.path_data:
            old_path_ids.append(row[0])
        old_path_ids = list(set(old_path_ids))
        
        new_path_ids = []
        for row in path_data:
            new_path_ids.append(row[0])
        new_path_ids = list(set(new_path_ids))

        deleted_path_ids = list(set(old_path_ids) - set(new_path_ids))

        for row in deleted_path_ids:
            old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{row}.jpg")
            if os.path.exists(old_file_name):
                os.remove(old_file_name)

        # Rename files
        for rename_path in rename_paths:
            old_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path[0]}.jpg")
            new_file_name = open_file(f"{PATH_IMAGE_FILE_LOCATION}{CURRENT_PATH_SET}_{rename_path[1]}.jpg")
            if os.path.exists(old_file_name):
                os.rename(old_file_name, new_file_name)

        self.path_data = path_data