import i18n
import PIL.Image, PIL.ImageTk
from tkinter import *
from Models.ControlBarButton import ControlBarButton
from Models.Enums.View import VIEW
from Modules.SaveLoadModule import SaveLoadModule
from Utilities.Constants import *
from Utilities.open_file import open_file

class HomeView(Frame):

    def __init__(self, *arg, view_width, view_height, navigate, change_title, change_buttons, exit, **kwargs):
        Frame.__init__(self, *arg, **kwargs)
        
        self.view_width = view_width
        self.view_height = view_height
        self.change_title = change_title
        self.change_buttons = change_buttons

        self.navigate = navigate
        self.exit = exit

        self.gui_calculate_values()

        self.logo_image = PIL.Image.open(open_file(f"{IMAGE_FILES_LOCATION}Logo.png")).resize((self.logo_image_size, self.logo_image_size), PIL.Image.ANTIALIAS)
        self.logo_image = PIL.ImageTk.PhotoImage(self.logo_image)
        self.logo_label = Label(self, image=self.logo_image, bg=THEME_COLOR_BLUE)
        
        self.name_label = Label(self, font=(FONT_FAMILY, TITLE_FONT_SIZE), bg=THEME_COLOR_BLUE)

        self.gui_set()


    # Navigation Methods

    def launch(self):
        i18n.set('locale', SaveLoadModule().load_settings().locale)
        self.change_title(i18n.t('t.home'))
        self.buttons = {
            0: ControlBarButton(i18n.t('t.camera'), lambda: self.navigate(VIEW.CAMERA)),
            1: ControlBarButton(i18n.t('t.game'), lambda: self.navigate(VIEW.PATHS)),
            2: ControlBarButton(i18n.t('t.recordings'), lambda: self.navigate(VIEW.RECORDINGS)),
            8: ControlBarButton(i18n.t('t.settings'), lambda: self.navigate(VIEW.SETTINGS)),
            9: ControlBarButton(i18n.t('t.exit_program'), lambda: self.exit(), THEME_COLOR_PINK)
        }
        self.change_buttons(self.buttons)
        self.name_label.config(text=f"{i18n.t('t.school_name')}\n{i18n.t('t.system_name')}")


    # GUI Methods

    def gui_calculate_values(self):
        self.logo_image_size = int(min(self.view_width, self.view_height)/3)

    def gui_set(self):
        self.logo_label.place(rely=0.1, relwidth=1.0, height=self.logo_image_size)
        self.name_label.place(rely=0.5, relwidth=1.0, relheight=0.3)
