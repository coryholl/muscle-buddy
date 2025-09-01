# Copyright (C) 2025 Cory Jon Hollingsworth
#
# This file is part of the Pantheon suite.
#
# The Pantheon suite is free software: you can redistribute it and/or modify
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
# along with the Pantheon suite.  If not, see <https://www.gnu.org/licenses/>.
from kivy.app import App
from kivy.utils import platform
from kivy.logger import Logger

__version__ = '1.0.0'

if platform == 'linux':
    import evdev
    from evdev import ecodes, InputDevice, ff
elif platform in ('android', 'ios'):
    from plyer import vibrator

class Vibrator:
    button_rumble = None
    alarm_rumble = None
    durations = {'alarm': {'ms': 1000}, 'button': {'ms': 100}, 'finish': {'ms': 5000}}
    button_press_duration = 100
    alarm_duration = 1000
    vibrator_device = None

    def __init__(self):
        """
        __init__
        args: self - self object
        purpose: initialize vibrator device
        """
        if platform == 'android':
            self.android_init()
        elif platform == 'linux':
            self.linux_init()

    def __exit__(self):
        """
        __exit__
        args: self - self object
        puprpose perform cleanup for shutdown
        """
        if platform == 'linux' and self.vibrator_device:
            for key in self.durations:
                self.vibrator_device.erase_effect(self.durations[key]['effect'])
            self.vibrator_device.close()

    def android_init(self):
        """
        android_init
        args: self - self object
        purpose: perform vibrator initialization for Android
        """
        if vibrator.exists():
            for key in self.durations:
                self.durations[key]['seconds'] = self.durations[key]['ms'] / 1000
            app = App.get_running_app()
            app.app_data_dict['unpickleable']['config'].enable_button('vibrate')

    def linux_init(self):
        """
        linux_init
        args: self - self object
        purpose: initialize vibrator for Linux
        """
        self.vibrator_device = None
        for path in evdev.list_devices():
            device = evdev.InputDevice(path)
            if evdev.ecodes.EV_FF in device.capabilities():
                self.vibrator_device = device
                break
            device.close()
        if self.vibrator_device:
            for key in self.durations:
                self.durations[key]['effect'] = self.register_linux_rumble_effect(self.durations[key]['ms'])
            app = App.get_running_app()
            app.app_data_dict['unpickleable']['config'].enable_button('vibrate')

    def register_linux_rumble_effect(self, duration):
        """
        register_linux_rumble_effect
        args: self - self object
            duration - length of rumble in ms
        purpose: register a vibrator effect
        returns: effect id for interfacing with vibrator hardware
        """
        effect_id = None
        try:
            rumble = ff.Rumble(strong_magnitude=0x0000, weak_magnitude=0xffff)
            effect_type = ff.EffectType(ff_rumble_effect=rumble)
            effect_trigger = ff.Trigger(0, 0)
            effect_replay = ff.Replay(duration, 0)
            effect = ff.Effect(ecodes.FF_RUMBLE, -1, 0, effect_trigger, effect_replay, effect_type)
            effect_id = self.vibrator_device.upload_effect(effect)
        except Exception as e:
            Logger.info('Vibrator: exception setting up vibrator: {}'.format(str(e)))
        return effect_id

    def vibrate(self, vibrate_type):
        """
        button_vibrate
        args: self - self object
            vibrate_type - either 'alarm', 'button' or 'finish' for selecting right type of vibration
        purpose: generate vibration for button press
        """
        app = App.get_running_app()
        if app.app_data_dict['config']['vibrate']['active']:
            if platform == 'linux':
                if self.vibrator_device:
                    self.vibrator_device.write(ecodes.EV_FF, self.durations[vibrate_type]['effect'], 1)
            elif platform in ('android', 'ios'):
                if vibrator.exists():
                    vibrator.vibrate(self.durations[vibrate_type]['seconds'])
