# Copyright (C) 2025 Cory Jon Hollingsworth
#
# This file is part of Muscle Buddy.
#
# Muscle Buddy is free software: you can redistribute it and/or modify
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
# along with Muscle Buddy.  If not, see <https://www.gnu.org/licenses/>.
import os
from kivy.app import App
from kivy.logger import Logger
from kivymd.uix.filemanager import MDFileManager
#local imports
import over_press

class SoundSelector(MDFileManager):
    ext = ['.ogg', '.OGG', '.mp3', '.MP3', '.wav', '.WAV']

    def _create_selection_button(self, *args):
        """
        _create_selection_button
        args: self - self object
            args - kivymd internal arguments
        purpose: customize selection appearance to remove selection button and improve toolbar appearance
        """
        toolbar = self.ids['toolbar']
        toolbar.specific_text_color = (1, 1, 1, 1)
        toolbar.right_action_items[0][0] = 'close-thick'

    def back(self):
        """
        back
        args: self - self object
        purpose: add overpress protection and vibrate to back event
        """
        Logger.info('sound_selector: back')
        if over_press.protect(vibrate=True):
            super().back()

    def select_dir_or_file(self, path, widget):
        """
        select_dir_or_file
        args: self - self object
            path - path of directory
            widget - kivy widget
        purpose: add vibrate and overpress protection to directory selection
        """
        Logger.info(f'sound_selector: select_dir_or_file: {path}')
        if over_press.protect(vibrate=True):
            super().select_dir_or_file(path, widget)
            if os.path.isfile(path) and os.path.splitext(path)[-1] in self.ext:
                app = App.get_running_app()
                app.app_data_dict['unpickleable']['workout builder'].sound_selector_set_path(path)

    def show(self, path):
        """
        show
        args: self - self object
            path - path to show in file manager
        purpose: override show method so better icons can be displayed
        """
        Logger.info(f'sound_selector: show {path}')
        super().show(path)
        for x in self.ids.rv.data:
            if os.path.isfile(x['path']) and os.path.splitext(x['path'])[-1] in self.ext:
                x['icon'] = 'music'
