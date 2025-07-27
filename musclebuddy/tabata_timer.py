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
from kivy.clock import Clock
from kivy.utils import get_hex_from_color
# local imports
import stateful_clock
import workout_trainer_util
from timer import Timer

class TabataTimer(Timer):
    """
    WorkoutTimer
    purpose: class for a timer for timing a full workout
    """
    end_time = 0 #app.app_data_dict['global properties']['tabata end time']
    state = 'not started' #app.app_data_dict['global properties']['tabata timer state']
    time_left = 0 #app.app_data_dict['global properties']['tabata time left']
    sheet_lightning_value = 1.0

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
        purpose: initialize workout timer restoring state on Android if necessary
        """
        super(Timer, self).__init__(**kwargs)

    def format_time(self, seconds, color):
        """
        format_time
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of clock text
        purpose: create a time string for a workout tabata timer
        returns: string to display in timer label
        """
        minute = int((seconds % 6000) // 60)
        second = int(seconds % 60)
        if self.state == 'run':
            app = App.get_running_app()
            app.trainer_state = workout_trainer_util.gen_spinner()
        return f'[color={color}]{minute:02d}:{second:02d}[/color]'

    def full_reset(self):
        """
        full_reset
        args: self - self object
        purpose: complete reset of state of timer
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['tabata workout index']]
        properties['tabata time left'] = self.time_left = workout['time length']
        properties['tabata end time'] = self.end_time = time.time() + self.time_left
        properties['tabata timer state'] = self.state = 'not started'
        app.tabata_set_timer = self.format_time_msd(0, get_hex_from_color((1, 1, 1)))

    def get_workout_time(self, dt):
        """
        get_workout_time
        args: self - self object
            dt - time since last callback call
        purpose: generate time string to dislay in workout timer label
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        properties['tabata time left'] = self.time_left = self.end_time - time.time()
        properties['tabata time'] = app.tabata_workout_timer = \
            self.format_time(self.time_left, get_hex_from_color((1, 1, 1)))
        workout = app.app_data_dict['workout dictionary'][properties['tabata workout index']]
        exercises = workout['active set']
        set_time_left = self.time_left - (exercises[workout['set index']]['end time'] -
                                          exercises[workout['set index']]['set timer'])
        if set_time_left > 0:
            app.tabata_set_timer = self.format_time_msd(set_time_left, get_hex_from_color((1, 1, 1)))
        else:
            workout['set index'] += 1
            if workout['set index'] == len(exercises) or self.time_left < 0:
                stateful_clock.unschedule(self.get_workout_time)
                properties['tabata time'] = app.tabata_workout_timer = \
                    self.format_time(0, get_hex_from_color((1, 1, 1)))
                app.tabata_exercise_name = f'[b]WORKOUT COMPLETE!!![/b]'
                self.parent.play_workout_alarm()
                app.tabata_set_timer = self.format_time_msd(0, get_hex_from_color((1, 1, 1)))
                properties['tabata timer state'] = self.state = 'finish'
            else:
                self.parent.next_workout_set(exercises[workout['set index']]['name'])
                set_time_left = exercises[workout['set index']]['set timer'] - \
                                (exercises[workout['set index']]['end time'] - self.time_left)
                app.tabata_set_timer = self.format_time_msd(set_time_left, get_hex_from_color((1, 1, 1)))
                app.app_data_dict['unpickleable']['sound'].play_sound(
                    exercises[workout['set index'] - 1]['alarm sound file'])
                Clock.schedule_interval(self.sheet_lightning, 0.03)
                app.app_data_dict['unpickleable']['vibrator'].vibrate('alarm')

    def restore_state(self):
        """
        restore_state
        purpose: restore timer state after a Android pause
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['tabata workout index']]
        self.time_left = properties['tabata time left'] if properties['tabata time left'] else workout['time length']
        self.end_time = properties['tabata end time'] if properties['tabata end time'] else time.time() + self.time_left
        self.state = properties['tabata timer state']
        app.tabata_workout_timer = properties['tabata time'] if 'tabata time' in properties else (
            self.format_time(self.time_left, get_hex_from_color((1, 1, 1))))

    def set_timer_paused_indicator(self, time_left, timer_text_color): # called from timer.py
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: set the text color for timer for pause pulse animation
        """
        app = App.get_running_app()
        app.app_data_dict['global properties']['tabata timer'] = app.tabata_workout_timer = \
            self.format_time(time_left, timer_text_color)

    def sheet_lightning(self, dt):
        """
        sheet_lightning
        args: self - self object
            dt - time since last callback
        purpose: create a sheet lightning effect for showing set transition
        """
        app = App.get_running_app()
        self.sheet_lightning_value -= 0.025
        if self.sheet_lightning_value < 0.0:
            self.sheet_lightning_value = 1.0
            app.tabata_bg_color = (0, 0, 0, 1)
            Clock.unschedule(self.sheet_lightning)
        else:
            app.tabata_bg_color = (self.sheet_lightning_value, self.sheet_lightning_value, self.sheet_lightning_value, 1)

    def timer_on_touch_up(self, touch, touch_type, app): # called from timer.py
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a workout timer
        """
        app = App.get_running_app()
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['workout index']]
        if self.state == 'finish':
            if workout['alarm sound file']:
                app.app_data_dict['unpickleable']['sound'].stop_sound(workout['alarm sound file'])
        elif self.state == 'not started':
            if touch_type == 'press':
                properties['tabata timer state'] = self.state = 'run'
                properties['tabata time left'] = self.time_left = self.time_left if self.time_left \
                    else workout['time length']
                properties['tabata end time'] = self.end_time = time.time() + self.time_left
                stateful_clock.schedule_interval(self.get_workout_time, 0.1)
        elif self.state == 'pause':
            if touch_type == 'press':
                properties['tabata timer state'] = self.state = 'run'
                properties['tabata end time'] = self.end_time = time.time() + self.time_left
                stateful_clock.unschedule(self.timer_paused_indicator)
                self.timer_paused_pulsate_object = None
                self.timer_text_color = get_hex_from_color((1, 1, 1))
                stateful_clock.schedule_interval(self.get_workout_time, 0.1)
        elif self.state == 'run':
            if touch_type == 'press':
                properties['tabata timer state'] = self.state = 'pause'
                stateful_clock.unschedule(self.get_workout_time)
                stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
