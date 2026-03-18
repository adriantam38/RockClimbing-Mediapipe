import playsound
from Utilities.Constants import SOUND_FILES_LOCATION
from Utilities.open_file import open_file

class SoundModule:

    def test_sound(self):
        playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}test_sound.wav"), False)

    def countdown(self):
        playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}countdown.wav"), False)

    def good_point(self):
        playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}good_point.wav"), False)

    def bad_point(self):
        playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}bad_point.mp3"), False)

    def danger_alert(self):
        playsound.playsound(open_file(f"{SOUND_FILES_LOCATION}danger_alert.wav"), False)
