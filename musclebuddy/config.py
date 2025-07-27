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
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton
from kivymd.uix.gridlayout import MDGridLayout
# local imports
import hard_keyboard
import over_press
import soft_keyboard

class Config(MDBoxLayout):
    sound_off_icon = 'volume-off'
    sound_high_icon = 'volume-high'
    sound_medium_icon = 'volume-medium'
    sound_low_icon = 'volume-low'
    sound_mute_icon = 'volume-mute'
    toggle_map = {
        'hardware keyboard': {
            'button id': 'hardware_keyboard_button_id',
            'icon': ('keyboard-off', 'keyboard'),
            'label id': 'hardware_keyboard_label_id',
            'text': ('hardware\nkeyboard off', 'hardware\nkeyboard on')
        },
        'software keyboard': {
            'button id': 'software_keyboard_button_id',
            'icon': ('keyboard-off-outline', 'keyboard-outline'),
            'label id': 'software_keyboard_label_id',
            'text': ('software\nkeyboard off', 'software\nkeyboard on')
        },
        'vibrate': {
            'button id': 'vibrate_button_id',
            'icon': ('vibrate-off', 'vibrate'),
            'label id': 'vibrate_label_id',
            'text': ('vibrate off', 'vibrate on')
        }
    }
    vibrator_button = None
    vibrator_label = None

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - MDBoxLayout arguments
        purpose: initialize values on config page
        """
        super().__init__(**kwargs)
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['vibrate toggle method'] = self.toggle_vibrate
        config = app.app_data_dict['config']
        selection_limit = int(config['selection bubble']['selection limit'])
        self.ids['select_bubble_label_id'].text = f'selector size: {selection_limit}'
        self.ids['selector_bubble_limit_id'].value = selection_limit
        if platform == 'linux':
            app.app_data_dict['unpickleable']['hardware keyboard toggle method'] = self.toggle_hardware_keyboard
            self.enable_button('hardware keyboard')
        self.set_config_gui(config['software keyboard']['active'], 'software keyboard', app=app)
        self.ids['volume_slider_id'].value = config['volume']['percent']
        self.set_volume_icon()

    def disable_soft_keyboard(self):
        """
        disable_soft_keyboard
        args: self - self object
        purpose: disable software keyboard throughout application
        """
        app = App.get_running_app()
        soft_keyboard.remove_soft_keyboard()
        unpickleable = app.app_data_dict['unpickleable']
        for key in ('exercise creator', 'set recorder', 'timers', 'workout builder', 'workout reader'):
            unpickleable[key].ids['keypad_button_container_id'].clear_widgets()
        unpickleable['trainer']['classic strength training'].ids['keypad_button_container_id'].clear_widgets()
        unpickleable['trainer']['timed, random, muscle confusion'].ids['keypad_button_container_id'].clear_widgets()

    def enable_button(self, button_key):
        """
        enable_button
        args: self - self object
            button_key - key of button for indexing dictionaries
        purpose: create config toggle button
        """
        app = App.get_running_app()
        on = app.app_data_dict['config'][button_key]['active']
        unpickleable = app.app_data_dict['unpickleable']
        button = unpickleable[f'{button_key} button'] = MDIconButton(icon=self.toggle_map[button_key]['icon'][int(on)],
            icon_size=app.app_data_dict['window height'] // 19, on_release=unpickleable[f'{button_key} toggle method'])
        label = unpickleable[f'{button_key} label'] = Label(font_size=app.app_data_dict['window height'] // 40,
            halign='center', text=self.toggle_map[button_key]['text'][int(on)])
        box_layout = MDBoxLayout(orientation='horizontal')
        box_layout.add_widget(Widget())
        box_layout.add_widget(button)
        box_layout.add_widget(Widget())
        grid_layout = MDGridLayout(cols=1)
        grid_layout.add_widget(Widget())
        grid_layout.add_widget(box_layout)
        grid_layout.add_widget(label)
        self.ids['control_panel_id'].add_widget(grid_layout)

    def enable_soft_keyboard(self):
        """
        enable_soft_keyboard
        args: self - self object
        purpose: enable software keyboard through application
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        size = app.app_data_dict['window height'] // 19
        for key in ('exercise creator', 'set recorder', 'timers', 'workout builder', 'workout reader'):
            button = MDIconButton(icon='keyboard-outline', icon_size=size)
            unpickleable[key].ids['keypad_button_container_id'].add_widget(button)
            button.bind(on_release=unpickleable[key].summon_keyboard_press)
        trainer = unpickleable['trainer']
        for key in ('classic strength training', 'timed, random, muscle confusion'):
            button = MDIconButton(icon='keyboard-outline', icon_size=size)
            trainer[key].ids['keypad_button_container_id'].add_widget(button)
            button.bind(on_release=trainer[key].summon_keyboard_press)

    def selector_bubble_slider_touched(self):
        """
        selector_bubble_slider_touched
        args: self - self object
        purpose: set selector bubble limit value
        """
        app = App.get_running_app()
        selection_limit = int(self.ids['selector_bubble_limit_id'].value)
        app.app_data_dict['config']['selection bubble']['selection limit'] = selection_limit
        self.ids['select_bubble_label_id'].text = f'selector size: {selection_limit}'

    def set_config_gui(self, on, key, app = None):
        """
        set_config_gui
        args: self - self object
            on - boolean indicator as to if config option is on or off
        purpose: set gui representation of config toggle state
        """
        Logger.info('config: on: {} key: {}'.format(on, key))
        app = app if app else App.get_running_app()
        mapping = self.toggle_map[key]
        self.ids[mapping['button id']].icon = mapping['icon'][int(on)]
        self.ids[mapping['label id']].text = mapping['text'][int(on)]
        app.app_data_dict['config'][key]['active'] = on

    def set_volume_icon(self):
        """
        set_volume_icon
        args: self - self object
        purpose: set icon volume icon based on slider location
        """
        value = self.ids['volume_slider_id'].value
        if not value:
            self.ids['volume_mute_button_id'].icon = self.sound_off_icon
        elif 0 <= value <= 33.3:
            self.ids['volume_mute_button_id'].icon = self.sound_low_icon
        elif 33.3 <= value <= 66.6:
            self.ids['volume_mute_button_id'].icon = self.sound_medium_icon
        else:
            self.ids['volume_mute_button_id'].icon = self.sound_high_icon

    def toggle_hardware_keyboard(self, *kwargs):
        """
        toggle_vibrate
        args: self - self object
            kwargs - additional arguments
        purpose: toggle vibrator
        """
        self.toggle_py_button('hardware keyboard')
        hard_keyboard.unbind_keyboard()

    def toggle_kv_button(self, key): # used in config.kv
        """
        toggle_kv_button
        args: self - self object
            key - key of toggle button
        purpose: toggle button state
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            mapping = self.toggle_map[key]
            self.set_config_gui((self.ids[mapping['button id']].icon == mapping['icon'][0]), key, app=app)
            if key == 'software keyboard':
                if app.app_data_dict['config']['software keyboard']['active']:
                    self.enable_soft_keyboard()
                else:
                    self.disable_soft_keyboard()

    def toggle_mute(self):
        """
        toggle_mute
        args: self - self object
        purpose: mute or unmute sound
        """
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            if self.ids['volume_mute_button_id'].icon == self.sound_mute_icon:
                self.set_volume_icon()
                app.app_data_dict['config']['volume']['mute'] = False
            else:
                self.ids['volume_mute_button_id'].icon = self.sound_mute_icon
                app.app_data_dict['config']['volume']['mute'] = True
            app.app_data_dict['unpickleable']['sound'].set_all_volumes()

    def toggle_py_button(self, key):
        """
        toggle_py_button
        args: self - self object
            key - key for generating dict indexes for button
        purpose: toggle dynamic button's status
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            mapping = self.toggle_map[key]
            button = app.app_data_dict['unpickleable'][f'{key} button']
            on = app.app_data_dict['config'][key]['active'] = (button.icon == mapping['icon'][0])
            button.icon = mapping['icon'][int(on)]
            app.app_data_dict['unpickleable'][f'{key} label'].text = mapping['text'][int(on)]

    def volume_slider_touched(self):
        """
        volume_slider_touched
        args: self - selv object
        purpose: process volume slider touch
        """
        app = App.get_running_app()
        self.set_volume_icon()
        app.app_data_dict['config']['volume']['percent'] = self.ids['volume_slider_id'].value
        app.app_data_dict['unpickleable']['sound'].set_all_volumes()

    def toggle_vibrate(self, *kwargs):
        """
        toggle_vibrate
        args: self - self object
            kwargs - additional arguments
        purpose: toggle vibrator
        """
        self.toggle_py_button('vibrate')
