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
import re
from kivy.app import App
from kivy.logger import Logger
#local imports
import hard_keyboard
import over_press
import soft_keyboard
from hard_keyboard_state import HardKeyboardState
from workout_text_field import WorkoutTextField

class TextInputUtil(HardKeyboardState):
    input_fields = [] # placeholder attribute for abstract class
    kilogram_icon = 'weight-kilogram'
    pound_icon = 'weight-pound'
    left_right_off_icon = 'hand-clap-off'
    left_right_on_icon = 'hand-clap'
    left_right_on_string = 'single set'
    left_right_off_string = 'left/right sets'
    prefix_string = '' # placeholder attribute for abstract class
    focus_order = []
    timed_on_icon = 'timer'
    timed_off_icon = 'abacus'
    timed_on_string = 'timed'
    timed_off_string = 'reps'

    def activate_keyboards(self, input_field):
        """
        activate_keyboards
        args: self - self object
            input_field - text input field object
        purpose: activate keyboards for a field
        """
        app = App.get_running_app()
        if app.app_data_dict['config']['software keyboard']['active']:
            keypad = soft_keyboard.get_keyboard(input_field.input_field_type, app=app)
            keypad.on_key_up = self.soft_key_press
            if keypad.parent:
                keypad.parent.remove_widget(keypad)
            self.ids['keypad_container_id'].add_widget(keypad)
        if app.app_data_dict['config']['hardware keyboard']['active']:
            hard_keyboard.get_hard_keyboard(input_field, on_key_down=self.hard_key_press,
                                            on_key_up=self.hard_key_release)

    def defocus_all(self, skip_defocus=None, disable=False, disable_keyboards=True):
        """
        defocus_all
        args: self - self object
            skip_defocus - optional argument to indicate a field to not defocus
            disable - optinal argument to indicator that fields should also be disabled
        purpose: remove focus to get rid of fantom teardrops on Android
        """
        Logger.info('text_input_util: defocus_all')
        for text_input in self.all_input_fields.values():
            if text_input != skip_defocus:
                text_input.focus = False
                if disable:
                    text_input.disabled = True
        if disable_keyboards:
            soft_keyboard.remove_soft_keyboard()
            hard_keyboard.unbind_keyboard()
        if hasattr(self, 'workout_selector_bubble'):
            self.remove_widget(self.workout_selector_bubble)

    def find_focused_field(self):
        """
        find_focused_field
        args: self - self object
        purpose: find focussed field
        returns: field that has focus
        """
        return_key = return_field = None
        for key, input_field in self.all_input_fields.items():
            if input_field.focused and input_field.parent:
                return_field = input_field
                return_key = key
                break
        return (return_key, return_field)

    def generic_toggle(self, button_id, label_id, on_icon, off_icon, label_on_text, label_off_text):
        """
        generic_toggle
        args: self - self object
            button_id - kivy id of button
            label_id - kivy id of label
            on_icon - icon indicating on state
            off_icon - icon indicating off state
            label_on_text - text indicating on state
            label_off_text - text indicating off state
        purpose: abstract out a button toggle action
        """
        if self.ids[button_id].icon == on_icon:
            self.ids[button_id].icon = off_icon
            self.ids[label_id].text = label_off_text
        else:
            self.ids[button_id].icon = on_icon
            self.ids[label_id].text = label_on_text

    def get_next_field(self, start_key):
        """
        get_next_field
        args: self - self object
            start_key - key to start field search from
        purpose: locate the next field to move to on a tab
        returns: tuple of key and field of next field
        """
        Logger.info(f'text_input_field: get_next_field {start_key}, fields: {self.all_input_fields}')
        found_key = False
        return_key = return_field = None
        for key, input_field in self.all_input_fields.items():
            if found_key and not input_field.disabled and input_field.parent:
                return_field = input_field
                return_key = key
                break
            if key == start_key:
                found_key = True
        if not return_key:
            for key, input_field in self.all_input_fields.items():
                if not input_field.disabled and input_field.parent:
                    return_field = input_field
                    return_key = key
                    break
        return (return_key, return_field)

    def init_set_fields(self, prefix_string, font_size, app=None):
        """
        init_set_fields
        args: self - self object
            prefix_string - string to use as an index prefix for mapping fields
            font_size - size of font to use in rendering
            app - optional app object
        purpose: initialize set fields for dynamic form control
        """
        app = app if app else App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        unpickleable[f'{prefix_string} left weight'] = (
            WorkoutTextField(font_size=font_size, hint_text='LEFT WGT',
                field_name=f'{prefix_string} left weight'.replace(' ', '_'), input_field_type='float',
                input_filter='float'))
        unpickleable[f'{prefix_string} left weight'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} left reps'] = (
            WorkoutTextField(font_size=font_size, hint_text='LEFT REPS',
                field_name=f'{prefix_string} left reps'.replace(' ', '_'), input_field_type='int',
                input_filter='int'))
        unpickleable[f'{prefix_string} left reps'].bind(focus=self.set_focus)
        if prefix_string != 'workout builder':
            unpickleable[f'{prefix_string} left time'] = (
                WorkoutTextField(font_size=font_size, hint_text='MIN:SEC',
                    field_name=f'{prefix_string} left time'.replace(' ', '_'), input_field_type='time',
                    text='00:00'))
            unpickleable[f'{prefix_string} left time'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} right weight'] = (
            WorkoutTextField(font_size=font_size, hint_text='RIGHT WGT',
                field_name=f'{prefix_string} right weight'.replace(' ', '_'), input_field_type='float',
                input_filter='float'))
        unpickleable[f'{prefix_string} right weight'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} right reps'] = (
            WorkoutTextField(font_size=font_size, hint_text='RIGHT REPS',
                field_name=f'{prefix_string} right reps'.replace(' ', '_'), input_field_type='int',
                input_filter='int'))
        unpickleable[f'{prefix_string} right reps'].bind(focus=self.set_focus)
        if prefix_string != 'workout builder':
            unpickleable[f'{prefix_string} right time'] = (
                WorkoutTextField(font_size=font_size, hint_text='MIN:SEC',
                    field_name=f'{prefix_string} right time'.replace(' ', '_'), input_field_type='time',
                    text='00:00'))
            unpickleable[f'{prefix_string} right time'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} weight'] = (
            WorkoutTextField(font_size=font_size, hint_text='WEIGHT',
                field_name=f'{prefix_string} weight'.replace(' ', '_'), input_field_type='float',
                input_filter='float'))
        unpickleable[f'{prefix_string} weight'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} reps'] = (
            WorkoutTextField(font_size=font_size, hint_text='REPS',
                field_name=f'{prefix_string} reps'.replace(' ', '_'), input_field_type='int',
                input_filter='int'))
        unpickleable[f'{prefix_string} reps'].bind(focus=self.set_focus)
        unpickleable[f'{prefix_string} time'] = (
            WorkoutTextField(font_size=font_size, hint_text='MIN:SEC',
                field_name=f'{prefix_string} time'.replace(' ', '_'), input_field_type='time', text='00:00'))
        unpickleable[f'{prefix_string} time'].bind(focus=self.set_focus)

    def key_press(self, _, keycode, app=None):
        """
        key_press
        args: self - self object
            - - for compatibility
            keycode - key value
            app - optional app object
        purpose: process key press
        """
        Logger.info(f'text_input_util: key_press keycode={keycode}')
        key, input_field = self.find_focused_field()
        if input_field:
            app = app if app else App.get_running_app()
            sound =  app.app_data_dict['unpickleable']['sound']
