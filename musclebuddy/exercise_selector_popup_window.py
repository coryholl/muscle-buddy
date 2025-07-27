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
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.logger import Logger # debug
from kivy.properties import ColorProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.carousel import Carousel
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button.button import MDIconButton
#local imports
import over_press
from muscle_selector import MuscleSelector

class ExerciseSelectorPopupWindow(Popup, MuscleSelector):
    muscle_selector_container = None
    exercise_carousel = None
    image_orientation = 'front'
    map_state_key = 'workout builder image state'
    add_button = None
    selector_back_button_color = ColorProperty((0, 0, 0, 1))
    selector_front_button_color = ColorProperty((0, 0.5, 0.8, 1))
    front_image_button = None
    back_image_button = None
    selected_muscle = ''

    def __init__(self, **kwargs):
        """
        __init__
        args: self - self object
            data_dict - application data dictionary
            kwargs - remaining init arguments for MBBoxLayout
        purpose: set initial base image
        """
        super(Popup, self).__init__(**kwargs)
        Logger.info('exercise_creator_popup_window: __init__ ids: {}'.format(self.ids))
        app = App.get_running_app()
        overlays = app.app_data_dict['image overlays']
        popup_container = RelativeLayout()
        box_container = MDBoxLayout(orientation='vertical')
        select_box = MDBoxLayout(orientation='horizontal', size_hint_y=0.1)
        box_container.add_widget(select_box)
        self.exercise_carousel = Carousel(loop=True, size_hint_x=0.8)
        select_box.add_widget(self.exercise_carousel)
        self.exercise_carousel.add_widget(Label(font_size=(app.app_data_dict['window height'] // 45),
            text='Touch muscle for exercises.\nSwipe to choose a match.'))
        self.muscle_selector_container = RelativeLayout(size_hint_y=0.8)
        box_container.add_widget(self.muscle_selector_container)
        button_container = MDBoxLayout(orientation='horizontal', size_hint_y=0.1)
        box_container.add_widget(button_container)
        image = Image(source=os.path.join('images', overlays['Master']['front']), fit_mode='contain')
        image.bind(on_touch_up=self.muscle_touched)
        self.muscle_selector_container.add_widget(image)
        button_container.add_widget(Widget())
        icon_size = app.app_data_dict['window height'] // 19
        self.add_button = MDIconButton(disabled=True, icon='check-bold', icon_color=(0, 1, 0, 1), icon_size=icon_size,
            md_bg_color=(0.3, 0.3, 0.3, 1), on_release=self.confirm_press, theme_icon_color='Custom')
        button_container.add_widget(self.add_button)
        button_container.add_widget(Widget())
        button_container.add_widget(MDIconButton(icon='close-thick', icon_color=(1, 0, 0, 1), icon_size=icon_size,
            md_bg_color=(0.3, 0.3, 0.3, 1), on_release=self.cancel_press, theme_icon_color='Custom'))
        button_container.add_widget(Widget())
        popup_container.add_widget(box_container)
        left_anchor = AnchorLayout(anchor_x='left', anchor_y='center')
        self.front_button_image = Image(keep_data=True, on_touch_up=self.select_front, size_hint_x=0.1,
            size_hint_y=0.12, source=os.path.join('images', overlays['Master']['front']))
        left_anchor.add_widget(self.front_button_image)
        right_anchor = AnchorLayout(anchor_x='right', anchor_y='center')
        self.back_button_image = Image(keep_data=True, on_touch_up=self.select_back, size_hint_x=0.1, size_hint_y=0.12,
            source=os.path.join('images', overlays['Master']['back']))
        right_anchor.add_widget(self.back_button_image)
        popup_container.add_widget(left_anchor)
        popup_container.add_widget(right_anchor)
        self.content = popup_container

    def cancel_press(self, *kwargs):
        """
        cancel_press
        args: self - self object
            kwargss - additional arguments sent from button press
        purpose: restore page to pre-press state
        """
        Logger.info('exercise_creator_popup_window: cancel_press')
        if over_press.protect(vibrate=True):
            self.dismiss()

    def confirm_press(self, *kwargs):
        """
        confirm_press
        args: self - self object
            kwargs - list of arguments
        purpose: confirm exercise selection and callback to workout builder
        """
        Logger.info('exercise_creator_popup_window: confirm_press {}'.format(kwargs))
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            app.app_data_dict['unpickleable']['workout builder'].exercise_selected(
                self.exercise_carousel.current_slide.text, self.selected_muscle)
            self.dismiss()

    def on_open(self):
        """
        on_open
        args: self - self object
        purpose: handle any initialization needed on popup render
        """
        Logger.info('exercise_selector_popup_window: on_open')
        if self.image_orientation == 'front':
            self.select_button(self.front_button_image, self.back_button_image)
        else:
            self.select_button(self.back_button_image, self.front_button_image)

    def open_with_muscle(self, muscle_name, exercise_name):
        """
        open_with_muscle
        args: self - self object
            muscle_name - the name of the selected muscle
            exercise_name - the name of the exercise to select
        purpose: provide a custom popup open method for setting muscle selector state
        """
        Logger.info(f'exercise_selector_popup_window: open_with_muscle {muscle_name} {exercise_name}')
        app = App.get_running_app()
        muscle_map = app.app_data_dict['unpickleable']['muscle selector maps']
        for muscle_key, muscle in muscle_map.items():
            if muscle_key == muscle_name:
                muscle[self.map_state_key] = 'selected'
                if self.image_orientation not in muscle:
                    if self.image_orientation == 'front':
                        self.image_orientation = 'back'
                        self.selector_back_button_color = self.color['selected']
                        self.selector_front_button_color = self.color['unselected']
                    else:
                        self.image_orientation = 'front'
                        self.selector_back_button_color = self.color['unselected']
                        self.selector_front_button_color = self.color['selected']
                    self.post_select_cleanup()
            else:
                muscle[self.map_state_key] = 'not selected'
        self.render_muscles()
        while self.exercise_carousel.current_slide.text != exercise_name:
            self.exercise_carousel.load_next()
            if not self.exercise_carousel.index:
                break
        self.open()

    def select_back(self, image, touch):
        """
        select_back
        args: self - self object
            kwargs list of arguments
        purpose: select front view of muscle selector
        """
        if image.collide_point(touch.x, touch.y):
            self.select_button(self.back_button_image, self.front_button_image)
        self.select_orientation(image, touch, 'back')

    def select_button(self, selected_button, unselected_button):
        """
        select_button
        args: self - self object
            selected_button - button widget to set to selected color
            unselected_button - button widget to set to unselected color
        purpose: toggle orientation button colors
        """
        with selected_button.canvas.before:
            Color(0, 0.5, 0.8, 1)
            RoundedRectangle(pos=selected_button.pos, size=selected_button.size)
        with unselected_button.canvas.before:
            Color(0, 0, 0, 1)
            RoundedRectangle(pos=unselected_button.pos, radius=(8,8,8,8), size=unselected_button.size)

    def select_front(self, image, touch):
        """
        select_front
        args: self - self object
            kwargs list of arguments
        purpose: select front view of muscle selector
        """
        if image.collide_point(touch.x, touch.y):
            self.select_button(self.front_button_image, self.back_button_image)
        self.select_orientation(image, touch, 'front')
