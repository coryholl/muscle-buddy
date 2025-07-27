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

from kivy.clock import Clock
from kivy.logger import Logger
# local imports
import hard_keyboard

class HardKeyboardState:

    key_map = {
        'space': ' ', '`': '~',
        '1': '!', '2': '@', '3': '#', '4': '$', '5': '%', '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
        '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|', ';': ':', "'": '"', ',': '<', '.': '>', '/': '?'
    }

    last_key_press = None

    def hard_key_press(self, keyboard, keytuple, *kwargs):
        """
        hard_key_press
        args: self - self object
            keyboard - keyboard object
            keytuple - tuple of key int value and key string value
            kwargs - other positional arguments
        purpose: detect key down press, used for tracking shift holding
        """
        Logger.info('text_input_util: hard_key_press {}'.format(keytuple))
        key_val = keytuple[1]
# Python 3.10 syntax commented out for future restore
#        match key_val:
#            case 'rshift':
#                hard_keyboard.right_shift = True
#            case 'shift':
#                hard_keyboard.left_shift = True
#            case _:
#                if ((hard_keyboard.capslock or hard_keyboard.left_shift or hard_keyboard.right_shift) and
#                        len(key_val) == 1 and key_val.isalpha()):
#                    key_val = key_val.upper()
#                elif (hard_keyboard.left_shift or hard_keyboard.right_shift) and key_val in self.key_map:
#                    key_val = self.key_map[key_val]
#                self.key_press(None, key_val)
#                self.last_key_press = key_val
#                Clock.schedule_once(self.repeat_key_press, 0.25)
# start old Python syntax
        if key_val == 'rshift':
            hard_keyboard.right_shift = True
        elif key_val == 'shift':
            hard_keyboard.left_shift = True
        else:
            if ((hard_keyboard.capslock or hard_keyboard.left_shift or hard_keyboard.right_shift) and
                    len(key_val) == 1 and key_val.isalpha()):
                key_val = key_val.upper()
            elif (hard_keyboard.left_shift or hard_keyboard.right_shift) and key_val in self.key_map:
                key_val = self.key_map[key_val]
            self.key_press(None, key_val)
            self.last_key_press = key_val
            Clock.schedule_once(self.repeat_key_press, 0.25)
# end old Python syntax

    def hard_key_release(self, keyboard, keytuple, *kwargs):
        """
        hard_key_release
        args: self - self object
            keyboard - keyboard object
            keytuple - tuple of key int value and key string value
            kwargs - other positional arguments
        purpose: process key press from a hardware keyboard
        """
        Logger.info('hard_keyboard_state: hard_key_release {}'.format(keytuple))
        key_val = keytuple[1]
# Python 3.10 syntax commented out for future restore
#        match key_val:
#            case 'capslock':
#                hard_keyboard.capslock = not hard_keyboard.capslock
#            case 'rshift':
#                hard_keyboard.right_shift = False
#            case 'shift':
#                hard_keyboard.left_shift = False
#            case _:
#                Clock.unschedule(self.repeat_key_press)
# start old Python syntax
        if key_val == 'capslock':
            hard_keyboard.capslock = not hard_keyboard.capslock
        elif key_val == 'rshift':
            hard_keyboard.right_shift = False
        elif key_val == 'shift':
            hard_keyboard.left_shift = False
        else:
            Clock.unschedule(self.repeat_key_press)
# end old Python syntax

    def key_press(self, keyboard, keycode, app=None):
        """
        key_press
        args: self - self object
            keycode - key press value
            app - app code
        """
        Logger.warning('hard_keyboard_state: key_press: Empty stub called from abstract class')

    def repeat_key_press(self, dt):
        """
        repeate_key_press
        args: self - self object
            dt - kivy time code
        purpose: create a key press repeat feature for hardware keyboards
        """
        Logger.info(f'hard_keyboard_state: repeat_key_press dt: {dt}')
        self.key_press(None, self.last_key_press)
        Clock.schedule_once(self.repeat_key_press, 0.05)
