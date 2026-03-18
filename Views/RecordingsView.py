import os
import i18n
from tkinter import *
from datetime import *
from Models.ControlBarButton import ControlBarButton
from Models.Enums.View import VIEW
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *
from Utilities.open_file import open_file

class RecordingsView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.navigate = navigate
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.selected_file = None
        self.date = datetime.now()
        
        self.date_label = Label(self, font=(FONT_FAMILY, SUBTITLE_FONT_SIZE), text=self.date.strftime("%Y-%m-%d"), bg=THEME_COLOR_BLUE)
        self.scrollbar = Scrollbar(self)
        self.file_listbox = Listbox(self, yscrollcommand=self.scrollbar.set, font=(FONT_FAMILY, HEADING_FONT_SIZE))
        self.file_listbox.bind("<Double-Button-1>", self.file_double_clicked)
        self.scrollbar.config(command = self.file_listbox.yview)

        self.gui_set()


    # Navigation Methods

    def launch(self):
        i18n.set('locale', SaveLoadModule().load_settings().locale)
        self.fetch_file()
        self.change_title(i18n.t('t.recordings'))
        self.buttons = {
            0: ControlBarButton(i18n.t('t.previous_day'), self.previous_btn_pressed),
            1: ControlBarButton(i18n.t('t.today'), self.today_btn_pressed),
            2: ControlBarButton(i18n.t('t.next_day'), self.next_btn_pressed),
            3: ControlBarButton("↑", self.up_btn_pressed),
            4: ControlBarButton("↓", self.down_btn_pressed),
            5: ControlBarButton(i18n.t('t.play'), self.play_btn_pressed),
            6: ControlBarButton(i18n.t('t.data'), self.data_btn_pressed),
            7: ControlBarButton(i18n.t('t.delete'), self.delete_btn_pressed),
            9: ControlBarButton(i18n.t('t.home'), lambda: self.navigate(VIEW.HOME), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)
        

    def fetch_file(self):
        self.file_listbox.delete(0, END)
        files = os.listdir(path=open_file(f"{VIDEO_FILES_LOCATION}"))
        for file in files:
            file_date = file[9:13] + '-' + file[13:15] + '-' + file[15:17]
            file_time = file[18:20] + ':' + file[20:22] + ':' + file[22:24]
            if file_date == self.date.strftime("%Y-%m-%d") and file.endswith('.mp4'):
                display_name = "{:<12}{:<8}".format(file_date, file_time)
                self.file_listbox.insert(END, display_name)     


    # Button Actions

    def previous_btn_pressed(self):
        self.date -= timedelta(days=1)
        self.date_label.config(text=self.date.strftime("%Y-%m-%d"))
        self.fetch_file()

    def today_btn_pressed(self):
        self.date = datetime.now()
        self.date_label.config(text=self.date.strftime("%Y-%m-%d"))
        self.fetch_file()

    def next_btn_pressed(self):
        self.date += timedelta(days=1)
        self.date_label.config(text=self.date.strftime("%Y-%m-%d"))
        self.fetch_file()

    def up_btn_pressed(self):
        if len(self.file_listbox.curselection()) != 0:
            next_listbox_index = self.file_listbox.curselection()[0] - 1
            if next_listbox_index >= 0 :
                self.file_listbox.selection_clear(0, END)
                self.file_listbox.selection_set(next_listbox_index)
        else:
            self.file_listbox.selection_set("end")

    def down_btn_pressed(self):
        if len(self.file_listbox.curselection()) != 0:
            next_listbox_index = self.file_listbox.curselection()[0] + 1
            if next_listbox_index < self.file_listbox.size():
                self.file_listbox.selection_clear(0, END)
                self.file_listbox.selection_set(next_listbox_index)
        else:
            self.file_listbox.selection_set(0)

    def play_btn_pressed(self):
        video_title, self.selected_file = self.get_selected_file()
        if self.selected_file is not None:
            file_path = open_file(f"{VIDEO_FILES_LOCATION}") + self.selected_file + ".mp4"
            self.navigate(VIEW.VIDEO, file_path=file_path, video_title=video_title)

    def data_btn_pressed(self):
        _, self.selected_file = self.get_selected_file()
        if self.selected_file is not None:
            file_path = open_file(f"{VIDEO_FILES_LOCATION}") + self.selected_file + ".csv"
            if os.path.exists(file_path):
                os.system(f'start {file_path}')
        
    def delete_btn_pressed(self):
        _, self.selected_file = self.get_selected_file()
        if self.selected_file is not None:
            for ext in [".mp4", ".csv"]:
                exact_file_name = open_file(f"{VIDEO_FILES_LOCATION}") + self.selected_file + ext
                if os.path.exists(exact_file_name):
                    os.remove(exact_file_name)
            self.fetch_file()


    # Other Methods

    def file_double_clicked(self, _):
        self.play_btn_pressed()

    def get_selected_file(self):
        if len(self.file_listbox.curselection()) != 0:
            video_title = self.file_listbox.get(self.file_listbox.curselection()[0])
            selected_file = 'pose_test' + video_title[0:4] + video_title[5:7] + video_title[8:10] + '-' + video_title[12:14] + video_title[15:17] + video_title[18:20]
            return video_title, selected_file
        else:
            return None, None


    # GUI Methods

    def gui_set(self):
        self.date_label.place(relx=0.8, y=CONTROL_BAR_BUTTON_HEIGHT, relwidth=0.2, height=CONTROL_BAR_BUTTON_HEIGHT)
        self.file_listbox.place(relx=0.3, relwidth=0.4, relheight=1.0)
        self.scrollbar.place(relx=0.7, width=20, relheight=1.0)
