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
from collections import OrderedDict
from kivy.app import App
#from kivy.logger import Logger
from kivymd.uix.boxlayout import MDBoxLayout
#local imports
import over_press
import soft_keyboard
from text_input_util import TextInputUtil
from workout_text_field import WorkoutTextField

class SetRecorder(MDBoxLayout, TextInputUtil):
    """
    SetRecorder
    purpose: class for recording the results of exercise sets
    """
    all_input_fields = OrderedDict()
    focus_order = None
    prefix_string = 'set recorder'
    set_index = None

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - unknown arguments to pass on to parent class
        purpose: initialize set recorder restoring state on Android if necessary
        """
        super(MDBoxLayout, self).__init__(**kwargs)
        app = App.get_running_app()
        self.set_index = app.app_data_dict['global properties']['set recorder index']
        self.init_set_fields('set recorder', app.app_data_dict['window height'] // 35, app=app)
        unpickleable = app.app_data_dict['unpickleable']
        items = [(k, v) for k, v in unpickleable.items() if k.startswith(self.prefix_string) and
            isinstance(v, WorkoutTextField)]
        for key, text_field in items:
            self.all_input_fields[key] = text_field
        soft_keyboard.render_keyboard_shortcut(self, app=app)
        self.render_set_form()

    def initialize_set_recorder(self):
        """
        initialize_set_recorder
        args: self - self object
            exercise_set - dictionary containing initial exercise set
        purpose: initialize set recorder
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['workout index']]
        properties['set recorder index'] = self.set_index = workout['set recorder index']
        self.update_form()

    def next_press(self): # called from set_recorder.kv
        """
        next_press
        args: self - self object
        purpose: go to next set
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        if over_press.protect(app = app, vibrate=True):
            workout = app.app_data_dict['workout dictionary'][properties['workout index']]
            if workout['set recorder index'] < (len(workout['active set']) - 1):
                workout['set recorder index'] += 1
                properties['set recorder index'] = workout['set recorder index']
                self.provision_state_store('previous_button_id')
                properties['set recorder states']['previous_button_id']['disabled'] = (
                    self.ids['previous_button_id'].disabled) = False
                if workout['set recorder index'] == (len(workout['active set']) - 1):
                    self.provision_state_store('next_button_id')
                    properties['set recorder states']['next_button_id']['disabled'] = (
                        self.ids['next_button_id'].disabled) = True
                self.set_save_button(workout['active set'][workout['set recorder index']]['recorded'])
                self.update_form()

    def parse_time(self, time_str):
        """
        parse_time
        args: self - self object
            time_str - string containing time
        purpose: parse a entered time into total seconds
        """
        if time_str is None or time_str == '00:00':
            seconds = None
        else:
            min_str, sec_str = time_str.split(':')
            seconds = (int(min_str) * 60) + int(sec_str)
        return seconds

    def previous_press(self): # called from set_recorder.kv
        """
        previous_press
        args: self - self object
        purpose: go to previous set
        """
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            properties = app.app_data_dict['global properties']
            workout = app.app_data_dict['workout dictionary'][properties['workout index']]
            if workout['set recorder index']:
                workout['set recorder index'] -= 1
                properties['set recorder index'] = workout['set recorder index']
                if not workout['set recorder index']:
                    self.provision_state_store('previous_button_id')
                    properties['set recorder states']['previous_button_id']['disabled'] = (
                        self.ids['previous_button_id'].disabled) = True
                self.provision_state_store('next_button_id')
                properties['set recorder states']['next_button_id']['disabled'] = (
                    self.ids['next_button_id'].disabled) = False
                self.set_save_button(workout['active set'][workout['set recorder index']]['recorded'])
                self.update_form()

    def provision_state_store(self, key):
        """
        provision_state_store
        args: self - self object
            key - dictionary key
        purpose: provision an entry to the set recorder state dictionary if missing
        """
        app = App.get_running_app()
        if key not in app.app_data_dict['global properties']['set recorder states']:
            app.app_data_dict['global properties']['set recorder states'][key] = {}

    def record_set(self):
        """
        record_set
        args: self - self object
        purpose: record a set
        """
        app = App.get_running_app()
        workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['workout index']]
        workout['active set'][workout['set recorder index']]['recorded'] = True
        self.set_save_button(True)
        self.save_current_set()

    def replace_set_confirmed(self, *kwargs):
        """
        replace_set_confirmed
        args - self - self object
            kwargs - argument from popup widget
        purpose: perform a replace set operation upon confirmation
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            self.record_set()
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()

    def restore_set_recorder_after_pause(self, dt):
        """
        restore_set_recorder_after_pause
        args: self - self object
            dt - time since last callback call
        purpose: delayed restore of Android state to fix chicken and egg problem
        """
        app = App.get_running_app()
        for kivy_id, values in app.app_data_dict['global properties']['set recorder states'].items():
            if 'decimal disabled' in values:
                self.ids[kivy_id].decimal_disabled = values['decimal disabled']
            if 'disabled' in values:
                self.ids[kivy_id].disabled = values['disabled']
            if 'icon' in values:
                self.ids[kivy_id].icon = values['icon']
            if 'icon_color' in values:
                self.ids[kivy_id].icon_color = values['icon_color']
            if 'text' in values:
               self.ids[kivy_id].text = values['text']

    def save_current_set(self):
        """
        save_current_set
        args: self - self object
        purpose: save set to database
        """
        app = App.get_running_app()
        left_right_is_on = (self.ids['left_right_button_id'].icon == self.left_right_on_icon)
        timed_is_on = (self.ids['reps_timer_button_id'].icon == self.timed_on_icon)
        workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['workout index']]
        exercise_set = workout['active set'][workout['set recorder index']]
        unpickleable = app.app_data_dict['unpickleable']
        exercise_set['name'] = self.ids['exercise_name_id'].text
        exercise_set['left weight'] = float(unpickleable['set recorder left weight'].text) if (
                unpickleable['set recorder left weight'].text and left_right_is_on) else None
        exercise_set['left reps'] = int(unpickleable['set recorder left reps'].text) if (
                unpickleable['set recorder left reps'].text and left_right_is_on and not timed_is_on) else None
        exercise_set['left time'] = self.parse_time(unpickleable['set recorder left time'].text) if (
                left_right_is_on and timed_is_on) else None
        exercise_set['right weight'] = float(unpickleable['set recorder right weight'].text) if (
                unpickleable['set recorder right weight'].text and left_right_is_on) else None
        exercise_set['right reps'] = int(unpickleable['set recorder right reps'].text) if (
                unpickleable['set recorder right reps'].text and left_right_is_on and not timed_is_on) else None
        exercise_set['right time'] = self.parse_time(unpickleable['set recorder right time'].text) if (
                left_right_is_on and timed_is_on) else None
        exercise_set['set number'] = workout['set recorder index'] + 1
        exercise_set['target reps'] = int(unpickleable['set recorder reps'].text) if (
                unpickleable['set recorder reps'].text and not left_right_is_on and not timed_is_on) else None
        exercise_set['target weight'] = float(unpickleable['set recorder weight'].text) if (
                unpickleable['set recorder weight'].text and not left_right_is_on) else None
        exercise_set['time'] = self.parse_time(unpickleable['set recorder time'].text) if (
                not left_right_is_on and timed_is_on) else None
        exercise_set['trainer'] = workout['type']
        exercise_set['weight unit name'] = 'pound' if self.ids['pound_kilogram_button_id'].icon == self.pound_icon else 'kilogram'
        exercise_set['workout name'] = workout['name']
        unpickleable['database'].store_set(exercise_set)

    def set_recommended_set_from_workout_plan(self, unpickleable, exercise_set, none_to_val):
        """
        set_recommended_set_from_workout_plan
        args: self - self object
            unpickleable - dictionary of unpickleable Kivy objects
            exercise_set - dictionary of exercise sets
            none_to_val - method for converting None to '' or strings
        purpose: set form input text values from workout plan
        """
        unpickleable['set recorder left reps'].text = none_to_val(exercise_set['left reps'])
        unpickleable['set recorder left time'].text = \
            self.to_min_sec(int(exercise_set['left time'])) if exercise_set.get('left time') else '00:00'
        unpickleable['set recorder left weight'].text = none_to_val(exercise_set['left weight'])
        unpickleable['set recorder reps'].text = none_to_val(exercise_set['target reps'])
        unpickleable['set recorder right reps'].text = none_to_val(exercise_set['right reps'])
        unpickleable['set recorder right time'].text = \
            self.to_min_sec(int(exercise_set['right time'])) if exercise_set.get('right time') else '00:00'
        unpickleable['set recorder right weight'].text = none_to_val(exercise_set['right weight'])
        unpickleable['set recorder time'].text = \
            self.to_min_sec(int(exercise_set['time'])) if exercise_set.get('time') else '00:00'
        unpickleable['set recorder weight'].text = none_to_val(exercise_set['target weight'])

    def save_press(self): # called from set_recorder.kv
        """
        save_press
        args: self - self object
        purpose: process save set button press
        """
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            if self.ids['save_button_id'].icon == 'notebook-check':
                app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup('Replace recorded set?',
                    self.replace_set_confirmed, over_press_protected=True)
            else:
                self.record_set()

    def set_save_button(self, recorded_flag):
        """
        set_save_button
        args: self - self object
            recorded_flag - boolean indicator as to if the set has been recorded
        purpose: set save button graphics and enable
        """
        app = App.get_running_app()
        self.provision_state_store('save_button_id')
        save_button_state = app.app_data_dict['global properties']['set recorder states']['save_button_id']
        if recorded_flag:
            save_button_state['icon'] = self.ids['save_button_id'].icon = 'notebook-check'
            save_button_state['icon_color'] = self.ids['save_button_id'].icon_color = (0, 0.75, 0, 1)
        else:
            save_button_state['icon'] = self.ids['save_button_id'].icon = 'notebook-edit'
            save_button_state['icon_color'] = self.ids['save_button_id'].icon_color = (0.75, 0.75, 0, 1)
        save_button_state['disabled'] = self.ids['save_button_id'].disabled = False

    def update_form(self):
        """
        update_form
        args: self - self object
        purpose: update values in form
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['workout index']]
        set_index = properties['set recorder index'] = workout['set recorder index']
        if set_index is not None:
            exercises = workout['active set']
            if exercises:
                set_index = set_index if set_index <= (len(exercises) - 1) else 0
                exercise_set = exercises[set_index]
                self.ids['set_number_id'].text = str(set_index + 1)
                self.ids['exercise_name_id'].text = exercise_set['name']
                unpickleable = app.app_data_dict['unpickleable']
                none_to_val = unpickleable['dictionary manager'].none_to_val
                if exercise_set['recorded']:
                    self.set_recommended_set_from_workout_plan(unpickleable, exercise_set, none_to_val)
                else:
                    recommended_set = unpickleable['database'].get_suggestion_set(exercise_set['name'])
                    if recommended_set:
                        unpickleable['set recorder left reps'].text = none_to_val(recommended_set[0]['left_reps'])
                        unpickleable['set recorder left time'].text = self.to_min_sec(recommended_set[0]['left_time'])
                        unpickleable['set recorder left weight'].text = none_to_val(recommended_set[0]['left_weight'])
                        unpickleable['set recorder reps'].text = none_to_val(recommended_set[0]['reps'])
                        unpickleable['set recorder right reps'].text = none_to_val(recommended_set[0]['right_reps'])
                        unpickleable['set recorder right time'].text = self.to_min_sec(recommended_set[0]['right_time'])
                        unpickleable['set recorder right weight'].text = none_to_val(recommended_set[0]['right_weight'])
                        unpickleable['set recorder time'].text = self.to_min_sec(recommended_set[0]['time'])
                        unpickleable['set recorder weight'].text = none_to_val(recommended_set[0]['weight'])
                    else:
                        self.set_recommended_set_from_workout_plan(unpickleable, exercise_set, none_to_val)
                self.set_save_button(exercise_set['recorded'])
                workout['set recorder index'] = properties['set recorder index'] = set_index

    def update_set_recorder(self):
        """
        update_set_recorder
        args: self - self object
        purpose: update set recorder
        """
        app = App.get_running_app()
        workout = app.app_data_dict['workout dictionary'][app.app_data_dict['global properties']['workout index']]
        if workout['set recorder index'] is None:
            self.initialize_set_recorder()
        workout['set recorder index'] = workout['set recorder index'] \
            if workout['set recorder index'] < len(workout['active set']) else 0
        self.provision_state_store('next_button_id')
        app.app_data_dict['global properties']['set recorder states']['next_button_id']['disabled'] = (
            self.ids['next_button_id'].disabled) = False \
            if workout['set recorder index'] < (len(workout['active set']) - 1) else True
        self.provision_state_store('previous_button_id')
        app.app_data_dict['global properties']['set recorder states']['previous_button_id']['disabled'] = (
            self.ids['previous_button_id'].disabled) = False if workout['set recorder index'] else True
