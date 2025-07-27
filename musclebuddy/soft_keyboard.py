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
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.vkeyboard import VKeyboard
from kivymd.uix.button import MDIconButton

layouts = {
    'capspad': 'squeek_qwerty_upper.json',
    'exercise selector': 'squeek_qwerty_lower.json',
    'float': 'float_pad.json',
    'int': 'int_pad.json',
    'lowpad': 'squeek_qwerty_lower.json',
    'numpad': 'squeek_numpad.json',
    'symbolpad': 'squeek_symbolpad.json',
    'text': 'squeek_qwerty_lower.json',
    'time': 'time_pad.json'
}

def get_keyboard(key, app=None):
    """
    get_keyboard
    args: key - indicator as to which keybaord to return
        app - optional app object
    purpose: return keyboard based on key
    returns: specified keyboard widget
    """
    app = app if app else App.get_running_app()
    return app.app_data_dict['unpickleable'][f'software keyboard {key}']

def get_mounted_keyboard(app=None):
    """
    get_mounted_keyboard
    args: app - app kivy object
    purpose: find mounted keyboard
    returns: Kivy VKeyboard object of mounted keyboard
    """
    global layouts
    app = app if app else App.get_running_app()
    for layout in layouts:
        kb = app.app_data_dict['unpickleable'][f'software keyboard {layout}']
        if kb.parent:
            return kb
    return None

def init_keyboards(app=None):
    """
    init_keyboards
    args: app - optional app object
    purpose: initialize keyboards
    """
    global layouts
    app = app if app else App.get_running_app()
    unpickleable = app.app_data_dict['unpickleable']
    window_height = app.app_data_dict['window height']
    numpad_height = window_height // 4
    keyboard_height = window_height // 2.8
    font_size = window_height // 30
    width = int(app.app_data_dict['window width'] * 1.1)
    for key, layout in layouts.items():
        kb = unpickleable[f'software keyboard {key}'] = VKeyboard(
            background_color=[0, 0, 0, 0],
            do_rotation=False,
            do_scale=False,
            do_translation_x=False,
            do_translation_y=False,
            font_size=font_size,
            height=(numpad_height if key in ('float','int','time') else keyboard_height),
            key_background_color=[0.6, 0.6, 0.6, 0.75],
            key_border=[1, 1, 1, 1],
            layout = layout,
            width=width)
        kb.key_background_disabled_normal = kb.key_disabled_background_normal # fixes VKeyboard missing attribute bug

def remove_soft_keyboard(app = None):
    """
    remove_soft_keyboard
    args: app - optional app object
    purpose: remove soft keyboard from screen
    """
    global layouts
    Logger.info('soft_keyboard: remove_soft_keyboard')
    app = app if app else App.get_running_app()
    unpickleable = app.app_data_dict['unpickleable']
    for key in layouts:
        kb = unpickleable[f'software keyboard {key}']
        if kb.parent:
            kb.parent.remove_widget(kb)

def render_keyboard_shortcut(screen, app = None):
    """
    render_keyboard_shortcut
    args: screen - screen object to mount button onto
        app - optional app object
    purpose: render keyboard shortcut on screen
    returns: button widget
    """
    app = app if app else App.get_running_app()
    button = None
    if app.app_data_dict['config']['software keyboard']['active']:
        button = MDIconButton(icon='keyboard-outline', icon_size=app.app_data_dict['window height']//19)
        screen.ids['keypad_button_container_id'].add_widget(button)
        button.bind(on_release=screen.summon_keyboard_press)
    return button

def set_keyboard_layout(parent, layout, key_press_method, app=None):
    """
    set_keyboard_layout
    args: parent = parent widget that has the keypad container layout
        layout - key indicating which layout to use for keyboard selection
        key_press_method - method to bind to for keypress processing
        app - optional kivy app object
    purpose: set new keyboard
    """
    Logger.info(f'soft_keyboard: set_keyboard_layout parent: {parent} layout: {layout} key_press_method: {key_press_method}')
    app = app if app else App.get_running_app()
    parent.ids['keypad_container_id'].clear_widgets()
    if app.app_data_dict['config']['software keyboard']['active']:
        kb = app.app_data_dict['unpickleable'][f'software keyboard {layout}']
        kb.on_key_up = key_press_method
        parent.ids['keypad_container_id'].add_widget(kb)
