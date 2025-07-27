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
import workout_trainer_util
from timer import Timer

class GenericTimer(Timer):
    """
    RestTimer
    purpose: class for creating timers for timing rest
    """
    end_time = 0 #app.app_data_dict['global properties']['generic timer end time']
    timer_length = 60 #app.app_data_dict['global properties']['generic timer time length']
    state = 'not started' #app.app_data_dict['global properties']['generic timer state']
    time_left = 60 #app.app_data_dict['global properties']['generic timer time left']
    stopwatch_start_time = 0
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
        stateful_clock.restore_clock(self.get_time)
        app.app_data_dict['unpickleable']['generic timer'] = self

    def format_time(self, seconds, color, *args):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of time text
            args - possible sign, may be missing
        purpose: create a time string for a workout timer
        returns: string to display in timer label
        """
        timer_str = super().format_time(seconds, color, '')
        app = App.get_running_app()
        app.app_data_dict['global properties']['generic timer'] = timer_str
        if self.state == 'run':
            app.timers_state = workout_trainer_util.gen_spinner()
        return timer_str

    def get_time(self, dt):
        """
        get_time
        args: self - self object
            dt - time since last callback call
        purpose: generate time string to dislay in workout timer label
        """
        app = App.get_running_app()
        self.time_left = self.end_time - time.time()
        if not int(self.time_left):
            self.state = 'finish'
            self.play_alarm()
            stateful_clock.unschedule(self.get_time)
        app.generic_timer = self.format_time(self.time_left, self.timer_text_color)

    def key_press(self, keyboard, keycode, *args):
        """
        key_press
        args: self - self object
            keyboard - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process number pad's key press
        """
        Logger.info('timer: key_press {}, timer_index {}, time_pad_str {}'.format(keycode, self.timer_index, self.time_pad_str))
        super().key_press(keyboard, keycode,args)
        app = App.get_running_app()
        app.generic_timer = self.markup_timer

    def parse_time_string(self, time_str):
        """
        parse_time_string
        args: self - self object
            time_str - hh:mm:ss formated time string
        purpose: turn a time string into seconds
        returns: seconds represented by time string
        """
        Logger.info('generic_timer: parse_time_string {}'.format(time_str))
        return (int(time_str[:2]) * 3600) + (int(time_str[3:][:2]) * 60) + int(time_str[6:])

    def play_alarm(self):
        """
        play__alarm
        args: self - self object
        purpose: play workout alarm sound file
        """
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['sound'].play_sound('cloister_bell.ogg')
        app.app_data_dict['unpickleable']['vibrator'].vibrate('finish')

    def set_timer_paused_indicator(self, time_left, timer_text_color):
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation
        """
        app = App.get_running_app()
        app.generic_timer = self.format_time(time_left, timer_text_color)

    def store_time_left_state(self):
        """
        store_time_left_state
        args: self - self object
            time_left - time remaining
        purpose: save rest time left state for Android pause
        """
        pass

    def timer_on_touch_up(self, touch, touch_type, app): # called from timer.py
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a workout timer
        """
        super().timer_on_touch_up(touch, touch_type, app)
        app.app_data_dict['global properties']['generic timer state'] = self.state
        app.app_data_dict['global properties']['generic timer time left'] = self.time_left
        app.app_data_dict['global properties']['generic timer end time'] = self.end_time
        app.app_data_dict['global properties']['generic timer'] = app.workout_timer = self.format_time(self.time_left, self.timer_text_color)

    def timer_paused_indicator(self, dt):
        """
        timer_paused_indicator
        args: self - self object
            dt - time since last callback call
        purpose: provide method mapping so state is retained
        """
        Logger.info('generic_timer: timer_paused_indicator')
        super().timer_paused_indicator(dt)

    def fix_tabata_switch(self):
        """
        fix_tabata_switch
        args: self - self object
        purpose: fix tabata trainer timer reset which is used to fix trainers upon switching
        """
        if self.state == 'run':
            stateful_clock.unschedule(self.timer_paused_indicator)
            self.timer_paused_pulsate_object = None
            self.timer_text_color = get_hex_from_color((1, 1, 1))
            stateful_clock.schedule_interval(self.get_time, 1)
