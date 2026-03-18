import tkinter.messagebox

import i18n
import uuid
from Modules.SaveLoadModule import SaveLoadModule
from tkinter import *
from tkinter.simpledialog import askstring
from Models.ControlBarButton import ControlBarButton
from Models.Enums.View import VIEW
from Utilities.Constants import *

class PathsView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.title = ''
        self.buttons = {}

        self.selected_path_name = None

        self.path_listbox = Listbox(self, font=(FONT_FAMILY, HEADING_FONT_SIZE))
        self.path_listbox.bind("<Double-Button-1>", self.path_double_clicked)
        
        self.gui_set()


    # Navigation Methods

    def launch(self, is_settings=False, path_data=[], path_images=[]):
        self.save_load_module = SaveLoadModule()
        i18n.set('locale', self.save_load_module.load_settings().locale)
        self.is_settings = is_settings
        self.path_images = path_images
        self.rename_paths = []

        self.buttons = {
            0: ControlBarButton("↑", self.up_btn_pressed),
            1: ControlBarButton("↓", self.down_btn_pressed),
            3: ControlBarButton(i18n.t('t.enter'), self.enter_btn_pressed)
        }

        if self.is_settings:
            self.path_data = path_data
            self.change_title(f"{i18n.t('t.select_path')} ({i18n.t('t.configuration')})")
            self.buttons[5] = ControlBarButton(i18n.t('t.add'), self.add_btn_pressed)
            self.buttons[6] = ControlBarButton(i18n.t('t.rename'), self.rename_btn_pressed)
            self.buttons[7] = ControlBarButton(i18n.t('t.delete'), self.delete_btn_pressed)
            self.buttons[9] = ControlBarButton(i18n.t('t.done'), lambda: self.navigate(VIEW.SETTINGS, path_data=self.path_data, rename_paths=self.rename_paths, path_images=self.path_images), THEME_COLOR_PURPLE)
        else:
            self.path_data = self.save_load_module.load_path_data()
            self.buttons[9] = ControlBarButton(i18n.t('t.home'), lambda: self.navigate(VIEW.HOME), THEME_COLOR_PURPLE)
            self.change_title(i18n.t('t.select_path'))

        self.change_buttons(self.buttons)
        self.gui_paths_update()


    # Button Methods

    def up_btn_pressed(self):
        if len(self.path_listbox.curselection()) != 0:
            next_listbox_index = self.path_listbox.curselection()[0] - 1
            if next_listbox_index >= 0 :
                self.path_listbox.selection_clear(0, END)
                self.path_listbox.selection_set(next_listbox_index)
        else:
            self.path_listbox.selection_set("end")


    def down_btn_pressed(self):
        if len(self.path_listbox.curselection()) != 0:
            next_listbox_index = self.path_listbox.curselection()[0] + 1
            if next_listbox_index < self.path_listbox.size():
                self.path_listbox.selection_clear(0, END)
                self.path_listbox.selection_set(next_listbox_index)
        else:
            self.path_listbox.selection_set(0)


    def enter_btn_pressed(self):
        self.selected_path_id, self.selected_path_name = self.get_selected_path_id_and_name()
        if self.selected_path_id is not None and self.selected_path_name is not None:
            points = self.create_point_list(self.selected_path_id)

            if self.is_settings:
                self.navigate(VIEW.CAMERA, is_settings=True, path_id=self.selected_path_id, path_name=self.selected_path_name, points=points, path_data=self.path_data, path_images=self.path_images)
            else:
                self.navigate(VIEW.CAMERA, is_game=True, path_id=self.selected_path_id, path_name=self.selected_path_name, points=points)


    def add_btn_pressed(self):
        new_path = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
        if len(self.path_data) > 0:
            for point in self.path_data:
                path_name = point[1]
                if path_name == new_path:
                    correct_path_name = False
                    break
                else:
                    correct_path_name = True
        else:
            correct_path_name = True
        if new_path is not None and new_path != '' and correct_path_name == True:
            self.navigate(VIEW.CAMERA, is_settings=True, path_id=uuid.uuid1(), path_name=new_path, points=[], path_data=self.path_data, path_images=self.path_images)
        elif new_path == '' or correct_path_name == False:
            tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
            self.add_btn_pressed()


    def delete_btn_pressed(self):
        self.selected_path_id, _ = self.get_selected_path_id_and_name()
        if self.selected_path_id is not None:
            new_path_data = []
            for row in self.path_data:
                if row[0] != self.selected_path_id:
                    new_path_data.append(row)
            self.path_data = new_path_data
            self.gui_paths_update()


    def rename_btn_pressed(self):
        self.selected_path_id, old_path_name = self.get_selected_path_id_and_name()
        if self.selected_path_id is not None:
            new_name = askstring(i18n.t('t.rename_path'), i18n.t('t.what_is_the_name_of_new_path?'))
            if len(self.path_data) > 0:
                for point in self.path_data:
                    path_name = point[1]
                    if path_name == new_name:
                        correct_path_name = False
                        break
                    else:
                        correct_path_name = True
            if new_name is not None and new_name != '' and correct_path_name == True:
                new_path_data = []
                for row in self.path_data:
                    if row[0] == self.selected_path_id:
                        new_path_data.append([self.selected_path_id, new_name, row[2], row[3], row[4], row[5], row[6], row[7]])
                    else:
                        new_path_data.append(row)
                self.path_data = new_path_data
                self.rename_paths.append((self.selected_path_name, new_name))
                self.gui_paths_update()
            elif new_name == '' or correct_path_name == False:
                tkinter.messagebox.showwarning(title=i18n.t('t.warning'), message=i18n.t('t.invalid_path'))
                self.rename_btn_pressed()


    def create_point_list(self, path_id):
        points = []
        for row in self.path_data:
            if row[0] == path_id:
                if row[4] == True:
                    points.append(( row[2], row[3], True, row[5], row[6], row[7]))
                else:
                    points.append(( row[2], row[3], False, row[5], row[6], row[7]))
        return points


    # Other Methods

    def path_double_clicked(self, _):
        self.enter_btn_pressed()        


    def get_selected_path_id_and_name(self):
        if len(self.path_listbox.curselection()) != 0:
            path_name = self.path_listbox.get(self.path_listbox.curselection()[0])
            path_id = ""
            for row in self.path_data:
                if path_name == row[1]:
                    path_id = row[0]
                    break
            return path_id, path_name
        else:
            return None, None


    # GUI Methods

    def gui_set(self):
        self.path_listbox.place(x=CONTROL_BAR_WIDTH/2, relx=0.3, relwidth=0.4, relheight=1.0)


    def gui_paths_update(self):
        self.path_listbox.delete(0, END)
        path_names = []
        for row in self.path_data:
            path_names.append(row[1])
        path_names = list(set(path_names))
        for path_name in path_names:
            self.path_listbox.insert(END, path_name)
