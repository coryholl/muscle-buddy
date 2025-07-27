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
# local imports
import soft_keyboard
from rest_timer import RestTimer # needed by kivy runtime
from workout_trainer import WorkoutTrainer

class WorkoutTrainerClassicStrengthTraining(WorkoutTrainer):
    """
    WorkoutTrainerClassicStrengthTraining
    purpose: class for running a strength training workout
    """

    def __init__(self, data_dict, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - remaining init arguments for MBBoxLayout
        purpose: reload trainer sate if unpaused on Android
        """
        super(WorkoutTrainer, self).__init__(**kwargs)
        self.ids['rest_timer'].keypad_container = self.ids['keypad_container_id']
        soft_keyboard.render_keyboard_shortcut(self)

    def load_workout(self):
        """
        load_workout
        args: self - self object
        purpose: load workout
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        properties['classic workout index'] = properties['workout index']
        workout = app.app_data_dict['workout dictionary'][properties['classic workout index']]
        properties['muscle group name'] = workout['muscle group'][0]['name']
        workout_set_carousel = self.ids['workout_set_carousel']
        workout_set_carousel.clear_widgets(children=workout_set_carousel.slides[1:])
        for kv in workout['set widgets']:
            workout_set_carousel.add_widget(Builder.load_string(kv))
        workout_set_carousel.load_slide(workout_set_carousel.slides[workout['set carousel index']])
        if properties['classic exercise name']:
            self.next_workout_image(properties['classic exercise name'].replace('[b]', '').replace('[/b]', ''))
        set_recorder = app.app_data_dict['unpickleable']['set recorder']
        set_recorder.ids['set_recorder_form_id'].disabled = False
        set_recorder.update_set_recorder()
        set_recorder.update_form()

    def set_changed(self, index): # called from workout_trainer_classic_strength_training.kv
        """
        set_changed
        args: self - self object
            index - index of set carousel
        purpose: update classic trainer widgets to match new set
        """
        app = App.get_running_app()
        workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['classic workout index']]
        workout['set carousel index'] =  index
        if index and index <= len(workout['active set']):
            exercise = workout['active set'][index - 1]
            exercise_name = '[b]{}[/b]'.format(exercise['name'])
            if exercise_name != app.classic_exercise_name:
                app.app_data_dict['global properties']['classic exercise name'] = app.classic_exercise_name = exercise_name
                self.next_workout_image(exercise['name'])

    def summon_keyboard_press(self, *kwargs):
        """
        summon_keyboard_press
        args: self - self object
            kwargs - kivy arguments
        purpose: provide method to summon keyboard on keyboard button press
        """
        self.summon_keyboard_template('rest_timer')
