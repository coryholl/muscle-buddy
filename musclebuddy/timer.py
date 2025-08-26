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
import re
import time
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.properties import ColorProperty
from kivy.utils import get_hex_from_color
from kivy.vector import Vector
# local imports
import hard_keyboard
import over_press
import pulsate
import soft_keyboard
import stateful_clock
from hard_keyboard_state import HardKeyboardState

class Timer(Label, HardKeyboardState):
    """
    Timer
    purpose: an abstract class for creating visual timers
    """
    markup = True
    timer_background_color = ColorProperty((0, 0, 0))
    timer_text_color = get_hex_from_color((1, 1, 1))
    time_pad_str = '00:00:00'
    timer_index = 0
    time_length = 0
    keypad_container = None
    markup_timer = ''
    timer_paused_pulsate_object = None
    finished_pulsate_object = None
    time_regular_expression = r'(\d\d):([0-5]\d)'

    def breakdown_time(self, seconds):
        """
        breakdown_time
        args: self - self object
            seconds - time to be broken down into components
        purpose: breakdown a time into hour, minute, second, and decisecond components
        returns: tuple containing hour, minute, second, and decisecond
        """
        hour = int(seconds // 3600)
        minute = int((seconds % 3600) // 60)
        second = int(seconds % 60)
        decisecond = int((seconds * 10) % 10)
        return (hour, minute, second, decisecond)

    def categorize_touch(self, touch):
        """
        categorize_touch
        args: self - self object
            touch - touch event object
        purpose: categorize a touch as press, left or right swipe
        returns: string indictating touch category
        """
        vector = Vector(touch.pos) - Vector(touch.opos)
        if abs(vector.x) < 20:
            return 'press'
        elif vector.x < 0:
            return 'left'
        else:
            return 'right'

    def finished_visual_alarm(self, dt):
        """
        finished_visual_alarm
        args: self - self object
            dt - time since last callback call
        purpose: generate a visual alarm to help indicate the end of the workout
        """
        self.finished_pulsate_object = (self.finished_pulsate_object if self.finished_pulsate_object else
            pulsate.Pulsate(0.0, 0.05))
        rgb_color = self.finished_pulsate_object.get_next_pulse()
        self.set_finished_visual_alarm(rgb_color)

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
        app = App.get_running_app()
        hour, minute, second, decisecond = self.breakdown_time(seconds)
        self.time_pad_str = temp_time_str = f'{hour:02d}:{minute:02d}:{second:02d}'
        if self.state == 'pause':
            cursor_color = color[:5] + '00'
            temp_time_str = (temp_time_str[:self.timer_index] + f'[color={cursor_color}]' +
                            temp_time_str[self.timer_index] + f'[/color]' + temp_time_str[self.timer_index + 1:])
        return f'{sign}[color={color}]{temp_time_str}[/color]'

    def format_time_msd(self, seconds, color):
        """
        format_time_msd
        args: self - self object
            seconds - number of seconds in time to convert to string
            color - color of time text
        purpose: create a time string in minute, second, decisecond format
        returns: string to display in timer label
        """
        hour, minute, second, decisecond = self.breakdown_time(seconds)
        self.time_pad_str = temp_time_str = f'{minute:02d}:{second:02d}'
        if self.state == 'pause':
            cursor_color = color[:5] + '00'
            temp_time_str = (temp_time_str[:self.timer_index] + f'[color={cursor_color}]' +
                             temp_time_str[self.timer_index] + f'[/color]' + temp_time_str[self.timer_index + 1:])
        return f'[color={color}]{temp_time_str}.{decisecond:01d}[/color]'

    def get_negative_workout_time(self, dt):
        """
        get_negative_stopwatch_time
        args: self - self object
            dt - time since last callback call
        purpose: generate a stopwatch for showing how much time has progressed since workout time ran out
        """
        Logger.warning('timer: call made to empty abstract method "get_negative_workout_time" which is meant to be overridden in child class')

    def get_time(self, dt):
        """
        get_time
        args: self - self object
            dt - time since last callback call
        purpose: empty binding to be overridden by child class
        """
        Logger.warning('timer: call made to empty abstract method "get_time" which is meant to be overridden in child class')

    def key_press(self, keyboard, keycode, *args):
        """
        key_press
        args: self - self object
            keyboard - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process number pad's key press
        """
        Logger.info('timer: key_press {}, timer_index {}, time_pad_str {}'.format(keycode, self.timer_index,
                                                                                  self.time_pad_str))
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            sound = app.app_data_dict['unpickleable']['sound']
# Python 3.10 syntax
            match keycode:
                case 'backspace':
                    if self.timer_index:
                        if self.time_pad_str[self.timer_index] != ':':
                            self.time_pad_str = self.time_pad_str[:self.timer_index] + '0' + \
                                self.time_pad_str[self.timer_index + 1:]
                        self.timer_index -= 1
                    else:
                        self.time_pad_str = '0' + self.time_pad_str[1:]
                    self.time_left = self.parse_time_string(self.time_pad_str)
                    self.markup_timer = self.format_time(self.time_left, self.timer_text_color, '')
                case 'exit':
                    soft_keyboard.remove_soft_keyboard()
                case 'left':
                    if self.timer_index:
                        self.timer_index -= 1
                    else:
                        sound.play_sound('beep.ogg')
                case 'right':
                    if self.timer_index < self.max_timer_index:
                        self.timer_index += 1
                    else:
                        sound.play_sound('beep.ogg')
                case 'tab':
                    pass
                case _:
                    if len(keycode) == 1:
                        test_text = list(self.time_pad_str)
                        if test_text[self.timer_index] == ':' and keycode != ':':
                            self.timer_index += 1
                        test_text[self.timer_index] = keycode
                        test_str = ''.join(test_text)
                        if re.match(self.time_regular_expression, test_str):
                            self.timer_index = self.timer_index + 1 if self.timer_index < self.max_timer_index else \
                                self.timer_index
                            self.time_pad_str = test_str
                            self.time_left = self.parse_time_string(self.time_pad_str)
                            self.markup_timer = self.format_time(self.time_left, self.timer_text_color, '')
                        else:
                            sound.play_sound('beep.ogg')
                    else:
                        sound.play_sound('beep.ogg')
# start old Python syntax
#            if keycode == 'backspace':
#                if self.timer_index:
#                    if self.time_pad_str[self.timer_index] != ':':
#                        self.time_pad_str = self.time_pad_str[:self.timer_index] + '0' + \
#                            self.time_pad_str[self.timer_index + 1:]
#                    self.timer_index -= 1
#                else:
#                    self.time_pad_str = '0' + self.time_pad_str[1:]
#                self.time_left = self.parse_time_string(self.time_pad_str)
#                self.markup_timer = self.format_time(self.time_left, self.timer_text_color, '')
#            elif keycode == 'exit':
#                soft_keyboard.remove_soft_keyboard()
#            elif keycode == 'left':
#                if self.timer_index:
#                    self.timer_index -= 1
#                else:
#                    sound.play_sound('beep.ogg')
#            elif keycode == 'right':
#                if self.timer_index < self.max_timer_index:
#                    self.timer_index += 1
#                else:
#                    sound.play_sound('beep.ogg')
#            elif keycode == 'tab':
#                pass
#            else:
#                if len(keycode) == 1:
#                    test_text = list(self.time_pad_str)
#                    if test_text[self.timer_index] == ':' and keycode != ':':
#                        self.timer_index += 1
#                    test_text[self.timer_index] = keycode
#                    test_str = ''.join(test_text)
#                    if re.match(self.time_regular_expression, test_str):
#                        self.timer_index = self.timer_index + 1 if self.timer_index < self.max_timer_index else \
#                            self.timer_index
#                        self.time_pad_str = test_str
#                        self.time_left = self.parse_time_string(self.time_pad_str)
#                        self.markup_timer = self.format_time(self.time_left, self.timer_text_color, '')
#                    else:
#                        sound.play_sound('beep.ogg')
#                else:
#                    sound.play_sound('beep.ogg')
# end old Python syntax

    def manage_keyboard_state(self):
        """
        manage_keyboard_state
        args: self - self object
        purpose: handle keyboard states for timers
        """
        config = App.get_running_app().app_data_dict['config']
        if config['software keyboard']['active']:
            time_pad = soft_keyboard.get_keyboard('time')
            time_pad.on_key_up = self.key_press
            if time_pad.parent and time_pad.parent is self:
                pass
            elif time_pad.parent:
                time_pad.parent.remove_widget(time_pad)
                self.keypad_container.add_widget(time_pad)
            else:
                self.keypad_container.add_widget(time_pad)
        if config['hardware keyboard']['active']:
            hard_keyboard.get_hard_keyboard(self, on_key_down=self.hard_key_press, on_key_up=self.hard_key_release)

    def on_touch_up(self, touch): # called from Kivy engine
        """
        on_touch_up
        args: self - self object
            touch - touch event object
        purpose: process a touch up event to create interactive timer behaviors
        """
        app = App.get_running_app()
        if self.collide_point(*touch.pos) and over_press.protect(app = app):
            touch_type = self.categorize_touch(touch)
            if touch_type == 'press':
                app.app_data_dict['unpickleable']['vibrator'].vibrate('button')
            self.timer_on_touch_up(touch, touch_type, app)

    def parse_time_string(self, time_str):
        """
        parse_time_string
        args: self - self object
            time_str - hh:mm:ss formated time string
        purpose: turn a time string into seconds
        returns: seconds represented by time string
        """
        Logger.info('timer: parse_time_string {}'.format(time_str))
        return (int(time_str[:2]) * 60) + float(time_str[3:])

    def set_finished_visual_alarm(self, red):
        """
        set_finished_visual_alarm
        args: self - self object
            red - red intensity
        purpose: default visual timer background set
        """
        self.timer_background_color = (red, 0, 0)

    def set_timer_paused_indicator(self, time_left, timer_text_color): # called from timer.py
        """
        set_timer_paused_indicator
        args: self - self object
            time_left - remaining time in timer
            timer_text_color - color of timer text
        purpose: empty binding to be overridden by child class
        """
        Logger.warning('timer: call made to empty abstract method "set_timer_paused_indicator" which is meant to be overridden in child class')

    def stop_alarm(self):
        """
        stop_alarm
        args: self - self object
        prupose: stub for stopping an alarm
        """
        pass

    def store_time_left_state(self):
        """
        store_time_left_state
        args: self - self object
        purpose: empty binding to be overridden by child class
        """
        Logger.warning('timer: call made to empty abstract method "store_time_left_state" which is meant to be overridden in child class')

    def timer_on_touch_up(self, touch, touch_type, app):
        """
        timer_on_touch_up
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for a timer
        """
        Logger.info(f'timer: timer_on_touch_up: touch {touch} touch_type {touch_type} app {app} state {self.state}')
        workout_index = app.app_data_dict['global properties']['workout index']
# Python 3.10 syntax
        match self.state:
            case 'finish':
                self.state = 'shutdown'
                stateful_clock.unschedule(self.finished_visual_alarm)
                stateful_clock.unschedule(self.get_negative_workout_time)
                self.timer_background_color = (0, 0, 0)
                if app.app_data_dict['workout dictionary'][workout_index]['alarm sound file']:
                    app.app_data_dict['unpickleable']['sound'].stop_sound(
                        app.app_data_dict['workout dictionary'][workout_index]['alarm sound file'])
                app.app_data_dict['unpickleable']['sound'].stop_sound('cloister_bell.ogg')
                try:
                   if 'keypad_button_container_id' in self.parent.parent.parent.ids.keys():
                       self.parent.parent.parent.ids['keypad_button_container_id'].disabled = False
                except Exception as e:
                    pass
            case 'not started':
                if touch_type == 'press':
                    self.state = 'run'
                    self.time_left = self.time_left if self.time_left else (
                        app.app_data_dict)['workout dictionary'][workout_index]['time length']
                    self.end_time = time.time() + self.time_left
                    stateful_clock.schedule_interval(self.get_time, 1)
                else:
                    if self.time_left:
                        self.time_left += 60 * (1 if touch_type == 'left' else -1)
                        self.time_left = self.time_left if self.time_left > 0 else 0
                    else:
                        self.time_left = (app.app_data_dict['workout dictionary'][workout_index]['time length'] + 60 *
                                          (1 if touch_type == 'left' else -1))
            case 'pause':
                if touch_type == 'press':
                    self.state = 'run'
                    self.end_time = self.time_left + time.time()
                    stateful_clock.unschedule(self.timer_paused_indicator)
                    self.timer_paused_pulsate_object = None
                    self.timer_text_color = get_hex_from_color((1, 1, 1))
                    stateful_clock.schedule_interval(self.get_time, 1)
                else:
                    self.time_left += 60 * (1 if touch_type == 'left' else -1)
                    self.time_left = self.time_left if self.time_left > 0 else 0
            case 'run':
                if touch_type == 'press':
                    self.state = 'pause'
                    self.timer_index = 0
                    stateful_clock.unschedule(self.get_time)
                    self.manage_keyboard_state()
                    stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
            case 'shutdown':
                pass
# start old Python syntax
#        if self.state == 'finish':
#            self.state = 'shutdown'
#            stateful_clock.unschedule(self.finished_visual_alarm)
#            stateful_clock.unschedule(self.get_negative_workout_time)
#            self.timer_background_color = (0, 0, 0)
#            if app.app_data_dict['workout dictionary'][workout_index]['alarm sound file']:
#                app.app_data_dict['unpickleable']['sound'].stop_sound(
#                    app.app_data_dict['workout dictionary'][workout_index]['alarm sound file'])
#            app.app_data_dict['unpickleable']['sound'].stop_sound('cloister_bell.ogg')
#            try:
#                if 'keypad_button_container_id' in self.parent.parent.parent.ids.keys():
#                    self.parent.parent.parent.ids['keypad_button_container_id'].disabled = False
#            except Exception as e:
#                pass
#        elif self.state == 'not started':
#            if touch_type == 'press':
#                self.state = 'run'
#                self.time_left = self.time_left if self.time_left else (
#                    app.app_data_dict)['workout dictionary'][workout_index]['time length']
#                self.end_time = time.time() + self.time_left
#                stateful_clock.schedule_interval(self.get_time, 1)
#            else:
#                if self.time_left:
#                    self.time_left += 60 * (1 if touch_type == 'left' else -1)
#                    self.time_left = self.time_left if self.time_left > 0 else 0
#                else:
#                    self.time_left = (app.app_data_dict['workout dictionary'][workout_index]['time length'] + 60 *
#                                        (1 if touch_type == 'left' else -1))
#        elif self.state == 'pause':
#            if touch_type == 'press':
#                self.state = 'run'
#                self.end_time = self.time_left + time.time()
#                stateful_clock.unschedule(self.timer_paused_indicator)
#                self.timer_paused_pulsate_object = None
#                self.timer_text_color = get_hex_from_color((1, 1, 1))
#                stateful_clock.schedule_interval(self.get_time, 1)
#            else:
#                self.time_left += 60 * (1 if touch_type == 'left' else -1)
#                self.time_left = self.time_left if self.time_left > 0 else 0
#        elif self.state == 'run':
#            if touch_type == 'press':
#                self.state = 'pause'
#                self.timer_index = 0
#                stateful_clock.unschedule(self.get_time)
#                self.manage_keyboard_state()
#                stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
#        elif self.state == 'shutdown':
#            pass
# end old Python syntax

        if self.state != 'pause':
            soft_keyboard.remove_soft_keyboard()
            hard_keyboard.unbind_keyboard()

    def timer_on_touch_up2(self, touch, touch_type, app):
        """
        timer_on_touch_up2
        args: self - self object
            touch - touch event object
            touch_type - categorization of touch up event
            app - Kivy object of running app
        purpose: process a touch up event for smaller timers
        """
        if self.state == 'finish':
            self.state = 'not started'
            self.stop_alarm()
        elif self.state in ('not started', 'not started 2'):
            if touch_type == 'press':
                self.state = 'run'
                self.time_left = self.time_left if self.time_left else self.time_length
                self.end_time = time.time() + self.time_left
                stateful_clock.schedule_interval(self.get_time, 0.1) # revisit cjh
            else:
                if self.state == 'not started':
                    self.time_left = app.app_data_dict['global properties']['rest time length']
                    self.state = 'not started 2'
                self.time_left += 10 * (1 if touch_type == 'left' else -1)
                self.time_left = self.time_length = 0 if self.time_left < 0 else self.time_left
        elif self.state == 'pause':
            if touch_type == 'press':
                self.state = 'run'
                self.end_time = self.time_left + time.time()
                stateful_clock.unschedule(self.timer_paused_indicator)
                self.timer_paused_pulsate_object = None
                self.timer_text_color = get_hex_from_color((1, 1, 1))
                stateful_clock.schedule_interval(self.get_time, 0.1)
            else:
                self.time_left += 10 * (1 if touch_type == 'left' else -1)
                self.time_left = 0 if self.time_left < 0 else self.time_left
        elif self.state == 'run':
            if touch_type == 'press':
                self.state = 'pause'
                self.timer_index = 0
                stateful_clock.unschedule(self.get_time)
                self.manage_keyboard_state()
                stateful_clock.schedule_interval(self.timer_paused_indicator, 0.05)
        if self.state != 'pause':
            soft_keyboard.remove_soft_keyboard()
            hard_keyboard.unbind_keyboard()

    def timer_paused_indicator(self, dt):
        """
        timer_paused_indicator
        args: self - self object
            dt - time since last callback call
        purpose: generate a pulse to indicate paused timer
        """
        self.timer_paused_pulsate_object = self.timer_paused_pulsate_object if self.timer_paused_pulsate_object else \
            pulsate.Pulsate(0.0, 0.05)
        pulse_color = self.timer_paused_pulsate_object.get_next_pulse()
        self.timer_text_color = get_hex_from_color((pulse_color, pulse_color, pulse_color))
        self.set_timer_paused_indicator(self.time_left, self.timer_text_color)
