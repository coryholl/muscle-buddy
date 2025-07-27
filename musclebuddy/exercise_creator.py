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
from kivy.logger import Logger
from kivy.properties import ColorProperty
from kivy.uix.image import Image
from kivymd.uix.floatlayout import MDFloatLayout
# local imports
import over_press
import soft_keyboard
from muscle_selector import MuscleSelector
from selector_bubble import SelectorBubble
from text_input_util import TextInputUtil

class ExerciseCreator(MDFloatLayout, TextInputUtil, MuscleSelector):
    all_input_fields = {}
    color = {'primary': '#FFD760', 'secondary': '#7AD1B0', 'selected': (0, 0.5, 0.8, 1), 'unselected': (0, 0, 0, 1)}
    exercise_selector_bubble = None
    image_orientation = 'front'
    selected = ('not selected', 'primary', 'secondary')
    map_state_key = 'exercise creator image state'
    muscle_selector_container = None
    selector_back_button_color = ColorProperty((0, 0, 0, 1))
    selector_front_button_color = ColorProperty((0, 0.5, 0.8, 1))
    keyboard_button = None # needs to be set in config upon restore

    def __init__(self, data_dict, **kwargs):
        """
        __init__
        args: self - self object
            data_dict - application data dictionary
            kwargs - remaining init arguments for MBBoxLayout
        purpose: reload trainer sate if unpaused on Android
        """
        Logger.info('exercise_creator: __init__')
        super(MDFloatLayout, self).__init__(**kwargs)
        image = Image(source=os.path.join('images', data_dict['image overlays']['Master']['front']), fit_mode='contain')
