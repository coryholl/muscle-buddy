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

def restore_clock(method):
    """
    restore_clock
    args: method - method to restore schedule
    purpose: restore a clock from state
    """
    app = App.get_running_app()
    if method.__qualname__ in app.app_data_dict['global properties']['clocks']:
        schedule_interval(method, app.app_data_dict['global properties']['clocks'][method.__qualname__])

def schedule_interval(method, interval):
    """
    schedule_interval
    args: method - method to schedule
        interval - clock interval to call method
    purpose: schedule a clock and record state
    """
    app = App.get_running_app()
    app.app_data_dict['global properties']['clocks'][method.__qualname__] = interval
    app.app_data_dict['unpickleable']['clock processes'][method.__qualname__] = method
    Clock.schedule_interval(app.app_data_dict['unpickleable']['clock processes'][method.__qualname__], interval)

def unschedule(method):
    """
    unschedule
    args: method - method to unschedule
    purpose: unschedule a clock and record its state.
    """
    app = App.get_running_app()
    if method.__qualname__ in app.app_data_dict['global properties']['clocks']:
        if method.__qualname__ in app.app_data_dict['unpickleable']['clock processes']:
            Clock.unschedule(app.app_data_dict['unpickleable']['clock processes'][method.__qualname__])
            del app.app_data_dict['unpickleable']['clock processes'][method.__qualname__]
        del app.app_data_dict['global properties']['clocks'][method.__qualname__]

def unschedule_all():
    """
    unschedule_all
    purpose: unschedule all stateful clocks
    """
    app = App.get_running_app()
    for name, clock in list(app.app_data_dict['unpickleable']['clock processes'].items()):
        unschedule(clock)
