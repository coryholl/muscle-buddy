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
from kivy.uix.popup import Popup
#local imports
import over_press

class ConfirmationPopupWindow(Popup):
    button_methods = {
        'confirmation_button_id': None,
        'cancel_button_id': None
    }

    def bind_to_button(self, button_id, method):
        """
        bind_to_button
        args: self - self object
            button_id - kivy id of button
            method - method to bind to popup button
        purpose: remove old binding and add a new one
        """
        if self.button_methods[button_id]:
            self.ids[button_id].unbind(on_release=self.button_methods[button_id])
        self.button_methods[button_id] = method
        self.ids[button_id].bind(on_release=self.button_methods[button_id])

    def cancel_press(self, *kwargs):
        """
        cancel_press
        args: self - self object
            kwargss - additional arguments sent from button press
        purpose: restore page to pre-press state
        """
        if over_press.protect(vibrate=True):
            self.dismiss()

    def open_confirm_popup(self, text, confirm_bind_method, over_press_protected=False, cancel_bind_method=None):
        """
        open_confirm_popup
        args: self - self object
            text - text to display in confirmation window.
            confirm_bind_method - method to bind to the confirmation button
            over_press_protected - optional indicator as to if over_press protection has already been applied
            cancel_bind_method - optional method to bind to cancel button
        purpose: open confirmation window
        """
        if over_press_protected or over_press.protect(vibrate=True):
            self.title = text
            self.bind_to_button('confirmation_button_id', confirm_bind_method)
            cancel_bind_method = cancel_bind_method if cancel_bind_method else self.cancel_press
            self.bind_to_button('cancel_button_id', cancel_bind_method)
            self.open()
