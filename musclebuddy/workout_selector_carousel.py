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
from kivy.uix.carousel import Carousel
from kivymd.uix.anchorlayout import MDAnchorLayout

class WorkoutSelectorCarousel(Carousel):
    """
    WorkoutSelectorCarousel
    purpose: class for selecting indivisual workouts from a workout group
    """
 
    def on_current_slide(self, carousel, slide): # called from Kivy engine
        """
        on_current_slide
        args: self - self obect
            carousel - carousel object
            slide - slide object
        purpose: set active workout index for dictionary
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        if unpickleable['workout selector'].selector_load_complete and isinstance(slide, MDAnchorLayout):
            properties = app.app_data_dict['global properties']
            properties['workout index'] = slide.workout_index
            properties['selector workout index'] = carousel.index
            if not properties['timer started']:
                if app.app_data_dict['workout dictionary'][slide.workout_index]['time length']:
                    time_length = app.app_data_dict['workout dictionary'][slide.workout_index]['time length']
                    hour = int(time_length // 3600)
                    minute = int((time_length % 3600) // 60)
                    second = int(time_length % 60)
                    properties['workout time'] = app.workout_timer = \
                        f'{hour:02d}:{minute:02d}:{second:02d}'
                else:
                    properties['workout time'] = app.workout_timer = ''
            unpickleable['trainer'][app.app_data_dict['workout dictionary'][slide.workout_index]['type']].load_workout()
