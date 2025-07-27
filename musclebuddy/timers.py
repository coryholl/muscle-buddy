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
import datetime
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
#local imports
import over_press
import soft_keyboard
import stateful_clock
from generic_timer import GenericTimer # needed by Kivy engine
from stopwatch import StopWatch # neede by Kivy engine

class Timers(MDBoxLayout):
    local_time = StringProperty()

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            kwargs - unknown arguments to pass on to parent class
        purpose: initialize generic timers
        """
        super(MDBoxLayout, self).__init__(**kwargs)
        self.ids['timer'].keypad_container = self.ids['keypad_container_id']
        soft_keyboard.render_keyboard_shortcut(self)
        Clock.schedule_interval(self.set_clock, 1)

    def __exit__(self):
        """
        __exit__
        args: self - self object
        purpose: unschedule clock upon object shutdown
        """
        Clock.unschedule(self.set_clock)
        super(MDBoxLayout, self).__exit__()

    def set_clock(self, dt):
        """
        set_clock
        args: self - self object
            dt - time since last clock call
        """
        self.local_time = datetime.datetime.now().strftime('%a %b %d %I:%M:%S %p %G')

    def summon_keyboard_press(self, *kwargs):
        """
        summon_keyboard_press
        args: self - self object
            kwargs - kivy arguments
        purpose: provide method to summon keyboard on keyboard button press
        """
        if over_press.protect(vibrate=True):
            self.ids['timer'].state = 'pause'
            stateful_clock.unschedule(self.ids['timer'].get_time)
            time_pad = soft_keyboard.get_keyboard('time')
            time_pad.on_key_up = self.ids['timer'].key_press
            self.ids['keypad_container_id'].add_widget(time_pad)
            stateful_clock.schedule_interval(self.ids['timer'].timer_paused_indicator, 0.05)
