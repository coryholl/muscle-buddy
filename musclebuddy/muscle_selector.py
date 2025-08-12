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
from kivy.logger import Logger # debug
from kivy.uix.image import Image
from kivy.uix.label import Label
#local imports
import over_press

class MuscleSelector:
    color = {'selected': (0, 0.5, 0.8, 1), 'unselected': (0, 0, 0, 1)}
    selected_muscle = ''

    def map_muscle_state(self, muscle, gama):
        """
        map_muscle_state
        args: self - self object
            muscle - dictionary of muscle states to update
            gama - gama value of pixel
        purpose: default muscle state mapping for muscle selector.  Overridden in exercise creator
        """
        muscle[self.map_state_key] = 'selected' if gama else 'unselected'

    def muscle_touched(self, image, touch):
        """
        muscle_touched
        args: self - self object
            image - image object touched
            touch - touch object
        purpose: processes a muscle selection touch
        """
        Logger.info('muscle_selector: muscle_touched: touch.pos {}'.format(touch.pos))
        if image.collide_point(touch.x, touch.y):
            app = App.get_running_app()
#            if over_press.protect(app = app, vibrate=True):
            binding_box_ratio = image.width / image.height
            if binding_box_ratio >= image.image_ratio:
                scale = image.size[1] / image.texture_size[1]
                x_padding = (image.size[0] - (image.texture_size[0] * scale)) / 2
                x_coord = (touch.x - x_padding) / scale
                y_coord = image.texture_size[1] - (touch.y / scale)
                if 0 <= x_coord < image.texture_size[0] and 0 <= y_coord < image.texture_size[1]:
                    if over_press.protect(app = app, vibrate=True):
                        for muscle in app.app_data_dict['unpickleable']['muscle selector maps'].values():
                            if self.image_orientation in muscle and 'primary' in muscle[self.image_orientation]:
                                color = muscle[self.image_orientation]['primary']['core image'].read_pixel(x_coord,
                                    y_coord)
                                self.map_muscle_state(muscle, color[3])
                        self.render_muscles()

    def post_select_cleanup(self):
        """
        post_select_cleanup
        args: self - self object
        purpose: perform default muscle selection cleanup
        """
        app = App.get_running_app()
        for muscle in app.app_data_dict['unpickleable']['muscle selector maps'].values():
            muscle[self.map_state_key] = 'unselected'
        self.render_muscles()

    def render_muscles(self):
        """
        render_muscles
        args: self - self object
        purpose: render selector image
        """
        Logger.info('muscle_selector: render_muscles')
        app = App.get_running_app()
        image = Image(source=os.path.join('images',
            app.app_data_dict['image overlays']['Master'][self.image_orientation]), fit_mode='contain')
        image.bind(on_touch_up=self.muscle_touched)
        self.muscle_selector_container.clear_widgets()
        self.muscle_selector_container.add_widget(image)
        self.add_button.disabled = True # move cjh
        for self.selected_muscle, muscle in app.app_data_dict['unpickleable']['muscle selector maps'].items():
            if muscle[self.map_state_key] == 'selected' and self.image_orientation in muscle:
                self.muscle_selector_container.add_widget(Image(source=os.path.join('images',
                    muscle[self.image_orientation]['primary']['image file']), fit_mode='contain'))
                self.add_button.disabled = False
                break
        exercises = app.app_data_dict['unpickleable']['database'].get_exercises_by_muscle(self.selected_muscle)
        self.exercise_carousel.clear_widgets()
        for exercise in exercises:
            self.exercise_carousel.add_widget(Label(text=exercise['exercise_muscles_exercise_name'],
                font_size=app.app_data_dict['window height'] // 35))
        if self.add_button.disabled:
            self.exercise_carousel.add_widget(Label(
                text='Touch muscle for exercises.\nSwipe to choose a match.',
                font_size=app.app_data_dict['window height'] // 45))

    def select_orientation(self, image, touch, orientation):
        """
        select_orientation
        args: self - self object
            image - image object
            touch - touch object
            orientation - indicator of which orientation was pressed
        purpose: process orientation button press
        """
        if (image.collide_point(touch.x, touch.y) and over_press.protect(vibrate=True) and
                orientation in ('back', 'front')):
            self.selector_back_button_color = self.color['selected'] \
                if orientation == 'back' else self.color['unselected']
            self.selector_front_button_color = self.color['selected'] \
                if orientation == 'front' else self.color['unselected']
            self.image_orientation = orientation
            self.post_select_cleanup()
