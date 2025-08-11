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
import copy
import random
from kivy.app import App
from kivy.lang.builder import Builder
# local imports
import over_press
import soft_keyboard
import stateful_clock
import workout_trainer_util
from workout_trainer import WorkoutTrainer

class WorkoutTrainerTimedRandomMuscleConfusion(WorkoutTrainer):
    """
    WorkoutTrainerTimedRandomMuscleConfusion
    purpose: provide a trainer class for timed, random, muscle confusion style workouts
    """

    def __init__(self, data_dict, **kwargs):
        """
        __init__
        args: self - self object
            data_dict - application data dictionary
            kwargs - remaining init arguments for MBBoxLayout
        purpose: reload trainer sate if unpaused on Android
        """
        super(WorkoutTrainer, self).__init__(**kwargs)
        properties = data_dict['global properties']
        if properties['timed random muscle confusion carousel widgets']:
            self.ids['workout_exercise_image_carousel'].clear_widgets()
            for kv in properties['timed random muscle confusion carousel widgets']:
                muscle_image_widget = Builder.load_string(kv)
                self.ids['workout_exercise_image_carousel'].add_widget(muscle_image_widget)
            if len(self.ids['workout_exercise_image_carousel'].slides) > 1:
                stateful_clock.schedule_interval(self.rotate_exercise_image, 20)
        if properties['timed random muscle confusion set widgets']:
            workout_set_carousel = self.ids['workout_set_carousel']
            blank_slide = workout_set_carousel.slides[-1]
            workout_set_carousel.remove_widget(blank_slide)
            for kv in properties['timed random muscle confusion set widgets']:
                workout_set_carousel.add_widget(Builder.load_string(kv))
            workout_set_carousel.add_widget(blank_slide)
            workout_set_carousel.load_slide(workout_set_carousel.slides[-2])
        self.ids['set_timer'].keypad_container = self.ids['workout_timer'].keypad_container = \
            self.ids['keypad_container_id']
        soft_keyboard.render_keyboard_shortcut(self)

    def get_next_set(self):
        """
        get_next_set
        args: self - self object
        purpose: generate and display next workout set
        """
        app = App.get_running_app()
        if over_press.protect(app = app):
            properties = app.app_data_dict['global properties']
            properties['set count'] += 1
            unpickleable = app.app_data_dict['unpickleable']
            workout = app.app_data_dict['workout dictionary'][properties['timed random muscle confusion workout index']]
            muscle_group = random.choice(workout['muscle group'])
            if properties['exercise']:
                unpickleable['sound'].stop_sound(properties['exercise']['alarm sound file'])
                self.ids['set_timer'].stop_alarm()
            exercise = properties['exercise'] = random.choice(muscle_group['exercises'])
            properties['timed random muscle confusion exercise name'] = \
                app.timed_random_muscle_confusion_exercise_name = f'[b]{exercise["name"]}[/b]' #.format(exercise['name']) cjh
            properties['muscle group name'] = muscle_group['name']
            if exercise['set timer']:
                minute = exercise['set timer'] // 60
                second = exercise['set timer'] % 60
                properties['workout set timer'] = app.workout_set_timer = f'{minute:02d}:{second:02d}.0' #.format(minute, second) cjh
                properties['workout set'] = workout_trainer_util.gen_set_base_string(None,
                    properties['set count'], workout, muscle_group, exercise)
                self.ids['set_timer'].state = 'not started'
            else:
                properties['workout set'] = '{}[i]reps[/i]: [b]{}[/b]'.format(
                    workout_trainer_util.gen_set_base_string(None, properties['set count'], workout,
                    muscle_group, exercise), exercise['target reps'])
                self.ids['set_timer'].state = 'finished'
                properties['workout set timer'] = app.workout_set_timer = ''
            self.next_workout_image(exercise['name'])
            self.next_set_label()
            self.set_finished_pulsate_object = None
            workout['active set'].append(copy.deepcopy(exercise))
            workout['active set'][-1]['workout name'] = workout['name']
            workout['active set'][-1]['recorded'] = False
            set_recorder = unpickleable['set recorder']
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
        properties = app.app_data_dict['global properties']
        unpickleable = app.app_data_dict['unpickleable']
        trmc_index = properties['timed random muscle confusion workout index'] = properties['workout index']
        workout = app.app_data_dict['workout dictionary'][trmc_index]
        set_recorder = unpickleable['set recorder']
        if workout['active set']:
            workout['set recorder index'] = len(workout['active set']) -1
            set_recorder.ids['set_recorder_form_id'].disabled = False
        else:
            workout['set recorder index'] = 0
            set_recorder.ids['set_recorder_form_id'].disabled = True
        workout_timer = self.ids['workout_timer']
        if workout_timer.state == 'shutdown':
            workout_timer.state = 'not started'
            workout_index = properties['workout index']
            workout_timer.time_left = app.app_data_dict['workout dictionary'][workout_index]['time length']
        self.ids['keypad_button_container_id'].disabled = False
        set_recorder.update_set_recorder()
        set_recorder.update_form()

    def next_set_label(self):
        """
        next_set_label
        args: self - self object
        purpose: populate and state store a set label
        """
        app = App.get_running_app()
        set_carousel = self.ids['workout_set_carousel']
        trmc_widgets = app.app_data_dict['global properties']['timed random muscle confusion set widgets']
        if (set_carousel.previous_slide and not set_carousel.previous_slide.past_set and len(trmc_widgets) > 1):
            set_carousel.previous_slide.custom_color = (0.35, 0, 0, 1)
            set_carousel.previous_slide.past_set = True
            trmc_widgets[-2] += """
    custom_color: (0.35, 0, 0, 1)
    past_set: True
"""
        set_label = set_carousel.current_slide
        set_label.text = app.app_data_dict['global properties']['workout set']
        trmc_widgets[-1] += '    text: "{}"'.format(app.app_data_dict['global properties']['workout set'].replace('"', "'").replace('\n', '\\n'))

    def play_set_alarm(self):
        """
        play_set_alarm
        args: self - self object
        purpose: play set alarm sound file
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['sound'].play_sound(app.app_data_dict['global properties']['exercise']['alarm sound file'])
        app.app_data_dict['unpickleable']['vibrateor'].vibrate('alarm')

    def summon_keyboard_press(self, *kwargs):
        """
        summon_keyboard_press
        args: self - self object
            kwargs - kivy arguments
        purpose: provide method to summon keyboard on keyboard button press
        """
        self.summon_keyboard_template('workout_timer')
