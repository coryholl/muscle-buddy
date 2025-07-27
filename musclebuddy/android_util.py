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
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass
#    from android.permissions import Permission, request_permissions, check_permission
#    from android.storage import app_storage_path, primary_external_storage_path, secondary_external_storage_path

def prevent_android_crash(window, key, scancode, codepoint, modifier):
    """
    prevent_android_crash
    args: window - unused
        key - numeric key code
        scancode - unused
        codepoint - unused
        modifier - unused
    purpose: prevent Android from crashing when back button is pressed
    returns: true if back button pressed else false
    """
    return True if key == 27 else False

def reboot_android():
    """
    reboot_android
    purpose: reboot app on an android OS
    """
    if platform == 'android':
        Intent = autoclass("android.content.Intent")
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        System = autoclass("java.lang.System")
        activity = PythonActivity.mActivity
        intent = Intent(activity.getApplicationContext(), PythonActivity)
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)
        activity.startActivity(intent)
        System.exit(0)

