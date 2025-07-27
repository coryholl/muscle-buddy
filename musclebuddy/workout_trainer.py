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
from kivy.lang.builder import Builder
from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
# local imports
import over_press
import set_carousel # needed by Kivy engine
import set_timer # needed by Kivy engine
import soft_keyboard
import stateful_clock
import workout_timer # needed by Kivy engine

class WorkoutTrainer(MDBoxLayout):
    """
    WorkoutTrainer
    purpose: abstract class for writing trainers
    """

    def get_muscle_widgets(self, exercise_name):
        """
        get_muscle_widgets
        args: self - self object
            exercise_name - name of exercise
        purpose: return list of widgets to represent the exercise in progress
        returns: list of displayable widgets
        """
        widgets = []
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        properties['workout muscle widgets'] = []
        overlays = app.app_data_dict['image overlays']
        kv_header = """
FloatLayout:
"""
        kv_body = """
    AsyncImage:
        source: '{}'
        mipmap: True
        fit_mode: 'contain'
"""
        if exercise_name == 'rest':
            kv = kv_header + kv_body.format(os.path.join('images', overlays[exercise_name]['rest']['rest'][0]))
            properties['workout muscle widgets'].append(kv)
            float_layout = Builder.load_string(kv)
            widgets.append(float_layout)
        else:
           for orientation in ('front', 'back'):
                if orientation in overlays[exercise_name]:
                    kv = kv_header + kv_body.format(os.path.join('images', overlays['Master'][orientation]))
                    for focus in ['secondary', 'primary']:
                        if focus in overlays[exercise_name][orientation]:
                            for image_file in overlays[exercise_name][orientation][focus]:
                                kv += kv_body.format(os.path.join('images', image_file))
                    properties['workout muscle widgets'].append(kv)
                    float_layout = Builder.load_string(kv)
                    widgets.append(float_layout)
        return widgets

    def load_workout(self):
        """
        load_workout
        args: self - self object
        purpose: stub for load workout logic that most trainers have
        """
        pass

    def next_workout_image(self, exercise_name):
        """
        next_workout_image
        args: self - self object
            exercise_name - exercise name
        purpose: generate next images for next work workout set
        """
        stateful_clock.unschedule(self.rotate_exercise_image)
        try:
            self.ids['workout_exercise_image_carousel'].clear_widgets()
        except Exception as e:
            Logger.info('Application: self.ids[\'workout_exercise_image_carousel\'].clear_widgets() failed')
        for widget in self.get_muscle_widgets(exercise_name):
            self.ids['workout_exercise_image_carousel'].add_widget(widget)
        if len(self.ids['workout_exercise_image_carousel'].slides) > 1:
            stateful_clock.schedule_interval(self.rotate_exercise_image, 20.5)

    def play_workout_alarm(self):
        """
        play_workout_alarm
        args: self - self object
        purpose: play workout alarm sound file
        """
        app = App.get_running_app()
        unpickleable =  app.app_data_dict['unpickleable']
        workout_dict = app.app_data_dict['workout dictionary']
        properties = app.app_data_dict['global properties']
        unpickleable['sound'].play_sound(workout_dict[properties['workout index']]['alarm sound file'])
        stateful_clock.unschedule(self.rotate_exercise_image)
        properties['timed random muscle confusion exercise name'] = app.timed_random_muscle_confusion_exercise_name = \
            "[b]WORKOUT COMPLETE!!![/b]"
        workout = workout_dict[properties['workout index']]
        image_widgets = unpickleable['finish image widget']
        image_widget = image_widgets[workout['finish image file']] \
            if (workout['finish image file'] in image_widgets) else None
        if image_widget:
            self.ids['workout_exercise_image_carousel'].clear_widgets()
            if image_widget.parent:
                image_widget.parent.remove_widget(image_widget)
            self.ids['workout_exercise_image_carousel'].add_widget(image_widget)
            if workout['finish image file'].lower().endswith('.gif'):
                image_widget.anim_delay = 0.05
        unpickleable['vibrator'].vibrate('finish')

    def reset_image_rotate_timer(self, touch): # called from workout_trainer_classic_strength_training.kv and workout_trainer_timed_random_muscle_confusion.kv
        """
        reset_image_rotate_timer
        args: self - self object
            touch - touch event object
        purpose: reset rotate timer because user changed slides manually
        """
        if len(self.ids['workout_exercise_image_carousel'].slides) > 1:
            stateful_clock.unschedule(self.rotate_exercise_image)
            stateful_clock.schedule_interval(self.rotate_exercise_image, 20.5)

    def rotate_exercise_image(self, dt):
        """
        rotate_exercise_image
        args: self - self object
            dt - time since last callback call
        purpose: rotate exercise image
        """
        self.ids['workout_exercise_image_carousel'].load_next()

    def summon_keyboard_template(self, timer_id):
        """
        summon_keyboard_template
        args: self - self object
            timer_id - kivy id of timer widget
        purpose: provide template for summoning timepad for trainers
        """
        if over_press.protect(vibrate=True):
            self.ids[timer_id].state = 'pause'
            stateful_clock.unschedule(self.ids[timer_id].get_time)
            time_pad = soft_keyboard.get_keyboard('time')
            time_pad.on_key_up = self.ids[timer_id].key_press
            if time_pad.parent:
                time_pad.parent.remove_widget(time_pad)
            self.ids['keypad_container_id'].add_widget(time_pad)
            stateful_clock.schedule_interval(self.ids[timer_id].timer_paused_indicator, 0.05)
