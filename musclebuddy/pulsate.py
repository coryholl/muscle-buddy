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
class Pulsate:
    """
    pulsate
    purpose: class for providing a reusable pulsating logic
    """
    color_value = 0.0
    increment = 0.0

    def __init__(self, color_value, increment):
        """
        __init__
        args: self - self object
            color_value - initial color value, needs to be between 0.0 and 1.0
            increment - positive or negative increment value
        purpose: initialize a pulation object for pulsating a color
        """
        self.color_value =  color_value
        self.increment = increment

    def get_next_pulse(self):
        """
        get_next_pulse
        args: self - self object
        purpose: generate a pulsing color value for a visual indicators
        returns: new color value
        """
        if round(self.color_value, 1) == 1.0:
            self.increment = -0.05
        elif round(self.color_value, 1) == 0.0:
            self.increment = 0.05
        self.color_value += self.increment
        return self.color_value

