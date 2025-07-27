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
import kivy.metrics
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.label import Label
from kivy.uix.bubble import Bubble
#local imports
import soft_keyboard
from selector_bubble_option import SelectorBubbleOption

class SelectorBubble(Bubble):

    def calc_x(self, app, center_x, width):
        """
        calc_x
        args: self - self object
            app - kivy running app object
            center_x - center x coordinate of text input
            width - width of select bubble
        purpose: calculate the X coordinate of selection bubble
        returns: selection bubble X coordinate
        """
        x =  center_x - (width // 2)
        if x > 0:
            x_right = x + width
            if x_right > app.app_data_dict['window width']:
                x = (app.app_data_dict['window width'] - width) // 2
            x = x if x > 0 else 0
        else:
            x = 0
        return x

    def render_selector_bubble(self, parent, text_input, bind_method, selection_items):
        """
        render_selector_bubble
        args: self - self object
            parent - widget to add selector bubble to
            text_input - text input widget for selection
            bind_method - method to bind presses to
            selection_items - list of selection items to show in selector bubble
        purpose: render selector bubble
        """
        Logger.info('selector_bubble: render bubble with {}'.format(selection_items))
        app = App.get_running_app()
        bubble_container = self.ids['selection_container_id']
        bubble_container.clear_widgets()
        height = 0
        widths = []
        test_label = Label(size_hint_x=None)
        for item_name in selection_items:
            selector_button = SelectorBubbleOption(text=item_name)
            selector_button.bind(on_release=bind_method)
            bubble_container.add_widget(selector_button)
            test_label.text = item_name
            test_label.font_size = selector_button.font_size
            test_label.texture_update()
            widths.append(test_label.texture_size[0])
            height += selector_button.height
        width = max(widths) + kivy.metrics.sp(10)
        self.size = (width, height)
        self.pos = (self.calc_x(app, text_input.center_x, width), text_input.y - height)
        if not self.parent:
            parent.add_widget(self)
        selection_items = bubble_container.children.copy()
        keyboard = soft_keyboard.get_mounted_keyboard(app=app)
        if keyboard:
            for selector_button in selection_items:
                if self.collide_widget(keyboard):
                    height -= selector_button.height
                    bubble_container.remove_widget(selector_button)
                    widths.pop()
                    width = max(widths) + kivy.metrics.sp(10)
                    self.size = (width, height)
                    self.pos = (self.calc_x(app, text_input.center_x, width), text_input.y - height)
                else:
                    break