# Python 3.10 syntax commented out for future restore
#            match keycode:
#                case 'backspace':
#                    if input_field.input_field_type == 'time':
#                        input_field.do_cursor_movement('cursor_left')
#                    else:
#                        input_field.do_backspace()
#                case 'delete':
#                    input_field.do_cursor_movement('cursor_right')
#                    input_field.do_backspace()
#                case 'end':
#                    input_field.do_cursor_movement('cursor_end')
#                case 'enter' | 'tab':
#                    new_key, new_input_field = self.get_next_field(key)
#                    new_input_field.focus = True
#                    input_field.focus = False
#                    soft_keyboard.set_keyboard_layout(self, new_input_field.input_field_type, self.soft_key_press,
#                                                      app=app)
#                case 'home':
#                    input_field.do_cursor_movement('cursor_home')
#                case 'exit':
#                    self.defocus_all()
#                    soft_keyboard.remove_soft_keyboard()
#                    hard_keyboard.unbind_keyboard()
#                case 'left':
#                    input_field.do_cursor_movement('cursor_left')
#                case 'right':
#                    input_field.do_cursor_movement('cursor_right')
#                case 'spacebar':
#                    if input_field.input_field_type == 'text':
#                        input_field.insert_text(' ')
#                    else:
#                        sound.play_sound('beep.ogg')
#                case str() as s if len(s) == 1:
#                    if input_field.input_field_type == 'float' and keycode == '.' and '.' in input_field.text:
#                        sound.play_sound('beep.ogg')
#                    elif input_field.input_field_type == 'time':
#                        test_text = list(str(input_field.text))
#                        try:
#                            test_text[input_field.cursor_index()] = keycode
#                        except Exception as e:
#                            sound.play_sound('beep.ogg')
#                            return
#                        if re.match(r'(\d\d):([0-5]\d)', ''.join(test_text)):
#                            input_field.do_cursor_movement('cursor_right')
#                            input_field.do_backspace()
#                        else:
#                            sound.play_sound('beep.ogg')
#                            return
#                    input_field.insert_text(keycode)
#                case str() as s if s in soft_keyboard.layouts:
#                    soft_keyboard.set_keyboard_layout(self, keycode, self.soft_key_press, app=app)
# start old Python syntax
            if keycode == 'backspace':
                if input_field.input_field_type == 'time':
                    input_field.do_cursor_movement('cursor_left')
                else:
                    input_field.do_backspace()
            elif keycode == 'delete':
                input_field.do_cursor_movement('cursor_right')
                input_field.do_backspace()
            elif keycode == 'end':
                input_field.do_cursor_movement('cursor_end')
            elif keycode in ('enter', 'tab'):
                new_key, new_input_field = self.get_next_field(key)
                new_input_field.focus = True
                input_field.focus = False
                soft_keyboard.set_keyboard_layout(self, new_input_field.input_field_type, self.soft_key_press, app=app)
            elif keycode ==  'home':
                input_field.do_cursor_movement('cursor_home')
            elif keycode == 'exit':
                self.defocus_all()
                soft_keyboard.remove_soft_keyboard()
                hard_keyboard.unbind_keyboard()
            elif keycode == 'left':
                input_field.do_cursor_movement('cursor_left')
            elif keycode == 'right':
                input_field.do_cursor_movement('cursor_right')
            elif keycode == 'spacebar':
                if input_field.input_field_type == 'text':
                    input_field.insert_text(' ')
                else:
                    sound.play_sound('beep.ogg')
            elif len(keycode) == 1:
                if input_field.input_field_type == 'float' and keycode == '.' and '.' in input_field.text:
                    sound.play_sound('beep.ogg')
                elif input_field.input_field_type == 'time':
                    test_text = list(str(input_field.text))
                    try:
                        test_text[input_field.cursor_index()] = keycode
                    except Exception as e:
                        sound.play_sound('beep.ogg')
                        return
                    if re.match(r'(\d\d):([0-5]\d)', ''.join(test_text)):
                        input_field.do_cursor_movement('cursor_right')
                        input_field.do_backspace()
                    else:
                        sound.play_sound('beep.ogg')
                        return
                input_field.insert_text(keycode)
            elif keycode in soft_keyboard.layouts:
                soft_keyboard.set_keyboard_layout(self, keycode, self.soft_key_press, app=app)
