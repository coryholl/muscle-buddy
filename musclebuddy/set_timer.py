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
import soft_keyboard
import stateful_clock
from timer import Timer

class SetTimer(Timer):
    """
    SetTimer
    purpose: class for creating timers for timing exercise sets
    """
    end_time = 0 #app.app_data_dict['global properties']['set end time']
    state = 'not started' #app.app_data_dict['global properties']['set timer state']
    time_left = 0 #app.app_data_dict['global properties']['set time left']
    time_pad_str = '00:00.0'
    timer_index = 0
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
        self.end_time = app.app_data_dict['global properties']['set end time']
        self.state = app.app_data_dict['global properties']['set timer state']
        self.time_left = app.app_data_dict['global properties']['set time left']
        stateful_clock.restore_clock(self.get_time)
        stateful_clock.restore_clock(self.timer_paused_indicator)
        stateful_clock.restore_clock(self.finished_visual_alarm)

    def finished_visual_alarm(self, dt):
        """
        finished_visual_alarm
        args: self - self object
            dt - time since last callback
        purpose: provide method mapping so state is retained for Android pause
        """
        super().finished_visual_alarm(dt)

    def format_time(self, seconds, color, sign):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of time text
            sign - sign to prefix the string with
        purpose: create a time string for a set timer
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
        app.app_data_dict['global properties']['set time left'] = self.time_left = self.end_time - time.time()
        if self.time_left > 0:
            app.app_data_dict['global properties']['workout set timer'] = app.workout_set_timer = self.format_time_msd(self.time_left, self.timer_text_color)
        else:
            app.app_data_dict['global properties']['set timer state'] = self.state = 'finish'
            app.app_data_dict['global properties']['set time left'] = app.app_data_dict['global properties']['set end time'] = self.time_left = self.end_time = 0
            stateful_clock.unschedule(self.get_time)
            try:
                self.parent.parent.play_set_alarm() # may need to be replaced for reuse purposes
            except Exception as e:
                try:
                    self.parent.parent.parent.play_set_alarm()
                except Exception as e:
                    try:
                        self.parent.parent.parent.parent.play_set_alarm()
                    except Exception as e:
                        Logger.error('set_timer: unable to find play_set_alarm method')
            stateful_clock.schedule_interval(self.finished_visual_alarm, 0.05)
            app.app_data_dict['global properties']['workout set timer'] = app.workout_set_timer = self.format_time_msd(self.time_left, self.timer_text_color)

    def key_press(self, keyboard, keycode, *args):
        """
        key_press
        args: self - self object
            keyboard - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process number pad's key press
        """
        Logger.info('set_timer: key_press {}, timer_index {}, time_pad_str {}'.format(keycode, self.timer_index, self.time_pad_str))
        super().key_press(keyboard, keycode,args)
        app = App.get_running_app()
        app.tabata_set_timer = self.markup_timer

    def set_finished_visual_alarm(self, blue_green):
        """
        set_finished_visual_alarm
        args: self - self object
            blue_green - color number for blue and green color
        purpose: set background color for timer finished visual alarm animation
        """
        self.timer_background_color = (0, blue_green / 2, blue_green)

    def set_timer_paused_indicator(self, time_left, timer_text_color):
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation

        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['workout set timer'] = app.workout_set_timer = self.format_time_msd(time_left, timer_text_color)

    def stop_alarm(self):
        """
        stop_alarm
        args: self - self object
        purpose: implement a shutdown mechanism for set timer
        """
        app = App.get_running_app()
        stateful_clock.unschedule(self.finished_visual_alarm)
        stateful_clock.unschedule(self.get_time)
        stateful_clock.unschedule(self.timer_paused_indicator) 
        self.timer_background_color = (0, 0, 0)
        self.timer_text_color = get_hex_from_color((1, 1, 1))
        app.app_data_dict['global properties']['set time left'] = self.time_left = 0
        if app.app_data_dict['global properties']['exercise']['alarm sound file']:
            app.app_data_dict['unpickleable']['sound'].stop_sound(app.app_data_dict['global properties']['exercise']['alarm sound file'])

    def store_time_left_state(self):
        """
        store_time_left_state
        args: self - self object
            time_left - time remaining
        purpose: save set time left state for Android pause
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['set time left'] = self.time_left

    def timer_on_touch_up(self, touch, touch_type, app): # called from Kivy engine
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a set timer
        """
        app = App.get_running_app()
        if not app.app_data_dict['global properties']['exercise'] or not app.app_data_dict['global properties']['exercise']['set timer']:
            app.app_data_dict['global properties']['set timer state'] = self.state = 'shutdown'
        if self.state == 'shutdown':
            app.app_data_dict['global properties']['workout set timer'] = app.workout_set_timer = ''
            soft_keyboard.remove_soft_keyboard()
        else:
            self.time_left = app.app_data_dict['global properties']['exercise']['set timer'] if self.state in ('not started', 'not started 2') else self.time_left
            self.timer_on_touch_up2(touch, touch_type, app)
            app.app_data_dict['global properties']['set timer state'] = self.state
            app.app_data_dict['global properties']['set time left'] = self.time_left
            app.app_data_dict['global properties']['set end time'] = self.end_time
            app.app_data_dict['global properties']['workout set timer'] = app.workout_rest_timer = self.format_time_msd(self.time_left, self.timer_text_color)

    def timer_paused_indicator(self, dt):
        """
        timer_paused_indicator
        args: self - self object
            dt - time since last callback call
        purpose: provide method mapping so state is retained for Android pause
        """
        super().timer_paused_indicator(dt)
