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
from kivy.properties import ColorProperty
from kivy.uix.image import Image
# local imports
import over_press
from muscle_selector import MuscleSelector
from workout_trainer import WorkoutTrainer

class WorkoutTrainerInstinctualTraining(WorkoutTrainer, MuscleSelector):
    """
    WorkoutTrainerInstinctualTraining
    purpose: class for doing arbitrary sets in workout
    """
    initializing = True
    image_orientation = 'front'
    map_state_key = 'instinctual trainer image state'
    muscle_selector_container = None
    exercise_carousel = None
    add_button = None
    selector_back_button_color = ColorProperty((0, 0, 0, 1))
    selector_front_button_color = ColorProperty((0, 0.5, 0.8, 1))

    def __init__(self, data_dict, **kwargs):
        """
        __init__
        args: self - self object
            data_dict - application data dictionary
            kwargs - remaining init arguments for MBBoxLayout
        purpose: set initial base image
        """
        super(WorkoutTrainer, self).__init__(**kwargs)
        image = Image(source=os.path.join('images', data_dict['image overlays']['Master']['front']), fit_mode='contain')
        image.bind(on_touch_up=self.muscle_touched)
        self.ids['muscle_selector_id'].add_widget(image)
        self.initializing = False
        self.muscle_selector_container = self.ids['muscle_selector_id']
        self.exercise_carousel = self.ids['exercise_selector_carousel']
        self.add_button = self.ids['add_set_button_id']

    def add_set(self): # called from workout_trainer_instinctual_training.kv
        """
        add_set
        args: self - self object
        purpose: add set to workout
        """
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['workout index']]
            exercise_set = {
                'set number': None,
                'name': self.ids['exercise_selector_carousel'].current_slide.text,
                'weight unit name': None,
                'target weight': None,
                'target reps': None,
                'left weight': None,
                'left reps':  None,
                'recorded': False,
                'right weight': None,
                'right reps': None,
                'set timer': None
            }
            workout['active set'].append(exercise_set)
            set_recorder = app.app_data_dict['unpickleable']['set recorder']
            set_recorder.ids['set_recorder_form_id'].disabled = False
            set_recorder.update_set_recorder()
            set_recorder.update_form()

    def load_workout(self):
        """
        load_workout
        args: self - self object
        purpose: load workout
        """
        app = App.get_running_app()
        workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['workout index']]
        set_recorder =  app.app_data_dict['unpickleable']['set recorder']
        if workout['active set']:
            set_recorder.ids['set_recorder_form_id'].disabled = False
            set_recorder.update_set_recorder()
            set_recorder.update_form()
        else:
            set_recorder.ids['set_recorder_form_id'].disabled = True
