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
from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.carousel import Carousel
# local imports
from set_label import SetLabel # needed for Kivy's factories

class SetCarousel(Carousel):
    """
    SetCarousel
    purpose: carousel class with ability to call parent to generate dynamic sets
    """

    def gen_next_set(self):
        """
        gen_next_set
        args: self - self object
        purpose: generate the next set upon swiping to end of carousel
        """
        if self.next_slide is None:
            app = App.get_running_app()
            kv = """
SetLabel:
    halign: 'center'
    valign: 'bottom'
    markup: True
"""
            app.app_data_dict['global properties']['timed random muscle confusion set widgets'].append(kv)           
            set_label = Builder.load_string(kv)
            self.add_widget(set_label)
            app.app_data_dict['unpickleable']['trainer']['timed, random, muscle confusion'].get_next_set()
