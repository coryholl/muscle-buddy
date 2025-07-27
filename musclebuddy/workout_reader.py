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
import datetime
from kivy.app import App
from kivy.logger import Logger #debug
from kivy.uix.floatlayout import FloatLayout
# local imports
import over_press
import soft_keyboard
from text_input_util import TextInputUtil

class WorkoutReader(FloatLayout, TextInputUtil):
    all_input_fields = {}
    keyboard_button = None

    def __init__(self):
        """
        __init__
        args: self - self object
        purpose: initialize Workout Reader
        """
        Logger.info('workout_reader: __init__')
        super().__init__()
        self.all_input_fields['exercise name'] = self.ids['exercise_name_id']
        self.build_list(None)
        self.keyboard_button = soft_keyboard.render_keyboard_shortcut(self)

    def build_list(self, data):
        """
        build_list
        args: self - self object
            data - data to match on
        purpose: generate a list of exercises
        """
        Logger.info('workout_reader: build_list')
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        set_history = unpickleable['database'].get_workout_history()
        scale = app.app_data_dict['window height'] // 58
        workout_list = []
        data_lower = data.lower() if type(data) == str else None
        is_None = (data is None)
        is_date = (type(data) == datetime.date)
        is_str = (type(data) == str)
        count = 0
        for work_set in set_history:
            if (is_None or (is_date and str(data) == work_set['exercise_date']) or
                    (is_str and data_lower in work_set['exercise_name'].lower())):
                first_line = '[size={}]{}: {}[/size]'.format(scale,
                    unpickleable['dictionary manager'].none_to_val(work_set['exercise_date']),
                    unpickleable['dictionary manager'].none_to_val(work_set['exercise_name']))
                weight_abbreviation = '' if work_set['weight_unit'] is None else \
                    app.app_data_dict['weight units'][work_set['weight_unit']]['abbreviation']
                second_line = f'[size={scale}]'
                if not any(work_set[key] is not None for key in ('left_weight', 'left_time', 'left_reps',
                        'right_weight', 'right_time', 'right_reps')):
                    second_line += '{}'.format(self.build_rep_line(work_set, weight_abbreviation, 'weight',
                        'time', 'reps'))
                else:
                    if any(work_set[key] is not None for key in ('left_weight', 'left_time', 'left_reps')):
                        second_line += 'left: {}'.format(self.build_rep_line(work_set, weight_abbreviation,
                            'left_weight', 'left_time', 'left_reps'))
                    if any(work_set[key] is not None for key in ('right_weight', 'right_time', 'right_reps')):
                        if any(work_set[key] for key in ('left_weight', 'left_time', 'left_reps')):
                            second_line += ' | '
                        second_line += 'right: {}'.format(self.build_rep_line(work_set, weight_abbreviation,
                            'right_weight', 'right_time', 'right_reps'))
                second_line += '[/size]'
                workout_list.append({'secondary_text': second_line, 'text': first_line, 'viewclass': 'TwoLineListItem'})
                count += 1
                if count > 100:
                    break
        self.ids['recycle_view_id'].data = workout_list
        over_press.set_protect(app = app) # fixes timing issue on PineTab2

    def build_rep_line(self, work_set, weight_abbreviation, weight_key, time_key, reps_key):
        """
        build_rep_line
        args: self - self object
            work_set - dictionary of the work set performed
            weight_abbreviation - abbreviation of the weight unit for display purposes
            weight_key - dictionary key of the weight unit
            time_key - dictionary key of time length of set
            reps_key - dictionary key of reps performed
        purpose: format string for use in reporting set
        """
        line = ''
        if work_set[weight_key]:
            line += '{} {} '.format(work_set[weight_key], weight_abbreviation)
        if work_set[time_key]:
            minutes = work_set[time_key] // 60
            seconds = work_set[time_key] % 60
            line += 'X {}:{:02d}'.format(minutes, seconds)
        elif work_set[reps_key]:
            line += 'X {} '.format(work_set[reps_key])
        return line

    def on_cancel(self, instance, value):
        """
        on_cancel
        args: self - self object
            instance - unused MDDatePicker object reference
            value - unused returned value
        purpose: binds to cancel button on date picker
        """
        Logger.info('workout_reader: on_cancel')
        if over_press.protect(vibrate=True):
            self.ids['exercise_name_id'].focus = False

    def on_save(self, instance, date, date_range):
        """
        on_save
        args: self - self object
            instance - unused MDDatePicker object reference
            date - selected date string in ISO format
            date_range - empty date range
        purpose: display exercises performed on a specific date
        """
        Logger.info('workout_reader: on_save')
        if over_press.protect(vibrate=True):
            self.ids['exercise_name_id'].focus = False
            self.build_list(date)

    def recycle_view_touch(self, recycle_view, touch): # called from workout_reader.kv
        """
        recycle_view_touch
        args: self - self object
            recycle_view - recycle view object
            touch - touch object
        purpose: do actions necessary for a scroll event
        """
        Logger.info('workout_reader: recycle_view_touch recycle_view: {}, touch: {}'.format(recycle_view, touch))
        if (not self.keyboard_button.collide_point(touch.x, touch.y) and
                recycle_view.collide_point(touch.x, touch.y) and over_press.protect(vibrate=True)):
            self.defocus_all()

    def select_date(self): # called from workout_reader.kv
        """
        select_date
        args: self - self object
        purpose: open selection calendar for workout history
        """ 
        Logger.info('workout_reader: select_date')
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            soft_keyboard.remove_soft_keyboard()
            date_dialog = app.app_data_dict['unpickleable']['date dialog']
            self.ids['exercise_name_id'].focus = False
            date_dialog.title_input = 'Input Date'
            date_dialog.title = 'Select Date of Workout'
            date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
            date_dialog.open()

    def text_search(self):
        """
        text_search
        args: self - self object
        purpose: provide a text search function bound to a button
        """
        if over_press.protect(vibrate=True):
            self.build_list(self.ids['exercise_name_id'].text)