# end old Python syntax

    def render_set_field(self, key, unpickleable):
        """
        render_set_field
        args: self - self object
            key - key of field to render
            unpickleable - dictionary of unpickleable objects
        purpose: render a set field setting focus order
        """
        self.ids['set_container_id'].add_widget(unpickleable[key])
        unpickleable[key].disabled = False
        self.focus_order.append(key)

    def render_set_form(self):
        """
        render_set_form
        args: self - self object
        purpose: generate the set input form based on selected set buttons
        """
        Logger.info('text_input_util: render_set_form')
        keys = ('left weight', 'left reps', 'right weight', 'right reps', 'left time', 'right time', 'time', 'reps',
                'weight')
        app = App.get_running_app()
        self.ids['set_container_id'].clear_widgets()
        unpickleable = app.app_data_dict['unpickleable']
        for key2 in [f'{self.prefix_string} {key1}' for key1 in keys]:
            if key2 in unpickleable:
                unpickleable[key2].disabled = True
        self.focus_order = []
        if self.ids['left_right_button_id'].icon == self.left_right_on_icon:
            self.render_set_field(f'{self.prefix_string} left weight', unpickleable)
            if self.ids['reps_timer_button_id'].icon == self.timed_off_icon:
                self.render_set_field(f'{self.prefix_string} left reps', unpickleable)
                self.render_set_field(f'{self.prefix_string} right weight', unpickleable)
                self.render_set_field(f'{self.prefix_string} right reps', unpickleable)
            else:
                if self.prefix_string != 'workout builder':
                    self.render_set_field(f'{self.prefix_string} left time', unpickleable)
                self.render_set_field(f'{self.prefix_string} right weight', unpickleable)
                if self.prefix_string == 'workout builder':
                    self.render_set_field(f'{self.prefix_string} time', unpickleable)
                else:
                    self.render_set_field(f'{self.prefix_string} right time', unpickleable)
        else:
            self.render_set_field(f'{self.prefix_string} weight', unpickleable)
            if self.ids['reps_timer_button_id'].icon == self.timed_off_icon:
                self.render_set_field(f'{self.prefix_string} reps', unpickleable)
            else:
                self.render_set_field(f'{self.prefix_string} time', unpickleable)
        self.defocus_all()

    def set_focus(self, input_field, *kwargs):
        """
        set_focus
        args: self - self object
            input_field - text input field object
            kwargs - unknown arguments
        purpose: set the ID of the field that was last in focus so focus can be restored
        returns: boolean indicator as to if over_press protection allowed execution
        """
        Logger.info('text_input_util: set_focus text_input: {} kwargs: {}'.format(input_field, kwargs))
        if over_press.protect(vibrate=True):
            self.defocus_all(skip_defocus=input_field)
            input_field.focus = True
            self.activate_keyboards(input_field)
            return True
        return False

    def soft_key_press(self, unused_keycode, keycode, *args):
        """
        soft_key_press
        args: self - self object
            unused_keycode - keyboard object
            keycode - key value
            args - remaining args from event
        purpose: process soft number pad's key press
        """
        Logger.info(f'text_input_util: soft_key_press {keycode}')
        app = App.get_running_app()
        if over_press.protect(app = app, vibrate=True):
            self.key_press(None, keycode, app=app)

    def summon_keyboard_press(self, *kwargs):
        """
        summon_keyboard_press
        args: self - self object
            kwargs - kivy arguments
        purpose: provide method to summon keyboard on keyboard button press
        """
        Logger.info('text_input_util: summon_keyboard_press')
        if over_press.protect(vibrate=True):
            found = False
            for text_input in self.all_input_fields.values():
                if text_input.focus:
                    Logger.info('text_input_util: found')
                    self.activate_keyboards(text_input)
                    found = True
                    break
            if not found:
                found2 = False
                for text_input in self.all_input_fields.values():
                    if not text_input.disabled:
                        Logger.info('text_input_util: found2')
                        text_input.focus = True
                        self.activate_keyboards(text_input)
                        found2 = True
                        break

    def to_min_sec(self, seconds):
        """
        to_min_sec
        args: self - self object
            seconds - seconds to convert to min and sec
        purpose: create string to represent time
        returns: 00:00 format string of time
        """
        if seconds:
            mins = seconds // 60
            secs = seconds % 60
        else:
            mins = secs = 0
        return '{:02d}:{:02d}'.format(mins, secs)

    def toggle_left_right(self): # called from kv file
        """
        toggle_left_right
        args: self - self object
        purpose: toggle between an exercise that has separate left or right sets and an exercise that combines both
        """
        Logger.info('text_input_util: toggle_left_right')
        if over_press.protect(vibrate=True):
            self.generic_toggle('left_right_button_id', 'left_right_label_id', self.left_right_on_icon,
                                self.left_right_off_icon, self.left_right_on_string, self.left_right_off_string)
            self.render_set_form()

    def toggle_pound_kilogram(self): # called from kv file
        """
        toggle_pound_kilogram
        args: self - self object
        purpose: toggle between pounds and kilograms weight
        """
        Logger.info('text_input_util: toggle_pound_kilogram')
        if over_press.protect(vibrate=True):
            self.generic_toggle('pound_kilogram_button_id', 'pound_kilogram_label_id', self.pound_icon,
                                self.kilogram_icon, 'pound', 'kilogram')

    def toggle_reps_timer(self):  # called from kv file
        """
        toggle_reps_timer
        args: self - self object
        purpose: toggle between repetition count or timed set
        """
        Logger.info('text_input_util: toggle_reps_timer')
        if over_press.protect(vibrate=True):
            self.generic_toggle('reps_timer_button_id', 'reps_timer_label_id', self.timed_on_icon,
                                self.timed_off_icon, self.timed_on_string, self.timed_off_string)
            self.render_set_form()
