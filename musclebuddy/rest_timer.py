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
from kivy.utils import get_hex_from_color
# local imports
import stateful_clock
from timer import Timer

class RestTimer(Timer):
    """
    RestTimer
    purpose: class for creating timers for timing rest
    """
    end_time = 0 #app.app_data_dict['global properties']['rest end time']
    time_length = 60 #app.app_data_dict['global properties']['rest time length']
    state = 'not started' #app.app_data_dict['global properties']['rest timer state']
    time_left = 0 #app.app_data_dict['global properties']['rest time left']
    time_pad_str = '00:00.0'
    max_timer_index = 4
    time_regular_expression = r'(\d\d):([0-5]\d)'

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
        purpose: initialize workout timer restoring state on Android if necessary
        """
        super(Timer, self).__init__(**kwargs)
        app = App.get_running_app()
        self.end_time = app.app_data_dict['global properties']['rest end time']
        self.state = app.app_data_dict['global properties']['rest timer state']
        self.time_left = app.app_data_dict['global properties']['rest time left']
        self.time_length = app.app_data_dict['global properties']['rest time length']
        app.workout_rest_timer = self.format_time_msd(60, self.timer_text_color)
        stateful_clock.restore_clock(self.get_time)
        stateful_clock.restore_clock(self.timer_paused_indicator)
        stateful_clock.restore_clock(self.finished_visual_alarm)

    def format_time(self, seconds, color, sign):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of time text
            sign - sign to prefix the string with
        purpose: create a time string for a rest timer
        returns: string to display in timer label
        """
        return self.format_time_msd(seconds, color)

    def get_time(self, dt):
        """
        get_time
        args: self - self object
            dt - time since last callback
        purpose: generate the label for set countdown
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        properties['rest time left'] = self.time_left = self.end_time - time.time()
        if self.time_left > 0:
            properties['workout rest timer'] = app.workout_rest_timer = \
                self.format_time_msd(self.time_left, self.timer_text_color)
        else:
            unpickleable = app.app_data_dict['unpickleable']
            properties['rest timer state'] = self.state = 'finish'
            properties['rest time left'] = properties['rest end time'] = self.time_left = self.end_time = 0
            stateful_clock.unschedule(self.get_time)
            unpickleable['sound'].play_sound('cloister_bell.ogg')
            stateful_clock.schedule_interval(self.finished_visual_alarm, 0.05)
            properties['workout rest timer'] = app.workout_rest_timer = \
                self.format_time_msd(self.time_left, self.timer_text_color)
            unpickleable['vibrator'].vibrate('alarm')

    def key_press(self, keyboard, keycode, *args):
        """
        key_press
        args: self - self object
            keyboard - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process number pad's key press
        """
        Logger.info('rest_timer: key_press {}, timer_index {}, time_pad_str {}'.format(keycode, self.timer_index,
                                                                                       self.time_pad_str))
        super().key_press(keyboard, keycode, args)
        app = App.get_running_app()
        app.workout_rest_timer = self.markup_timer

    def set_timer_paused_indicator(self, time_left, timer_text_color):
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation

        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout rest timer'] = app.workout_rest_timer = \
            self.format_time_msd(time_left, timer_text_color)

    def stop_alarm(self): # called from timer.py
        """
        stop_alarm
        args: self - self object
        purpose: implement a shutdown mechanism for rest timer
        """
        app = App.get_running_app()
        stateful_clock.unschedule(self.finished_visual_alarm)
        stateful_clock.unschedule(self.get_time)
        stateful_clock.unschedule(self.timer_paused_indicator) 
        self.timer_background_color = (0, 0, 0)
        self.timer_text_color = get_hex_from_color((1, 1, 1))
        app.app_data_dict['global properties']['rest time left'] = self.time_left = self.time_length
        app.app_data_dict['unpickleable']['sound'].stop_sound('cloister_bell.ogg')

    def store_time_left_state(self):
        """
        store_time_left_state
        args: self - self object
            time_left - time remaining
        purpose: save rest time left state for Android pause
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['rest time left'] = self.time_left

    def timer_on_touch_up(self, touch, touch_type, app): # called from Kivy engine
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a set timer
        """
        self.timer_on_touch_up2(touch, touch_type, app)
        properties = app.app_data_dict['global properties']
        properties['rest timer state'] = self.state
        properties['rest time left'] = self.time_left
        properties['rest end time'] = self.end_time
        properties['workout rest timer'] = app.workout_rest_timer = \
            self.format_time_msd(self.time_left, self.timer_text_color)

    def timer_paused_indicator(self, dt):
        """
        timer_paused_indicator
        args: self - self object
            dt - time since last callback call
        purpose: provide method mapping so state is retained for Android pause
        """
        super().timer_paused_indicator(dt)