#        image = Image(source=data_dict['image overlays']['Master']['front'], fit_mode='contain')   # atlas code
        image.bind(on_touch_up=self.muscle_touched)
        self.muscle_selector_container = self.ids['muscle_selector_id']
        self.ids['muscle_selector_id'].add_widget(image)
        self.exercise_selector_bubble = SelectorBubble()
        self.all_input_fields['exercise name'] = self.ids['exercise_name']
        self.keyboard_button = soft_keyboard.render_keyboard_shortcut(self)

    def add_exercise(self):
        """
        add_exercise
        args: self - self object
        purpose: add new or update existing exercise in database
        """
        Logger.info('exercise_creator: add_exercise')
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            exercise_name = self.ids['exercise_name'].text.strip()
            if exercise_name:
                exercise = app.app_data_dict['unpickleable']['database'].get_exercise(exercise_name)
                if exercise:
                    app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
                        f'Replace "{exercise_name}" in exercise database?', self.replace_confirmed,
                        over_press_protected = True)
                else:
                    self.insert_exercise()

    def bubble_press(self, bubble_button):
        """
        bubble_press
        args: self - self object
            bubble_button - other arguments
        purpose: process bubble selection
        """
        Logger.info('exercise_creator: bubble_press selection text = {}'.format(bubble_button.text))
        if over_press.protect(vibrate=True):
            self.ids['exercise_name'].text = bubble_button.text
            self.defocus_all()
            self.load_muscle_states()

    def deletion_confirmed(self, button):
        """
        deletion_confirmed
        args: self - self object
            button - button widget
        purpose: process deletion confirmation button press for exercise
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            self.ids['delete_exercise_button_id'].disabled = True
            exercise_name = self.ids['exercise_name'].text.strip()
            unpickleable = app.app_data_dict['unpickleable']
            unpickleable['database'].delete_exercise(exercise_name)
            unpickleable['database'].delete_exercise_muscle_mapping(exercise_name)
            unpickleable['confirmation popup'].dismiss()

    def delete_exercise(self):
        """
        delete_exercise
        args: self - self object
        purpose: delete exercise from database
        """
        Logger.info('exercise_creator: delete_exercise')
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            exercise_name = self.ids['exercise_name'].text.strip()
            if exercise_name:
                exercise = app.app_data_dict['unpickleable']['database'].get_exercise(exercise_name)
                if exercise:
                    app.app_data_dict['unpickleable']['confirmation popup'].open_confirm_popup(
                        f'Delete "{exercise_name}" from exercise database?', self.deletion_confirmed,
                        over_press_protected = True)

    def insert_exercise(self):
        """
        insert_exercise
        args: self - self object
        purpose: insert or replace an exercise in app database
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        db = unpickleable['database']
        exercise_name = self.ids['exercise_name'].text.strip()
        db.store_exercise(exercise_name)
        db.delete_exercise_muscle_mapping(exercise_name)
        for muscle_name, muscle in app.app_data_dict['unpickleable']['muscle selector maps'].items():
            if muscle['exercise creator image state'] in ('primary', 'secondary'):
                db.store_exercise_muscle_mapping(exercise_name, muscle_name, muscle['exercise creator image state'])
        app.app_data_dict['image overlays'] = unpickleable['dictionary manager'].get_image_overlays(db)
        self.ids['delete_exercise_button_id'].disabled = False

    def load_muscle_states(self):
        """
        load_muscle_states
        args: self - self object
        purpose: load muscle highlight info from exercise database
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        for muscle in unpickleable['muscle selector maps'].values():
            muscle['exercise creator image state'] = 'not selected'
        muscle_highlights = unpickleable['database'].get_muscle_by_exercise(self.ids['exercise_name'].text.strip())
        for muscle_highlight in muscle_highlights:
            unpickleable['muscle selector maps'][muscle_highlight['muscle_name']]['exercise creator image state'] = (
                muscle_highlight)['focus']
        self.render_muscles()

    def map_muscle_state(self, muscle, gama):
        """
        map_muscle_state
        args: self - self object
            muscle - dictionary of muscle states to update
            gama - gama value of pixel
        purpose: muscle state mapping for muscle selector.
        """
        if gama:
            new_index = (self.selected.index(muscle[self.map_state_key]) + 1) % len(self.selected)
            muscle[self.map_state_key] = self.selected[new_index]

    def muscle_touched(self, image, touch):
        """
        muscle_touched
        args: self - self object
            image - image object touched
            touch - touch object
        purpose: processes a muscle selection touch
        """
        Logger.info(f'exercise_creator: muscle_touched touch.x {touch.x} touch.y {touch.y}')
        if (not (self.exercise_selector_bubble.parent and
                self.exercise_selector_bubble.collide_point(touch.x, touch.y)) and
                not self.keyboard_button.collide_point(touch.x, touch.y) and
                image.collide_point(touch.x, touch.y) and over_press.check_protect()):
            super().muscle_touched(image, touch)
            self.defocus_all()

    def post_select_cleanup(self):
        """
        post_select_cleanup
        args: self - self object
        purpose: perform muscle selection cleanup
        """
        self.render_muscles()
        self.defocus_all()

    def render_muscles(self):
        """
        render_muscles
        args: self - self object
        purpose: render selector image
        """
        Logger.info('exercise_creator: render_muscles')
        app = App.get_running_app()
        image = Image(source=os.path.join('images',
            app.app_data_dict['image overlays']['Master'][self.image_orientation]), fit_mode='contain')
        image.bind(on_touch_up=self.muscle_touched)
        self.muscle_selector_container.clear_widgets()
        self.muscle_selector_container.add_widget(image)
        selection_text = ''
        split_text = True
        for muscle_name, muscle in app.app_data_dict['unpickleable']['muscle selector maps'].items():
            if muscle[self.map_state_key] in ('primary', 'secondary'):
                if self.image_orientation in muscle:
                    self.muscle_selector_container.add_widget(Image(source=os.path.join('images',
                        muscle[self.image_orientation][muscle[self.map_state_key]]['image file']),
                        fit_mode='contain'))
                if split_text and len(selection_text) > 200:
                    selection_text += '\n'
                    split_text = False
                selection_text += '[b]{}[/b][color={}]{}[/color]'.format(' | ' if selection_text else '',
                    self.color[muscle[self.map_state_key]], muscle_name)
        self.ids['exercise_creator_label'].text = selection_text if selection_text else \
            'Select muscles\n[color=#FFD760][b]primary muscles[/b][/color] | [color=#7AD1B0][b]secondary muscles[/b][/color]'

    def replace_confirmed(self, button):
        """
        replace_confirmed
        args: self - self object
            button - button widget
        purpose: process replace confirmation button press for exercise
        """
        app = App.get_running_app()
        if over_press.protect(app=app, vibrate=True):
            self.insert_exercise()
            app.app_data_dict['unpickleable']['confirmation popup'].dismiss()

    def text_input(self):
        """
        text_input
        args: self - self object
        purpose: perform any behavior needed when exercise text changes
        """
        Logger.info('exercise_creator: text_input')
        stripped_exercise_name = self.ids['exercise_name'].text.strip()
        if stripped_exercise_name:
            self.ids['add_exercise_button_id'].disabled = True if stripped_exercise_name == 'rest' else False
            app = App.get_running_app()
            db = app.app_data_dict['unpickleable']['database']
            exercise_matches = db.get_exercises(stripped_exercise_name,
                app.app_data_dict['config']['selection bubble']['selection limit'])
            if exercise_matches:
                exercise_names = [exercise['exercise_name'] for exercise in exercise_matches]
                self.exercise_selector_bubble.render_selector_bubble(self, self.ids['exercise_name'], self.bubble_press,
                    exercise_names)
                self.ids['delete_exercise_button_id'].disabled = not bool(db.get_exercise(stripped_exercise_name))
            else:
                self.ids['delete_exercise_button_id'].disabled = True
                self.remove_widget(self.exercise_selector_bubble)
        else:
            self.ids['add_exercise_button_id'].disabled = self.ids['delete_exercise_button_id'].disabled = True
            self.remove_widget(self.exercise_selector_bubble)
        over_press.set_protect()
