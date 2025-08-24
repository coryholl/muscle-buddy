# Copyright (C) 2025 Cory Jon Hollingsworth
#
# This file is part of the Pantheon suite.
#
# The Pantheon suite is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the Pantheon suite.  If not, see <https://www.gnu.org/licenses/>.
import os
import pathlib
from kivy.app import App
from kivy.core.audio import SoundLoader

__version__ = '1.0.0'

class Sound:
    """
    Sound
    purpose: provide a class for handling sound
    """
    sound_dict = {}

    def __init__(self, db):
        """
        __init__
        args: self - self object
            db - open database object
        purpose: create Sound object with database context
        """
        sound_files = db.get_sound_files()
        for sound_file_item in sound_files:
            sound_file_path = self.find_sound_file_path(sound_file_item['sound_file'])
            if sound_file_path:
                self.sound_dict[sound_file_item['sound_file']] = SoundLoader.load(sound_file_path)
                base_name = os.path.basename(sound_file_item['sound_file'])
                if base_name != sound_file_path:
                    self.sound_dict[base_name] = self.sound_dict[sound_file_item['sound_file']]

    def find_sound_file_path(self, file_path):
        """
        find_sound_file_path
        args: self - self object
            file_path - path of sound file to check
        purpose: determine what the correct path of a sound file is
        returns: correct path for mapping
        """
        sound_file_path = None
        expanded_file_path = os.path.expanduser(file_path)
        if os.path.exists(expanded_file_path):
            sound_file_path = expanded_file_path
        else:
            app_sound_path = os.path.join('sounds', expanded_file_path)
            if os.path.exists(app_sound_path):
                sound_file_path = app_sound_path
            else:
                alternate_music_path = os.path.join(pathlib.Path.home(), 'Music', file_path)
                if os.path.exists(alternate_music_path):
                    sound_file_path = alternate_music_path
        return sound_file_path

    def play_sound(self, sound_file):
        """
        play_game
        args: self - self object
            sound_file - sound file to play
        purpose: send play command for specified sound file
        """
        app = App.get_running_app()
        volume = app.app_data_dict['config']['volume']
        if not volume['mute'] and sound_file and sound_file in self.sound_dict:
            sound = self.sound_dict[sound_file]
            if sound.state == 'play':
                sound.stop()
            sound.volume = volume['percent'] / 100
            sound.seek(0)
            sound.play()

    def set_all_volumes(self):
        """
        set_all_volumes
        args: self - self object
        purpose: set volume of all sound objects
        """
        app = App.get_running_app()
        volume_config = app.app_data_dict['config']['volume']
        volume = 0 if volume_config['mute'] else volume_config['percent'] / 100
        for sound_obj in self.sound_dict.values():
            sound_obj.volume = volume

    def stop_all_sounds(self):
        """
        stop_all_sounds
        args: self - self object
        purpose: stop playing all sounds
        """
        for sound_file in self.sound_dict:
            self.stop_sound(sound_file)

    def stop_sound(self, sound_file):
        """
        stop_sound
        args: self - self object
            sound_file - soudn file to stop
        purpose: send stop play for specified sound file
        """
        if sound_file and sound_file in self.sound_dict and self.sound_dict[sound_file].state == 'play':
            self.sound_dict[sound_file].stop()
            self.sound_dict[sound_file].seek(0)

    def update_sound_dict(self):
        """
        update_sound_dict
        args: self - self object
        purpose: add any additional sound files to
        """
        app = App.get_running_app()
        sound_files = app.app_data_dict['unpickleable']['database'].get_sound_files()
        for sound_file_item in sound_files:
            if sound_file_item['sound_file'] not in self.sound_dict:
                sound_file_path = self.find_sound_file_path(sound_file_item['sound_file'])
                if sound_file_path:
                    self.sound_dict[sound_file_item['sound_file']] = SoundLoader.load(sound_file_path)
