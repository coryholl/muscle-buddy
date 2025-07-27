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
import bisect
import copy
import os
import textwrap
from collections import OrderedDict
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger # debug
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivymd.uix.button import MDIconButton
from kivymd.uix.button.button import MDFillRoundFlatIconButton
#local imports
import over_press
import soft_keyboard
from selector_bubble import SelectorBubble
from sound_selector import SoundSelector
from text_input_util import TextInputUtil
from workout_text_field import WorkoutTextField
from exercise_selector_popup_window import ExerciseSelectorPopupWindow

class WorkoutBuilder(FloatLayout, TextInputUtil):
    all_input_fields = OrderedDict()
    carousel_revert_index = 0
    default_color = (0.35, 0.35, 0.35, 1)
    white_color = (1, 1, 1, 1)
    exercise_group_keys = ['workout builder previous exercise group button',
        'workout builder delete exercise group button',
        'workout builder exercise group',
        'workout builder next exercise group button']
    exercise_group_selector_bubble = None
    exercise_selector_popup_window = None
    finish_sound_file_name = ''
    not_a_swipe = False
    prefix_string = 'workout builder'
    rest_insert_button = None
    row_index = 0
    set_insertion_disposition = 'replace'
    shift_exercise_text_left = True # animation direction toggle for exercise name set
    sound_selector_button = None
    sound_selector = None
    spacer1 = spacer2 = spacer3 = None
    tabata_time_label = None
    workout = []
    workout_changed = False
    workout_direction = 'next'
    workout_selector_bubble = None

    def __init__(self):
        """
        __init__
        args: self - self object
        purpose: initialize Workout Builder
        """
        Logger.info('workout_builder: __init__')
        super().__init__()
        app = App.get_running_app()
        font_size = app.app_data_dict['window height'] // 35
        button_size = app.app_data_dict['window height'] // 19
        trainers = app.app_data_dict['unpickleable']['database'].get_workout_types()
        for trainer in trainers:
            key = trainer['workout_type_type'].replace(' ', '_')
            if key in self.ids:
                self.ids[key].source = os.path.join('images', trainer['workout_type_image_file_name'])
        self.workout_selector_bubble = SelectorBubble()
        self.exercise_group_selector_bubble = SelectorBubble()
        self.exercise_selector_popup_window = ExerciseSelectorPopupWindow()
        unpickleable = app.app_data_dict['unpickleable']
        unpickleable['workout builder workout name'] = self.ids['workout_name_id']
        self.ids['workout_name_id'].bind(focus=self.set_focus)
        unpickleable['workout builder workout length'] = WorkoutTextField(font_size=font_size, hint_text='HH:MN',
            input_field_type='time', size_hint_x=0.2, text='00:00')
        unpickleable['workout builder workout length'].bind(focus=self.set_focus)
        self.create_button('workout builder previous exercise group button', 'arrow-left-drop-circle',
            unpickleable, button_size, self.previous_exercise_group_button_press, 'exercise_group_container_id')
        self.create_button('workout builder delete exercise group button', 'minus-circle', unpickleable,
            button_size, self.delete_exercise_group_button_press, 'exercise_group_container_id')
        exercise_group_name = unpickleable['workout builder exercise group'] = WorkoutTextField(font_size=font_size,
            hint_text='CIRCUIT GROUP', input_field_type='text', size_hint_x=0.7)
        exercise_group_name.bind(focus=self.set_focus)
        exercise_group_name.bind(text=self.exercise_group_text_update)
        self.ids['exercise_group_container_id'].add_widget(exercise_group_name)
        self.create_button('workout builder next exercise group button', 'arrow-right-drop-circle',
            unpickleable, button_size, self.next_exercise_group_button_press, 'exercise_group_container_id')
        unpickleable['workout builder exercise'] = self.ids['exercise_id']
        self.ids['exercise_id'].bind(focus=self.set_focus)
        set_count = unpickleable['workout builder exercise set count'] = WorkoutTextField(font_size=font_size,
            hint_text='CNT', input_field_type='int', input_filter='int', size_hint_x=0.15)
        set_count.bind(focus=self.set_focus)
        self.ids['exercise_container_id'].add_widget(set_count, index = 2)
        self.init_set_fields(self.prefix_string, font_size, app=app)
        items = [(k, v) for k, v in unpickleable.items() if k.startswith(self.prefix_string) and
            isinstance(v, WorkoutTextField)]
        for key, text_field in items:
            self.all_input_fields[key] = text_field
            text_field.disabled = True
        self.ids['workout_name_id'].disabled = False
        self.rest_insert_button = MDFillRoundFlatIconButton(disabled=True, icon='bed-clock',
            icon_color=self.white_color, icon_size=button_size, md_bg_color=self.default_color, text='insert rest',
            text_color=self.white_color)
        self.rest_insert_button.bind(on_release=self.insert_rest_set_button_press)
        self.tabata_time_label = Label(halign='center', font_size=font_size, text='total time\n00:00')
        self.spacer1 = Widget()
        self.spacer2 = Widget()
        self.spacer3 = Widget()
        self.sound_selector = SoundSelector(background_color_selection_button=self.default_color,
            background_color_toolbar=self.default_color, exit_manager=self.sound_selector_exit,
            icon_color=self.white_color, icon_selection_button='check-bold', select_path=self.sound_selector_set_path)
        self.sound_selector_button = MDFillRoundFlatIconButton(disabled=True, icon='music', icon_color=self.white_color,
            icon_size=button_size, md_bg_color=self.default_color, pos_hint={'center_x': 0.5, 'center_y': 0.5},
            text='select finish sound', text_color=self.white_color)
        self.sound_selector_button.bind(on_release=self.open_sound_selector)
        self.render_form()
        soft_keyboard.render_keyboard_shortcut(self, app=app)
        Clock.schedule_interval(self.shift_exercise_text, 4)

    def clear_form(self):
        """
        clear_form
        args: self - self object
        purpose: reset the form text fields to empty string
        """
        set_time = self.to_min_sec(0)
        for text_field in self.all_input_fields.values():
            text_field.text = set_time if text_field.input_field_type == 'time' else ''
            text_field.disabled = True
        self.ids['workout_name_id'].disabled = False
        self.render_form()

    def clear_workout(self, *kwargs):
        """
        clear_workout
        args: self - self object
            kwargs - potential additional arguments from kivy
        purpose: clear contents from workout builder
        """
        app = App.get_running_app()
        self.workout = []
        self.row_index = 0
        self.clear_form()
        app.app_data_dict['unpickleable']['confirmation popup'].dismiss()

    def clear_workout_button_press(self): # called from kv file
        """
        clear_workout_button_press
        args: self - self object
        purpose: generate confirmation window to confirm clearing of workout builder contents
        """
        Logger.info('workout_builder: clear_workout_button_press')
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
                'Clear workout builder contents?', self.clear_workout)

    def confirm_reset(self, *kwargs):
        """
        confirm_reset
        args: self - self object
            kwargs - catch additional arguments if called from Clock
        purpose: confirm app reload to make change active
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
            'Reload Muscle Buddy trainers to reflect this change?', self.reset)

    def create_button(self, key, icon, unpickleable, button_size, bind_method, parent_id):
        """
        create_button
        args: self - self object
            key - dictionary key of button to create
            icon - icon of button to create
            button_size - size of button
            bind_method - method to bind button to
            parent_id - kivy_id of parent
        purpose: create a button for workout builder
        """
        unpickleable[key] = MDIconButton(disabled=True, icon=icon, icon_size=button_size)
        unpickleable[key].bind(on_release=bind_method)
        self.ids[parent_id].add_widget(unpickleable[key])
        unpickleable[key].size_hint_x = 0.1

    def create_new_set_button_press(self, disposition): # called from kv file
        """
        create_new_set_button_press
        args: self - self object
            disposition - indicates a before or an after insertion
        purpose: create an new exercise set
        """
        if over_press.protect(vibrate=True):
            self.set_insertion_disposition = disposition
            self.sync_form_to_list()
            self.exercise_selector_popup_window.open()

    def delete_exercise_group(self, *kwargs):
        """
        delete_exercise_group
        args: self - self object
            kwargs - additional arguments sent from button press
        purpose: delete an exercise group and accompanying exercise sets from database
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            Clock.schedule_once(self.confirm_reset, 0.5)
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()
            db = app.app_data_dict['unpickleable']['database']
            workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
            workout_name = self.ids['workout_name_id'].text.strip()
            exercise_group_name = app.app_data_dict['unpickleable']['workout builder exercise group'].text.strip()
            db.delete_exercise_group(workout_type, workout_name, exercise_group_name)
            self.load_workout()

    def delete_exercise_group_button_press(self, *kwargs):
        """
        delete_exercise_group_button_press
        args: self -self object
        purpose: process delete exercise group button press
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
            'Delete exercise group from database?', self.delete_exercise_group)

    def delete_exercise_set(self, *kwargs):
        """
        delete_exercise_set
        args: self - self object
            kwargs - additional arguments sent from button press
        purpose: delete an exercise set from database
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()
            self.workout.pop(self.row_index)
            if len(self.workout):
                self.row_index = self.row_index % len(self.workout)
                self.populate_form(self.row_index)
            else:
                self.workout = []
                self.row_index = 0
                unpickleable = app.app_data_dict['unpickleable']
                title = unpickleable['workout builder workout name'].text.strip()
                time_str = unpickleable['workout builder workout length'].text.strip()
                self.clear_form()
                unpickleable['workout builder workout name'].text = title
                unpickleable['workout builder workout length'].text = time_str

    def delete_set_button_press(self, *kwargs): # called from kv file
        """
        delete_set_button_press
        args: self -self object
        purpose: process delete group button press
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
            'Delete set from database?', self.delete_exercise_set)

    def delete_workout(self, *kwargs):
        """
        delete_workout
        args: self - self object
            kwargs - additional arguments sent from button press
        purpose: delete a workout from database
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            Clock.schedule_once(self.confirm_reset, 0.5)
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()
            db = app.app_data_dict['unpickleable']['database']
            workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
            workout_name = self.ids['workout_name_id'].text.strip()
            db.delete_workout_program_exercise_sets(workout_type, workout_name)
            db.delete_workout_program_head(workout_type, workout_name)
            self.workout = []
            self.row_index = 0
            self.clear_form()
            self.render_form()

    def exercise_focus(self):
        """
        exercise_focus
        args: self - self object
        purpose: provide reusable method to trigger selection of an exercise
        """
        self.remove_widget(self.exercise_group_selector_bubble)
        self.remove_widget(self.workout_selector_bubble)
        self.ids['exercise_id'].do_cursor_movement('cursor_home')
        self.ids['exercise_id'].focus = False
        self.set_insertion_disposition = 'replace'
        self.open_muscle_selector()

    def exercise_group_bubble_press(self, bubble_button):
        """
        exercise_group_bubble_press
        args: self - self object
            bubble_button - button pressed
        purpose: process selection of exercise group
        """
        Logger.info('workout_builder: exercise_group_bubble_press: {}'.format(bubble_button))
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            if bubble_button.text != app.app_data_dict['unpickleable']['workout builder exercise group'].text.strip():
                for index, row in enumerate(self.workout):
                    if bubble_button.text == row['exercise_group_name']:
                        self.row_index = index
                        self.populate_form(index)

    def exercise_group_text_update(self, *kwargs):
        """
        exercise_group_text_update
        args: self - self object
            kwargs - other arguments from the kivy framework
        purpose: process text input to exercise group field
        """
        Logger.info('workout_builder: exercise_group_text_update')
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        if unpickleable['workout builder exercise group'].focused:
            stripped_group_name = unpickleable['workout builder exercise group'].text.strip()
            if stripped_group_name:
                groups = set([row['exercise_group_name'] for row in self.workout if
                         row['exercise_group_name'].startswith(stripped_group_name)])
                if groups:
                    self.exercise_group_selector_bubble.render_selector_bubble(self,
                        unpickleable['workout builder exercise group'], self.exercise_group_bubble_press, groups)
                else:
                    self.remove_widget(self.exercise_group_selector_bubble)
                self.workout_changed = True
            else:
                self.remove_widget(self.exercise_group_selector_bubble)
            if self.ids['exercise_id'].text.strip() == '':
                self.set_insertion_disposition = 'replace'
                self.exercise_focus()
            else:
                Logger.info(f'workout_builder: exercise_group_text_update: stripped_group_name = {stripped_group_name}')
                Logger.info(f'workout_builder: exercise_group_text_update: self.row_index = {self.row_index}')
                Logger.info(f'workout_builder: exercise_group_text_update: self.workout = {self.workout}')
                if self.row_index < len(self.workout):
                    self.workout[self.row_index]['exercise_group_name'] = stripped_group_name

    def exercise_selected(self, exercise_name, muscle_group):
        """
        exercise_selected
        args: self - self object
            exercise_name - name of exercise
            muscle_group - muscle group
        purpose: select exercise and muscle group
        """
        app = App.get_running_app()
        if (self.ids['trainer_carousel_id'].current_slide.workout_type !=
                'timed workout with timed sets and auto advance'):
            present_exercise_group_name = \
                app.app_data_dict['unpickleable']['workout builder exercise group'].text.strip()
            group_found = False
            group_index = 0
            for group_index, set in enumerate(self.workout):
                if set['exercise_group_name'] == present_exercise_group_name:
                    group_found = True
                    break
            set_found = False
            if group_found:
                for index in range(group_index, len(self.workout)):
                    set = self.workout[index]
                    if set['exercise_group_name'] == present_exercise_group_name:
                        if set['exercise_name'] == exercise_name:
                            self.row_index = index
                            self.populate_form(index)
                            set_found = True
                            self.render_form()
                            break
                    else:
                        set_found = False
                        break
            if not set_found:
                self.insert_set_into_workout_list(exercise_name, muscle_group,
                    disposition=self.set_insertion_disposition)
        else:
            self.insert_set_into_workout_list(exercise_name, muscle_group, disposition=self.set_insertion_disposition)
        self.defocus_all()
        self.set_insertion_disposition = 'replace'
        self.workout_changed = True
        self.ids['exercise_id'].do_cursor_movement('cursor_home')

    def generate_exercise_group_name(self):
        """
        generate_exercise_group_name
        args: self - self object
        purpose: generate a new exercise group name if none available
        """
        count = 1
        base_group_name = self.ids['workout_name_id'].text.strip()
        while True:
            group_name = f'{base_group_name}: group {count}'
            if not any(row['exercise_group_name'] == group_name for row in self.workout):
                break
            count += 1
        return group_name

    def insert_rest_set_button_press(self, *kwargs):
        """
        insert_rest_set_button_press
        args: self - self object
            kwargs - kivy arguments
        purpose: insert a sleep set
        """
        if over_press.protect(vibrate=True):
            self.sync_form_to_list()
            self.insert_set_into_workout_list('rest', 'Rest', disposition='after')

    def insert_set_into_workout_list(self, exercise_name, muscle_group, disposition='replace'):
        """
        insert_exercise_into_workout_list
        args: self - self object
            exercise_name - name of new exercise to insert
            muscle_group - muscle group name for exercise
            disposition - either "after", "before", "replace", or "global" indicating how to insert row
            after - indicates insertion is to occur after set row
            replace - indicates if the insertion is a replacement set
        purpose: insert new set into in memory workout set list
        """
        disposition = self.set_insertion_disposition if disposition == 'global' else disposition
        if self.workout:
            new_row = copy.deepcopy(self.workout[self.row_index])
        else:
            new_row = {
                'weight_units': 'pound',
                'exercise_group_name': self.generate_exercise_group_name()
            }
        new_row['exercise_name'] = exercise_name
        new_row['muscle_group'] = muscle_group
        for key in ('left_reps', 'left_weight', 'right_reps', 'right_weight', 'set_count', 'set_time', 'target_reps',
                'target_weight'):
            new_row[key] = None
        workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
        if workout_type == 'classic strength training':
            new_row['set_count'] = 1
        elif workout_type == 'timed workout with timed sets and auto advance':
            new_row['set_time'] = 30
        if disposition == 'after':
            if self.row_index >= len(self.workout) - 1:
                self.workout.append(new_row)
                self.row_index = len(self.workout) - 1
            else:
                self.row_index += 1
                self.workout.insert(self.row_index, new_row)
        elif disposition == 'before':
            self.workout.insert(self.row_index, new_row)
        else:
            if self.workout:
                self.workout[self.row_index] = new_row
            else:
                self.workout.append(new_row)
        self.populate_form(self.row_index)
        self.render_form()

    def insert_workout(self, *kwargs):
        """
        insert_workout
        args: self - self object
            kwargs - additional arguments sent from button press
        purpose: insert a workout into database
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            unpickleable = app.app_data_dict['unpickleable']
            unpickleable['confirmation popup'].dismiss()
            Clock.schedule_once(self.confirm_reset, 0.5)
            self.sync_form_to_list()
            db = unpickleable['database']
            workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
            workout_name = self.ids['workout_name_id'].text.strip()
            alarm_file = None if workout_type == 'classic strength training' else self.finish_sound_file_name
            hour, minute = unpickleable['workout builder workout length'].text.split(':') \
                if ':' in unpickleable['workout builder workout length'].text else (0, 0)
            length = (int(hour) * 3600) + (int(minute) * 60)
            db.store_workout_program_head(workout_type, workout_name, length, alarm_file)
            db.delete_workout_program_exercise_sets(workout_type, workout_name)
            if self.workout:
                for count, row in enumerate(self.workout):
                    row_copy = row.copy()
                    row_copy['alarm_file'] = None if workout_type == 'classic strength training' else 'boxing_bell.ogg' # change this logic for go live cjh
                    row_copy['insert_sort_index'] = count + 1
                    row_copy['exercise_group_name'] = f'{workout_name} {count}' \
                        if workout_type == 'timed workout with timed sets and auto advance' else \
                        row_copy['exercise_group_name']
                    db.insert_workout_set(workout_type, workout_name, row_copy)

    def key_press(self, _, keycode, app=None):
        """
        key_press
        args: self - self object
            - - for compatibility
            keycode - key_value
            app - optional app object
        purpose: override the parent key_press method to perform updates to tabata form timer label
        """
        super().key_press(_, keycode, app=app)
        if self.ids['trainer_carousel_id'].current_slide.workout_type == 'timed workout with timed sets and auto advance':
            key, input_field = self.find_focused_field()
            if key == 'workout builder time':
                minute, second = input_field.text.strip().split(':')
                self.workout[self.row_index]['set_time'] = (int(minute) * 60) + int(second)
                self.populate_tabata_timer_label()

    def load_workout(self, workout_name=None):
        """
        load_workout
        args: self - self object
            workout_name - optional workout program name to load
        purpose: load selected workout
        """
        app = App.get_running_app()
        workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
        workout_name = workout_name if workout_name else self.ids['workout_name_id'].text.strip()
        unpickleable = app.app_data_dict['unpickleable']
        self.workout = unpickleable['database'].get_workout_program(workout_type, workout_name)
        if self.workout:
            self.populate_form(0)
            self.row_index = 0
        self.ids['delete_workout_name_button_id'].disabled = self.ids['pound_kilogram_button_id'].disabled = \
            self.workout_changed = False
        if workout_type != 'timed workout with timed sets and auto advance':
            self.ids['reps_timer_button_id'].disabled = self.ids['left_right_button_id'].disabled = False
            if workout_type == 'timed, random, muscle confusion':
                workout_head = unpickleable['database'].get_workout_program_head(workout_type, workout_name)
                length = workout_head[0]['workout_program_time_length']
                hour = length // 3600
                minute = (length % 3600) // 60
                unpickleable['workout builder workout length'].text = f'{hour:02}:{minute:02}'
        self.render_form()
        self.set_button_statuses()

    def mount_exercise_group(self, unpickleable):
        """
        mount_exercise_group
        args: self - self object
            unpickleable - dictionary of unpickleable kivy objects
        purpose: add the widgets to edit exercise groups to the workout builder form
        """
        if self.rest_insert_button and self.rest_insert_button.parent:
            self.ids['exercise_group_container_id'].clear_widgets()
        if not unpickleable['workout builder previous exercise group button'].parent:
            for key in self.exercise_group_keys:
                self.ids['exercise_group_container_id'].add_widget(unpickleable[key])

    def next_exercise_group_button_press(self, *kwargs):
        """
        next_exercise_group_button_press
        args: self - self object
        purpose: render to the next exercise group
        """
        if over_press.protect(vibrate=True):
            self.sync_form_to_list()
            current_exercise_group = self.workout[self.row_index]['exercise_group_name']
            index = self.row_index + 1
            while len(self.workout) > index and current_exercise_group == self.workout[index]['exercise_group_name']:
                index += 1
            self.row_index = index
            self.populate_form(self.row_index)
            self.set_button_statuses()
            self.ids['exercise_id'].do_cursor_movement('cursor_home')

    def next_previous_workout(self, direction=None):
        """
        next_previous_workout
        args: self - self object
            direction - indicates if we go to next or previous exercise
        purpose: load the next or previous workout program for workout type
        """
        app = App.get_running_app()
        workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
        workouts = app.app_data_dict['unpickleable']['database'].get_workout_program_heads(workout_type)
        names = [row['workout_program_name'] for row in workouts]
        current_workout = self.ids['workout_name_id'].text.strip()
        if current_workout:
            direction = direction if direction else self.workout_direction
            if direction == 'next':
                index = (((bisect.bisect(names, current_workout) % len(names)) if current_workout in names else
                      bisect.bisect_left(names, current_workout))) % len(names)
            else:
                index = bisect.bisect_left(names, current_workout) - 1
                index = index if index >= 0 else len(names) - 1
        else:
            index = 0
        if names:
            self.load_workout(workout_name=names[index])
            self.ids['workout_name_id'].text = names[index]
            if workout_type != 'classic strength training':
                self.update_sound_file(workouts[index]['workout_program_alarm_sound_file'])
        if self.workout_changed:
            self.workout_changed = False
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()
        self.ids['exercise_id'].do_cursor_movement('cursor_home')

    def next_previous_workout_button_press(self, direction): # called from kv file
        """
        next_workout_button_press
        args: self - self object
            direction - indicates if next or previous button press
        purpose: load the previous workout program for workout type
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            if self.workout_changed:
                self.workout_direction = direction
                app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
                    'Abandon unsaved workout changes?', self.next_previous_workout, over_press_protected=True)
            else:
                self.next_previous_workout(direction=direction)

    def next_set_button_press(self, *kwargs): # called from kv file
        """
        next_set_button_press
        args: self - self object
        purpose: render to the next exercise set
        """
        if over_press.protect(vibrate=True):
            self.sync_form_to_list()
            if self.row_index < len(self.workout) - 1:
                self.row_index += 1
            self.populate_form(self.row_index)
            self.set_button_statuses()
            self.ids['exercise_id'].do_cursor_movement('cursor_home')

    def open_muscle_selector(self): #called from kv file
        """
        open_muscle_selector
        args: self - self object
        purpose: open muscle selector window for selecting exercise
        """
        Logger.info('workout_builder: open_muscle_selector called')
        if self.ids['exercise_id'].text:
            self.exercise_selector_popup_window.open_with_muscle(self.workout[self.row_index]['muscle_group'],
                self.ids['exercise_id'].text)
        else:
            self.set_insertion_disposition = 'replace'
            self.exercise_selector_popup_window.open()

    def open_sound_selector(self, *kwargs):
        """
        open_sound_selector
        args: self - self object
            kwargs - kivy arguments
        purpose: open sound selector
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            self.sound_selector.show(os.path.join(os.getcwd(), 'sounds'))

    def populate_form(self, index):
        """
        populate_form
        args: self - self object
            index - index of workout entry to populate
        purpose: populate form fields with workout values
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        row = self.workout[index]
        exercise_group = unpickleable['workout builder exercise group']
        if exercise_group.parent:
            exercise_group.disabled = False
            exercise_group.text = row['exercise_group_name']
        self.ids['exercise_id'].disabled = False
        exercise_group_count = unpickleable['workout builder exercise set count']
        none_to_val = unpickleable['dictionary manager'].none_to_val
        if exercise_group_count.parent:
            exercise_group_count.disabled = False
            exercise_group_count.text = none_to_val(row['set_count'])
        self.ids['exercise_id'].text = row['exercise_name']
        set_time = self.to_min_sec(row['set_time'])
        unpickleable['workout builder left reps'].text = none_to_val(row['left_reps'])
        unpickleable['workout builder left weight'].text = none_to_val(row['left_weight'])
        unpickleable['workout builder right reps'].text = none_to_val(row['right_reps'])
        unpickleable['workout builder right weight'].text = none_to_val(row['right_weight'])
        unpickleable['workout builder reps'].text = none_to_val(row['target_reps'])
        unpickleable['workout builder weight'].text = none_to_val(row['target_weight'])
        unpickleable['workout builder time'].text = set_time
        if row['weight_units'] == 'pound':
            self.ids['pound_kilogram_button_id'].icon = self.pound_icon
            self.ids['pound_kilogram_label_id'].text = 'pound'
        else:
            self.ids['pound_kilogram_button_id'].icon = self.kilogram_icon
            self.ids['pound_kilogram_label_id'].text = 'kilogram'

    def populate_tabata_timer_label(self):
        """
        populate_tabata_timer_label
        args: self - self object
        purpose: populate tabata timer label text with total workout length
        """
        time_length = 0
        for row in self.workout:
            time_length += row['set_time']
        minute = time_length // 60
        second = time_length % 60
        self.tabata_time_label.text = f'total time\n{minute:02d}:{second:02d}'

    def previous_exercise_group_button_press(self, *kwargs):
        """
        previous_exercise_group_button_press
        args: self - self object
        purpose: render to the previous exercise group
        """
        if over_press.protect(vibrate=True):
            self.sync_form_to_list()
            current_exercise_group = self.workout[self.row_index]['exercise_group_name']
            index = self.row_index - 1
            while index and current_exercise_group == self.workout[index]['exercise_group_name']:
                index -= 1
            self.row_index = index
            self.populate_form(self.row_index)
            self.set_button_statuses()
            self.ids['exercise_id'].do_cursor_movement('cursor_home')

    def previous_set_button_press(self, *kwargs): # used kv file
        """
        previous_set_button_press
        args: self - self object
        purpose: render to the previous exercise set
        """
        if over_press.protect(vibrate=True):
            self.sync_form_to_list()
            if self.row_index:
                self.row_index -= 1
            self.populate_form(self.row_index)
            self.set_button_statuses()

    def render_classic_form(self, set_count_field, workout_length_field, unpickleable):
        """
        render_classic_form
        args: self - self object
            set_count_field - kivy text input field for set count
            workout_length_field - workout length field
            unpickleable - unpickleable dictionary containing kivy widgets
        purpose: render a classic workout form
        """
        if not set_count_field.parent:
            self.ids['exercise_id'].size_hint_x = 0.35
            self.ids['exercise_container_id'].add_widget(set_count_field, index=2)
        if workout_length_field.parent:
            self.ids['workout_name_container_id'].remove_widget(workout_length_field)
            self.ids['workout_name_id'].size_hint_x = 0.7
        if self.sound_selector_button.parent:
            self.ids['sound_container_id'].clear_widgets()
        self.mount_exercise_group(unpickleable)
        unpickleable['workout builder exercise group'].hint_text = 'CIRCUIT GROUP'
        self.ids['reps_timer_button_id'].disabled = self.ids['left_right_button_id'].disabled = \
            not bool(self.workout)

    def render_form(self):
        """
        render_form
        self - self object
        purpose: render form based on widget statuses
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        set_count_field = unpickleable['workout builder exercise set count']
        workout_length_field = unpickleable['workout builder workout length']
        workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
        if workout_type == 'classic strength training':
            self.render_classic_form(set_count_field, workout_length_field, unpickleable)
        elif workout_type == 'timed, random, muscle confusion':
            self.render_trmc_form(set_count_field, workout_length_field, unpickleable)
        elif workout_type == 'timed workout with timed sets and auto advance':
            self.render_tabata_form(set_count_field, workout_length_field, unpickleable)
        self.ids['pound_kilogram_button_id'].disabled = not bool(self.workout)
        self.render_set_form()
        self.set_button_statuses()

    def render_tabata_form(self, set_count_field, workout_length_field, unpickleable):
        """
        render_tabata_form
        args: self - self object
            set_count_field - kivy text input field for set count
            workout_length_field - workout length field
            unpickleable - unpickleable dictionary containing kivy widgets
        purpose: render a tabata workout form
        """
        if set_count_field.parent:
            self.ids['exercise_container_id'].remove_widget(set_count_field)
            self.ids['exercise_id'].size_hint_x = 0.5
        if workout_length_field.parent:
            self.ids['workout_name_container_id'].remove_widget(workout_length_field)
            self.ids['workout_name_id'].size_hint_x = 0.7
        if not self.sound_selector_button.parent:
            self.ids['sound_container_id'].add_widget(self.sound_selector_button)
            self.sound_selector_button.disabled = False
        self.ids['exercise_group_container_id'].clear_widgets()
        self.populate_tabata_timer_label()
        self.ids['exercise_group_container_id'].add_widget(self.spacer1)
        self.ids['exercise_group_container_id'].add_widget(self.rest_insert_button)
        self.ids['exercise_group_container_id'].add_widget(self.spacer3)
        self.ids['exercise_group_container_id'].add_widget(self.tabata_time_label)
        self.ids['exercise_group_container_id'].add_widget(self.spacer2)
        self.ids['reps_timer_button_id'].icon = self.timed_on_icon
        self.ids['reps_timer_label_id'].text = self.timed_on_string
        self.ids['left_right_button_id'].icon = self.left_right_off_icon
        self.ids['left_right_label_id'].text = self.left_right_off_string
        self.ids['reps_timer_button_id'].disabled = self.ids['left_right_button_id'].disabled = True

    def render_trmc_form(self, set_count_field, workout_length_field, unpickleable):
        """
        render_trmc_form
        args: self - self object
            set_count_field - kivy text input field for set count
            workout_length_field - workout length field
            unpickleable - unpickleable dictionary containing kivy widgets
        purpose: render a timed random muscle confusion workout form
        """
        if set_count_field.parent:
            self.ids['exercise_container_id'].remove_widget(set_count_field)
            self.ids['exercise_id'].size_hint_x = 0.5
        if not workout_length_field.parent:
            self.ids['workout_name_id'].size_hint_x = 0.5
            self.ids['workout_name_container_id'].add_widget(workout_length_field, index=2)
        if not self.sound_selector_button.parent:
            self.ids['sound_container_id'].add_widget(self.sound_selector_button)
            self.sound_selector_button.disabled = False
        self.mount_exercise_group(unpickleable)
        unpickleable['workout builder exercise group'].hint_text = 'EXERCISE GROUP'
        self.ids['reps_timer_button_id'].disabled = self.ids['left_right_button_id'].disabled = \
            not bool(self.workout)

    def reset(self, *kwargs):
        """
        reset
        args: self - self object
            kwargs - additional argument set from button press
        purpose: performs partial app reset to allow new workout changes to work
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            Clock.schedule_once(app.reload_workout_widgets, 0.2)

    def revert_trainer(self, *kwargs):
        """
        revert_trainer
        args: self - self object
            kwargs - arguments from kivy engine
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].dismiss()
        self.not_a_swipe = True
        self.ids['trainer_carousel_id'].index = self.carousel_revert_index

    def set_button_statuses(self):
        """
        set_button_statuses
        args: self - self object
        purpose: activate and inactivate form button based on app state
        """
        app = App.get_running_app()
        self.set_workout_name_buttons()
        self.set_exercise_group_nav_buttons(app)
        self.set_exercise_group_insert_delete_buttons(app)
        self.set_insert_button_state()
        self.set_exercise_nav_buttons()
        self.set_exercise_insert_delete_buttons(app)
        self.ids['insert_workout_name_button_id'].disabled = not self.workout_changed

    def set_carousel_swipe(self, trainer_index): # called from workout_builder.kv
        """
        set_carousel_swipe
        args: self - self object
            trainer_index - carousel index of trainer
        purpose: handle trainer type swipe
        """
        Logger.info(f'workout_builder: set_carousel_swipe: {trainer_index}')
        if self.not_a_swipe:
            self.not_a_swipe = False
        else:
            if self.workout_changed:
                app = App.get_running_app()
                app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
                    'Abandon unsaved workout changes?', self.set_trainer, cancel_bind_method=self.revert_trainer)
            else:
                self.set_trainer()

    def set_exercise_group_insert_delete_buttons(self, app):
        """
        set_exercise_group_insert_delete_buttons
        args: self - self object
            app - app object
        purpose: set insert and delete buttons for exercise group name
        """
        unpickleable = app.app_data_dict['unpickleable']
        unpickleable['workout builder delete exercise group button'].disabled = True
        if unpickleable['workout builder delete exercise group button'].parent:
            workout_name = self.ids['workout_name_id'].text.strip()
            if workout_name:
                exercise_group = unpickleable['workout builder exercise group'].text.strip()
                if exercise_group:
                    workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
                    result = unpickleable['database'].get_exercise_set_group(workout_type, workout_name, exercise_group)
                    unpickleable['workout builder delete exercise group button'].disabled = not bool(result)

    def set_exercise_group_nav_buttons(self, app):
        """
        set_exercise_group_nav_buttons
        args: self - self object
            app - app object
        purpose: set state of exercise group navigation buttons
        """
        next_group_button = app.app_data_dict['unpickleable']['workout builder next exercise group button']
        prev_group_button = app.app_data_dict['unpickleable']['workout builder previous exercise group button']
        if self.workout:
            current_group_name = self.workout[self.row_index]['exercise_group_name']
            next_group_button.disabled = not any(current_group_name != self.workout[index]['exercise_group_name']
                for index in range(self.row_index, len(self.workout)))
            prev_group_button.disabled = not any(current_group_name != self.workout[index]['exercise_group_name']
                for index in range(self.row_index - 1, -1, -1))
        else:
            next_group_button.disabled = prev_group_button.disabled = True

    def set_exercise_insert_delete_buttons(self, app):
        """
        set_exercise_insert_delete_buttons
        args: self - self object
            app - app object
        purpose: set statuses for buttons for updating exercise set field
        """
        exercise_name = self.ids['exercise_id'].text.strip()
        self.ids['create_after_exercise_button_id'].disabled = self.ids['create_before_exercise_button_id'].disabled = \
            self.ids['delete_exercise_id'].disabled = not bool(exercise_name)

    def set_exercise_nav_buttons(self):
        """
        set_exercise_nav_buttons
        args: self - self object
            app - app object
        purpose: set state of exercise navigation buttons
        """
        self.ids['previous_exercise_id'].disabled = not bool(self.row_index)
        self.ids['next_exercise_id'].disabled = self.row_index >= len(self.workout) - 1

    def set_insert_button_state(self):
        """
        set_insert_button_state
        args: self - self object
        purpose: set the insert button state based on form state
        """
        workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
        if workout_type != 'timed workout with timed sets and auto advance' or not self.workout or \
            self.ids['exercise_id'].text == 'rest' or (
                self.row_index + 1 < len(self.workout) and self.workout[self.row_index + 1]['exercise_name'] == 'rest'):
            self.rest_insert_button.disabled = True
        else:
            self.rest_insert_button.disabled = False

    def set_focus(self, input_field, *kwargs):
        """
        set_focus
        args: self - self object
            input_field - kivy input field object
            kwargs - event arguments
        purpose: add status setting for muscle selector button when appropriate
        """
        if super().set_focus(input_field, *kwargs):
            app = App.get_running_app()
            unpickleable = app.app_data_dict['unpickleable']
            if self.ids['exercise_id'].focus:
                self.exercise_focus()
            elif unpickleable['workout builder exercise group'].focus:
                if self.ids['exercise_id'].text.strip() == '':
                    self.exercise_focus()
                else:
                    self.exercise_group_text_update()
                self.remove_widget(self.workout_selector_bubble)
                if not unpickleable['workout builder exercise group'].text.strip():
                    unpickleable['workout builder exercise group'].text = self.generate_exercise_group_name()
            elif self.ids['workout_name_id'].focus:
                self.workout_name_text_update()
                self.remove_widget(self.exercise_group_selector_bubble)
            else:
                self.remove_widget(self.exercise_group_selector_bubble)
                self.remove_widget(self.workout_selector_bubble)

    def set_trainer(self, *kwargs):
        """ 
        set_trainer
        args: self - self object
            kwargs - additional arguments sent from kivy runtime system
        purpose: set the correct workout builder context
        """
        app = App.get_running_app()
        Logger.info('workout_builder: set_trainer')
        self.workout = []
        self.row_index = 0
        self.clear_form()
        self.defocus_all(skip_defocus=self.ids['workout_name_id'], disable=True)
        self.ids['workout_name_id'].text = ''
        self.sound_selector_button.text = 'select finish sound'
        self.activate_keyboards(self.ids['workout_name_id'])
        self.carousel_revert_index = self.ids['trainer_carousel_id'].index
        self.workout_changed = False
        app.app_data_dict['unpickleable']['confirmation popup'].dismiss()

    def set_workout_name_buttons(self):
        """
        set_workout_name_buttons
        args: self - self object
        purpose: set status of workout name insertion and deletion buttons
        """
        app = App.get_running_app()
        stripped_workout_name = self.ids['workout_name_id'].text.strip()
        if stripped_workout_name:
            result = app.app_data_dict['unpickleable']['database'].get_workout_program_head(
                self.ids['trainer_carousel_id'].current_slide.workout_type, stripped_workout_name)
            self.ids['delete_workout_name_button_id'].disabled = not bool(result)
            self.ids['insert_workout_name_button_id'].disabled = not bool(self.workout)
        else:
            self.ids['delete_workout_name_button_id'].disabled = (
                self.ids['insert_workout_name_button_id'].disabled) = True

    def shift_exercise_text(self, dt):
        """
        shift_exercise_text
        args: self - self object
            dt - time since last call
        purpose: shift exercise text so it can be read on small interfaces
        """
        self.shift_exercise_text_left ^= True
        shift_command = 'cursor_home' if self.shift_exercise_text_left else 'cursor_end'
        self.ids['exercise_id'].do_cursor_movement(shift_command)

    def sound_selector_exit(self, *kwargs):
        """
        sound_selector_exit
        args: self - self object
            kwargs - kivy arguments
        purpose: handle exiting of sound selector
        """
        if over_press.protect(vibrate=True):
            self.sound_selector.close()

    def sound_selector_set_path(self, sound_file_path):
        """
        sound_selector_set_path
        args: self - self object
            sound_file_path - selected sound file
        purpose: handle selection of sound file
        """
        Logger.info(f'workout_builder: sound_selector_set_path: {sound_file_path}')
        self.update_sound_file(sound_file_path)
        self.sound_selector.close()
        self.set_button_statuses()

    def sync_form_to_list(self):
        """
        sync_form_to_list
        self - self object
        purpose: copy kivy object content to python workout list row
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        if self.workout:
            row = self.workout[self.row_index]
            row['set_count'] = self.text_to_num(unpickleable['workout builder exercise set count'].text.strip())
            row['left_weight'] = self.text_to_num(unpickleable['workout builder left weight'].text.strip(),
                num_type='float')
            row['left_reps'] = self.text_to_num(unpickleable['workout builder left reps'].text.strip())
            row['right_weight'] = self.text_to_num(unpickleable['workout builder right weight'].text.strip(),
                num_type='float')
            row['right_reps'] = self.text_to_num(unpickleable['workout builder right reps'].text.strip())
            row['target_weight'] = self.text_to_num(unpickleable['workout builder weight'].text.strip(),
                num_type='float')
            row['target_reps'] = self.text_to_num(unpickleable['workout builder reps'].text.strip())
            minute, second = unpickleable['workout builder time'].text.strip().split(':')
            row['set_time'] = (int(minute) * 60) + int(second)
            row['weight_units'] = self.ids['pound_kilogram_label_id'].text
            self.workout_changed = True

    def text_to_num(self, text, num_type='int'):
        """
        text_to_num
        args: self - self object
            text - text may contain a number
            num_type - 'int' or 'float' indicating what type of number to convert to
        purpose: convert a string to a number object
        returns: an int, float, or None
        """
        if text:
            retval = int(text) if num_type == 'int' else float(text)
        else:
            retval = None
        return retval

    def update_sound_file(self, sound_file_path):
        """
        update_sound_file
        args: self - self object
            sound_file_path - path to sound file
        purpose: update sound file data sources display and future storage
        """
        self.finish_sound_file_name = sound_file_path
        file_name = os.path.basename(sound_file_path)
        self.sound_selector_button.text = textwrap.shorten(file_name, width=35, placeholder="...") \
            if file_name else 'select sound file'
        self.workout_changed = True

    def workout_bubble_press(self, bubble_button):
        """
        workout_bubble_press
        args: self - self object
            bubble_button - button pressed
        purpose: process selection of a workout
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            self.ids['workout_name_id'].text = bubble_button.text
            workout_head = app.app_data_dict['unpickleable']['database'].get_workout_program_head(
                self.ids['trainer_carousel_id'].current_slide.workout_type, bubble_button.text)
            if self.ids['trainer_carousel_id'].current_slide.workout_type != 'classic strength training':
                self.update_sound_file(workout_head[0]['workout_program_alarm_sound_file'])
            self.defocus_all()
            self.load_workout()

    def workout_delete_button_press(self): # called from kv file
        """
        workout_delete_button_press
        args: self - self object
        purpose: process workout delete button press
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
            'Delete workout program from database?', self.delete_workout)

    def workout_insert_button_press(self): # called from kv file
        """
        workout_insert_button_press
        args: self - self object
        purpose: process workout insert button press
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
            'Insert new workout program into database?', self.insert_workout)

    def workout_name_text_update(self): # called from workout_builder.kv
        """
        workout_name_text_update
        args: self - self object
        purpose: handle text changes in workout name text input
        """
        Logger.info('workout_builder: workout_name_text_update')
        stripped_workout_name = self.ids['workout_name_id'].text.strip()
        if stripped_workout_name:
            app = App.get_running_app()
            unpickleable = app.app_data_dict['unpickleable']
            workout_type = self.ids['trainer_carousel_id'].current_slide.workout_type
            self.ids['exercise_id'].disabled = False
            if workout_type == 'timed workout with timed sets and auto advance':
                self.set_insert_button_state()
            else:
                unpickleable['workout builder exercise group'].disabled = False
                if workout_type == 'timed, random, muscle confusion':
                    unpickleable['workout builder workout length'].disabled = False
            workout_matches = unpickleable['database'].get_workout_program_selector_bubble(stripped_workout_name,
                workout_type, app.app_data_dict['config']['selection bubble']['selection limit'])
            if workout_matches:
                workout_names = [workout['workout_program_name'] for workout in workout_matches]
                self.workout_selector_bubble.render_selector_bubble(self, self.ids['workout_name_id'],
                    self.workout_bubble_press, workout_names)
            else:
                self.remove_widget(self.workout_selector_bubble)
            self.workout_changed = True
        else:
            self.defocus_all(skip_defocus=self.ids['workout_name_id'], disable=True, disable_keyboards=False)
            self.rest_insert_button.disabled = True
        self.set_button_statuses()
