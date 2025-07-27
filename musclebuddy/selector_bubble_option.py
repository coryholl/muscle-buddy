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
from kivy.logger import Logger
from kivymd.uix.button import MDFlatButton
# local imports
import over_press

class SelectorBubbleOption(MDFlatButton):

    def button_press(self, selection_text):
        """
        button_press
        args: self - self object
        purpose: process a selection press of a selection bubble
        """
        if over_press.protect(vibrate=True):
            Logger('selector_bubble_option: selected "{}"'.format(selection_text))