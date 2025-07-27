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
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.utils import platform

on_key_up_bind = on_key_down_bind = widget_bind = None
capslock = left_shift = right_shift = False

def get_hard_keyboard(widget, on_key_up=None, on_key_down=None):
    """
    get_hard_keyboard
    args: widget - widget to attach keyboard object to
        on_key_up - optional binding for on_key_dup method
        on_key_down - optional binding for on_key_down method
    purpose: abstract out hard keyboard behavior
    """
    global on_key_up_bind, on_key_down_bind, widget_bind
    Logger.info('hard_keyboard: get_hard_keyboard')
    if platform == 'linux':
        hardware_keyboard = Window.request_keyboard(keyboard_closed, widget)
        if on_key_up:
            if on_key_up_bind:
                hardware_keyboard.unbind(on_key_up=on_key_up_bind)
            hardware_keyboard.bind(on_key_up=on_key_up)
            on_key_up_bind = on_key_up
        if on_key_down:
            if on_key_down_bind:
                hardware_keyboard.unbind(on_key_down=on_key_down_bind)
            hardware_keyboard.bind(on_key_down=on_key_down)
            on_key_down_bind = on_key_down
        widget_bind = widget

def keyboard_closed(*kwargs):
    """
    keyboard_closed
    purpose: process keyboard close event
    """
    Logger.info('hard_keyboard: keyboard_closed {}'.format(kwargs))

def unbind_keyboard():
    """
    unbind_keyboard
    purpose: make certain hardware keyboard is not running
    """
    global on_key_up_bind, on_key_down_bind, widget_bind
    if platform == 'linux':
        hardware_keyboard = Window.request_keyboard(keyboard_closed, widget_bind)
        if on_key_up_bind:
            hardware_keyboard.unbind(on_key_up=on_key_up_bind)
        if on_key_down_bind:
            hardware_keyboard.unbind(on_key_down=on_key_down_bind)
