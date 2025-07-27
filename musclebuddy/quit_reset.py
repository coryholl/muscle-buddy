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
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.utils import platform
from kivymd.uix.boxlayout import MDBoxLayout
#local imports
import over_press

if platform == 'linux':
    import psutil

class QuitReset(MDBoxLayout):

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - mystery arguments
        """
        super(MDBoxLayout, self).__init__(**kwargs)
        if (platform == 'android' or (platform == 'linux' and
                any(process.name() == 'phosh' for process in psutil.process_iter()))):
            self.remove_widget(self.ids['minimize_button_container'])

    def maximize_button_press(self):
        """
        maximize_button_press
        args: self - self object
        purpose: maximize application
        """
        Logger.info('quit_reset: maximize_button_press')
        if over_press.protect(vibrate=True):
            Window.maximize()

    def minimize_button_press(self):
        """
        minimize_button_press
        args: self - self object
        purpose: minimize application
        """
        Logger.info('quit_reset: minimize_button_press')
        if over_press.protect(vibrate=True):
            Window.minimize()

    def on_stop(self, *kwargs):
        """
        on_stop
        args: self - self object
            kwargs - additional arguments sent from button press
        purpose: fix argument mismatch to on_stop application shutdown method
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            Clock.schedule_once(app.stop, 0.2)

    def reset(self, *kwargs):
        """
        reset
        args: self - self object
            kwargs - additional argument set from button press
        purpose: fix argument mismatch to reset application method
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            Clock.schedule_once(app.reset, 0.2)

    def reset_button_press(self):
        """
        reset_button_press
        args: self - self object
        purpose: render confirmation window for reset
        """
        Logger.info('quit_reset: shutdown_button_press')
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup('Reset Muscle Buddy?', self.reset)

    def shutdown_button_press(self):
        """
        shutdown_button_press
        args: self - self object
        purpose: render confirmation window for shutdown
        """
        Logger.info('quit_reset: shutdown_button_press')
        app = App.get_running_app()
        app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup('Quit Muscle Buddy?', self.on_stop)
