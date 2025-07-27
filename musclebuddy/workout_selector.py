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
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.boxlayout import MDBoxLayout
#local imports
import soft_keyboard
from scaling_label import ScalingLabel
from workout_selector_carousel import WorkoutSelectorCarousel

class WorkoutSelector(MDBoxLayout):
    """
    WorkoutSelector
    purpose: class for the workout selection screen
    """

    selector_load_complete = False

    def load_workout_selector(self):
        """
        load_workout_selector
        args: self - self object
        purpose: load workout selector objects to build out selector
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        unpickleable['workout selector workout carousels'] = carousels = {}
        properties = app.app_data_dict['global properties']
        self.ids['workout_type_carousel'].clear_widgets()
        for i, workout in enumerate(app.app_data_dict['workout dictionary']):
            if workout['type'] not in carousels:
                box_layout = MDBoxLayout(orientation='vertical')
                box_layout.type_name = workout['type name']
                string1, string2 = self.split_string(workout['type name'])
                box_layout.add_widget(Widget(size_hint_y=0.05))
                box_layout.add_widget(ScalingLabel(text=string1, halign='center', valign='top', size_hint_y=0.05,
                    markup=True))
                box_layout.add_widget(ScalingLabel(text=string2, halign='center', valign='top', size_hint_y=0.05,
                    markup=True))
                box_layout.add_widget(Widget(size_hint_y=0.05))
                box_layout.add_widget(Image(size_hint_y=0.4, mipmap=True, fit_mode='contain',
                    source=os.path.join('images', workout['image file'])))
                carousels[workout['type']] = WorkoutSelectorCarousel(loop=True, size_hint_y=0.4, direction='bottom',
                    ignore_perpendicular_swipes=True)
                box_layout.add_widget(carousels[workout['type']])
                self.ids['workout_type_carousel'].add_widget(box_layout)
            anchor_layout = MDAnchorLayout(anchor_x='center', anchor_y='center')
            box_layout = MDBoxLayout(orientation='vertical')
            string1, string2 = self.split_string(workout['name'])
            box_layout.add_widget(Widget())
            box_layout.add_widget(ScalingLabel(halign='center', valign='top', text=string1, size_hint_y=0.5,
                markup=True))
            box_layout.add_widget(ScalingLabel(halign='center', valign='top', text=string2, size_hint_y=0.5,
                markup=True))
            box_layout.add_widget(Widget())
            anchor_layout.add_widget(box_layout)
            anchor_layout.workout_index = i
            carousels[workout['type']].add_widget(anchor_layout)
        app.navigation_map['Workout Trainer']['screen'] = \
            unpickleable['trainer'][app.app_data_dict['workout dictionary'][0]['type']]
        Logger.info('Application: loading index {}'.format(properties['trainer index']))
        workout_type_slide = self.ids['workout_type_carousel'].slides[properties['trainer index']]
        self.ids['workout_type_carousel'].load_slide(workout_type_slide)
        for child in workout_type_slide.children:
            if type(child) is WorkoutSelectorCarousel:
                properties['selector workout index'] = properties['selector workout index'] if \
                    properties['selector workout index'] < len(child.slides) else 0
                workout_slide = child.slides[properties['selector workout index']]
                child.load_slide(workout_slide)
                break
        self.selector_load_complete = True

    def set_trainer(self, trainer_index): # called from workout_selector.kv
        """
        set_trainer
        args: self - self object
            trainer_index - index of workout type carousel
        purpose: set the workout tab to match the selector
        """
        if type(trainer_index) is int:
            app = App.get_running_app()
            for child in self.ids['workout_type_carousel'].current_slide.children:
                if type(child) is WorkoutSelectorCarousel and child.current_slide:
                    index = app.app_data_dict['global properties']['workout index'] = child.current_slide.workout_index
                    workout = app.app_data_dict['workout dictionary'][index]
                    trainer = app.app_data_dict['unpickleable']['trainer'][workout['type']]
                    app.navigation_map['Workout Trainer']['screen'] = trainer
                    soft_keyboard.remove_soft_keyboard(app=app)
                    trainer.load_workout()
                    if workout['time length']:
                        time_length = workout['time length']
                        hour = int(time_length // 3600)
                        minute = int((time_length % 3600) // 60)
                        second = int(time_length % 60)
                        app.app_data_dict['global properties']['workout time'] = app.workout_timer = \
                            f'{hour:02d}:{minute:02d}:{second:02d}'
                    break
            Logger.info(f'Application: trainer index {trainer_index}')
            if self.selector_load_complete:
                app.app_data_dict['global properties']['trainer index'] = trainer_index

    def split_string(self, string):
        """
        split_string
        args: self - self object
            string - string to split
        purpose: split string into two if over 25 in length
        returns: tuple of split strings
        """
        string1 = string
        string2 = ''
        if len(string) > 25:
            for i in range(25, -1, -1):
                if string[i] == ' ':
                    string1 = string[0:i]
                    string2 = string[i+1:]
                    break
        return string1, string2
