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
import math
from kivy.app import App
from kivy.graphics.opengl import glGetIntegerv, GL_MAX_TEXTURE_SIZE
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
# local imports
from license_label import LicenseLabel

class About(MDBoxLayout):

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - arguments for MDBoxLayout
        purpose: initialize about page
        """
        super().__init__(**kwargs)
        self.load_license_text()

    def load_license_text(self):
        """
        load_licsene_text
        args: self - self object
        purpose: load license text into slider view
        """
        app = App.get_running_app()
        license_lines = []
        with open('license.txt', 'r') as file:
            license_lines = file.readlines()
        num_of_lines = len(license_lines)
        max_texture_size = glGetIntegerv(GL_MAX_TEXTURE_SIZE)[0]
        labels = []
        if 'license' in app.app_data_dict['config']:
            divider = app.app_data_dict['config']['license']['chunk count']
            loop = True
        else:
            labels.append(LicenseLabel(text = ''.join(license_lines)))
            self.ids['license_container_id'].add_widget(labels[0])
            labels[0].texture_update()
            divider = math.ceil(labels[0].texture_size[1] / max_texture_size)
            loop = bool(divider != 1)
        while loop:
            Logger.info('about: divider = {}'.format(divider))
            split_line_count = math.ceil(num_of_lines / divider)
            list_in_list = [license_lines[i:i + split_line_count] for i in range(0, num_of_lines, split_line_count)]
            for label_index, license_lines_part in enumerate(list_in_list):
                label_text = ''.join(license_lines_part)
                if label_index == len(labels):
                    labels.append(LicenseLabel(text = label_text))
                    self.ids['license_container_id'].add_widget(labels[label_index])
                else:
                    labels[label_index].text = label_text
                license_label = labels[label_index]
                license_label.texture_update()
                Logger.info('about: texture_size = {}'.format(license_label.texture_size))
                if license_label.texture_size[1] > max_texture_size:
                    divider += 1
                    loop = True
                    break
                else:
                    loop = False
        Logger.info('about: License loaded in {} parts'.format(divider))
        app.app_data_dict['config']['license'] = {'chunk count': divider}

