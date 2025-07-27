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
import os
import shutil
import subprocess
from kivy.core.window import Window
from kivy.utils import platform

if platform == 'linux':
    import psutil

def disable_squeekboard():
    """
    disable_squeekboard
    purpose: disable squeekboard
    """
    set_squeekboard(False)

def enable_squeekboard():
    """
    enable_squeekboard
    purpose: enabel squeekboard
    """
    set_squeekboard(True)

def set_mobile_fullscreen():
    """
    set_mobile_fullscreen
    purpose: set fullscreen mode in case we are running on Plasma
    """
    if platform == 'linux' and not os.path.exists('no_fullscreen'):
        Window.maximize()
        Window.fullscreen = True

def set_squeekboard(enabled):
    """
    set_squeekboard
    args: enabled - boolean indicator as to if the squeekboard icon is to be enabled or disabled
    purpose: remove the manual icon button for keyboard to fix touch screen conflicts
    """
    if platform == 'linux' and any(process.name() == 'squeekboard' for process in psutil.process_iter()):
        try: # most efficient solution using PyGObject
            from gi.repository import Gio, GLib
            gso=Gio.Settings.new('org.gnome.desktop.a11y.applications')
            gso.set_value('screen-keyboard-enabled', GLib.Variant('b', enabled))
        except Exception as e: # dirty hack if PyGObject does not work
            subprocess.Popen([shutil.which('gsettings'), 'set', 'org.gnome.desktop.a11y.applications',
                'screen-keyboard-enabled', str(enabled).lower()], start_new_session=True)
