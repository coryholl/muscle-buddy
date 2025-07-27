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
import time
from kivy.app import App
from kivy.logger import Logger
# local imports
import stateful_clock
import workout_trainer_util
from timer import Timer

class WorkoutTimer(Timer):
    """
    WorkoutTimer
    purpose: class for a timer for timing a full workout
    """
    end_time = 0 #app.app_data_dict['global properties']['workout end time']
    state = 'not started' #app.app_data_dict['global properties']['workout timer state']
    time_left = 0 #app.app_data_dict['global properties']['workout time left']
    max_timer_index = 7
    time_regular_expression = r'(\d\d):([0-5]\d):([0-5]\d)'

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
        purpose: initialize workout timer restoring state on Android if necessary
        """
        super(Timer, self).__init__(**kwargs)
        app = App.get_running_app()
        self.end_time = app.app_data_dict['global properties']['workout end time']
        self.state = app.app_data_dict['global properties']['workout timer state']
        self.time_left = app.app_data_dict['global properties']['workout time left']
        stateful_clock.restore_clock(self.get_time)
        stateful_clock.restore_clock(self.timer_paused_indicator)
        stateful_clock.restore_clock(self.finished_visual_alarm)
        stateful_clock.restore_clock(self.get_negative_workout_time)
        time_left = self.end_time - time.time()
        if self.state == 'run' and time_left < 0:
            app.app_data_dict['global properties']['workout timer state'] = self.state = 'finish'
            stateful_clock.unschedule(self.get_time)
            stateful_clock.schedule_interval(self.finished_visual_alarm, 0.05)
            stateful_clock.schedule_interval(self.get_negative_workout_time, 1)

    def format_time(self, seconds, color, sign):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of time text
            sign - sign to prefix the string with
        purpose: create a time string for a workout timer
        returns: string to display in timer label
        """
        hour = int(seconds // 3600)
        minute = int((seconds % 3600) // 60)
        second = int(seconds % 60)
        self.time_pad_str = temp_time_str = f'{hour:02d}:{minute:02d}:{second:02d}'
        if self.state == 'pause':
            cursor_color = color[:5] + '00'
            temp_time_str = (temp_time_str[:self.timer_index] + f'[color={cursor_color}]' +
                             temp_time_str[self.timer_index] + f'[/color]' + temp_time_str[self.timer_index + 1:])
        elif self.state == 'run':
            app = App.get_running_app()
            app.trainer_state = workout_trainer_util.gen_spinner()
        return f'{sign}[color={color}]{temp_time_str}[/color]'

    def get_negative_workout_time(self, dt):
        """
        get_negative_stopwatch_time
        args: self - self object
            dt - time since last callback call
        purpose: generate a stopwatch for showing how much time has progressed since workout time ran out
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout time left'] = self.time_left = time.time() - self.end_time
        app.app_data_dict['global properties']['workout timer'] = app.workout_timer = (
            self.format_time(self.time_left, self.timer_text_color, '-'))

    def get_time(self, dt):
        """
        get_time
        args: self - self object
            dt - time since last callback call
        purpose: generate time string to dislay in workout timer label
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout time left'] = self.time_left = self.end_time - time.time()
        if not int(self.time_left):
            app.app_data_dict['global properties']['workout timer state'] = self.state = 'finish'
            try:
                self.parent.play_workout_alarm() # may need to be replaced for reuse purposes
            except Exception as e:
                try:
                    self.parent.parent.play_workout_alarm()
                except Exception as e:
                    try:
                        self.parent.parent.parent.play_workout_alarm()
                    except Exception as e:
                        Logger.error('workout_timer: play_workout_alarm method failure')
            stateful_clock.unschedule(self.get_time)
            stateful_clock.schedule_interval(self.finished_visual_alarm, 0.05)
            stateful_clock.schedule_interval(self.get_negative_workout_time, 1)
        app.app_data_dict['global properties']['workout timer'] = app.workout_timer = (
            self.format_time(self.time_left, self.timer_text_color, ''))

    def key_press(self, keyboard, keycode, *args):
        """
        key_press
        args: self - self object
            keyboard - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process number pad's key press
        """
        Logger.info(f'workout_timer: key_press {keycode}, timer_index {self.timer_index}, time_pad_str {self.time_pad_str}')
        super().key_press(keyboard, keycode, args)
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout timer'] = app.workout_timer = self.markup_timer

    def parse_time_string(self, time_str):
        """
        parse_time_string
        args: self - self object
            time_str - hh:mm:ss formated time string
        purpose: turn a time string into seconds
        returns: seconds represented by time string
        """
        Logger.info('workout_timer: parse_time_string {}'.format(time_str))
        return (int(time_str[:2]) * 3600) + (int(time_str[3:][:2]) * 60) + int(time_str[6:])

    def set_timer_paused_indicator(self, time_left, timer_text_color): # called from timer.py
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout timer'] = app.workout_timer = (
            self.format_time(time_left, timer_text_color, ''))

    def store_time_left_state(self): # called from timer.py
        """
        store_time_left_state
        args: self - self object
        purpose: save workout time left state for Android pause
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout time left'] = self.time_left

    def timer_on_touch_up(self, touch, touch_type, app): # called from timer.py
        """
        workout_timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a workout timer
        """
        super().timer_on_touch_up(touch, touch_type, app)
        app.app_data_dict['global properties']['workout timer state'] = self.state
        app.app_data_dict['global properties']['workout time left'] = self.time_left
        app.app_data_dict['global properties']['workout end time'] = self.end_time
        app.app_data_dict['global properties']['workout timer'] = app.workout_timer = (
            self.format_time(self.time_left, self.timer_text_color, '-' if self.state in ('finish', 'shutdown') else ''))

    def timer_paused_indicator(self, dt):
        """
        timer_paused_indicator
        args: self - self object
            dt - time since last callback call
        purpose: provide method mapping so state is retained for Android pause
        """
        super().timer_paused_indicator(dt)
