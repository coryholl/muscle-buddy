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
from kivy.utils import get_hex_from_color
# local imports
import stateful_clock
import workout_trainer_util
from timer import Timer

class StopWatch(Timer):
    start_time = 0
    time_elapsed = 0
    timer_text_color = get_hex_from_color((1, 1, 1))
    pause_time = 0
    state = 'not started'

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
        purpose: initialize workout timer restoring state on Android if necessary
        """
        super(Timer, self).__init__(**kwargs)
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['stopwatch'] = self

    def format_time(self, seconds, color, sign):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of text
            sign - unused for compatibility
        purpose: create a time string for a workout timer
        returns: string to display in timer label
        """
        hour, minute, second, decisecond = self.breakdown_time(seconds)
        hour %= 10
        if self.state == 'run':
            app = App.get_running_app()
            app.timers_state = workout_trainer_util.gen_spinner()
        return f'[color={color}]{hour:01d}:{minute:02d}:{second:02d}.{decisecond:01d}[/color]'

    def get_time(self, dt):
        """
        get_time
        args: self - self object
            dt - time since last callback call
        purpose: generate time string to display in stopwatch label
        """
        app = App.get_running_app()
        self.time_elapsed = time.time() - self.start_time
        app.generic_stopwatch = self.format_time(self.time_elapsed, self.timer_text_color, None)

    def set_timer_paused_indicator(self, seconds, timer_text_color): # called from timer.py
        """
        set_timer_paused_indicator
        args: self - self object
            seconds - time in stopwatch
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation
        """
        app = App.get_running_app()
        app.generic_stopwatch = self.format_time(seconds, timer_text_color, None)

    def timer_on_touch_up(self, touch, touch_type, app):
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for stopwatch
        """
# Python 3.10 syntax commented out for future restore
#        match self.state:
#            case 'finish':
#                self.state = 'shutdown'
#            case 'not started':
#                if touch_type == 'press':
#                    self.state = 'run'
#                    self.start_time = time.time()
#                    self.time_elapsed = 0
#                    app.generic_stopwatch = self.format_time(0,  self.timer_text_color, None)
#                    stateful_clock.schedule_interval(self.get_time, 0.1)
#            case 'pause':
#                if touch_type == 'press':
#                    self.state = 'run'
#                    self.start_time += time.time() - self.pause_time
#                    stateful_clock.unschedule(self.timer_paused_indicator)
#                    self.timer_text_color = get_hex_from_color((1, 1, 1))
#                    app.generic_stopwatch = self.format_time(self.time_elapsed, self.timer_text_color, None)
#                    stateful_clock.schedule_interval(self.get_time, 0.1)
#                elif touch_type == 'left':
#                    self.state = 'not started'
#                    self.time_elapsed = 0
#                    stateful_clock.unschedule(self.timer_paused_indicator)
#                    self.timer_text_color = get_hex_from_color((1, 1, 1))
#                    app.generic_stopwatch = self.format_time(0, self.timer_text_color, None)
#            case 'run':
#                if touch_type == 'press':
#                    self.state = 'pause'
#                    self.pause_time = time.time()
#                    self.time_left = self.time_elapsed
#                    stateful_clock.unschedule(self.get_time)
#                    stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
#            case 'shutdown':
#                pass
# start old Python syntax
        if self.state == 'finish':
            self.state = 'shutdown'
        elif self.state == 'not started':
            if touch_type == 'press':
                self.state = 'run'
                self.start_time = time.time()
                self.time_elapsed = 0
                app.generic_stopwatch = self.format_time(0,  self.timer_text_color, None)
                stateful_clock.schedule_interval(self.get_time, 0.1)
        elif self.state == 'pause':
                if touch_type == 'press':
                    self.state = 'run'
                    self.start_time += time.time() - self.pause_time
                    stateful_clock.unschedule(self.timer_paused_indicator)
                    self.timer_text_color = get_hex_from_color((1, 1, 1))
                    app.generic_stopwatch = self.format_time(self.time_elapsed, self.timer_text_color, None)
                    stateful_clock.schedule_interval(self.get_time, 0.1)
                elif touch_type == 'left':
                    self.state = 'not started'
                    self.time_elapsed = 0
                    stateful_clock.unschedule(self.timer_paused_indicator)
                    self.timer_text_color = get_hex_from_color((1, 1, 1))
                    app.generic_stopwatch = self.format_time(0, self.timer_text_color, None)
        elif self.state == 'run':
            if touch_type == 'press':
                self.state = 'pause'
                self.pause_time = time.time()
                self.time_left = self.time_elapsed
                stateful_clock.unschedule(self.get_time)
                stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
        elif self.state == 'shutdown':
            pass
# end old Python syntax

    def fix_tabata_switch(self):
        """
        fix_tabata_switch
        args: self - self object
        purpose: fix tabata trainer timer reset which is used to fix trainers upon switching
        """
        if self.state == 'run':
            stateful_clock.unschedule(self.timer_paused_indicator)
            self.timer_text_color = get_hex_from_color((1, 1, 1))
            app = App.get_running_app()
            app.generic_stopwatch = self.format_time(self.time_elapsed, self.timer_text_color, None)
            stateful_clock.schedule_interval(self.get_time, 0.1)