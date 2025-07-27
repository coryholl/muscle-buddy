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

def check_protect(app = None, now = None):
    """
    check_protect
    args: app - optional app object
        now - optional timestamp object
    purpose: check if over press protection is needed
    returns: true if over press protection is needed, false otherwise
    """
    app = app if app else App.get_running_app()
    now = now if now else time.time()
    return ((now - app.app_data_dict['global properties']['last button press time']) > 0.2)

def protect(app=None, now=None, vibrate=False):
    """
    protect
    args: app - optional app object
        now - optional timestamp object
        vibrate - optional vibrate feedback that may trigger if passes overpress check
    purpose: global function to protect event over press by storing a timer state
    returns: true if in over press protect state, false otherwise
    """
    app = app if app else App.get_running_app()
    now = now if now else time.time()
    retval = check_protect(app = app, now = now)
    if retval:
        set_protect(app = app, now = now, vibrate = vibrate)
    return retval

def set_protect(app = None, now = None, vibrate = False):
    """
    set_protect
    args: app - optional app object
        now - optional timestamp object
        vibrate - optional vibrate feedback that may trigger when setting overpress protect
    purpose: set the over press global variable
    """
    app = app if app else App.get_running_app()
    if vibrate:
        app.app_data_dict['unpickleable']['vibrator'].vibrate('button')
    now = now if now else time.time()
    app.app_data_dict['global properties']['last button press time'] = now
