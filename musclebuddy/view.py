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
# along with Muscle Buddy.  If not, see <https://www.gnu.org/licenses/>.`
import datetime
import os
import pickle
import platform as pplatform
import kivy
import signal
import time
from kivy.base import stopTouchApp
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.loader import Loader
from kivy.logger import Logger
from kivy.properties import BooleanProperty, ColorProperty, StringProperty
from kivy.utils import platform
from kivymd.app import MDApp
# local imports
import about
import android_util
import config
import exercise_creator
import linux_mobile_util
import over_press
#import pantheon_util
import quit_reset
import set_recorder
import soft_keyboard
import sound
import timers
import vibrator
import workout_builder
import workout_reader
import workout_selector
import workout_trainer_classic_strength_training
import workout_trainer_instinctual_training
import workout_trainer_timed_random_muscle_confusion
import workout_trainer_timed_workout_with_timed_sets_and_auto_advance
from date_picker import DatePicker
from confirmation_popup_window import ConfirmationPopupWindow
kivy.require('2.2.0')

class MuscleBuddyApp(MDApp):
    """ 
    MainApp
    purpose: create class for main Kivy app object
    """
    app_data_dict = {}
    classic_exercise_name = StringProperty('')
    generic_stopwatch = StringProperty('0:00:00.0')
    generic_timer = StringProperty('00:01:00')
    load_disable = BooleanProperty(True)
    tabata_bg_color = ColorProperty((0, 0, 0, 1))
    tabata_exercise_name = StringProperty('')
    tabata_set_timer = StringProperty('0:00.0')
    tabata_workout_timer = StringProperty('00:00')
    tabata_workout_name = StringProperty('')
    timed_random_muscle_confusion_exercise_name = StringProperty('')
    timers_state = StringProperty('')
    title = StringProperty('Muscle Buddy')
    workout_rest_timer = StringProperty()
    workout_timer = StringProperty()
    workout_set_timer = StringProperty()
    trainer_state = StringProperty('')
    navigation_map = {
        'About': {
            'title': 'About',
            'screen': None
        },
        'Config': {
            'title': 'Configure Features',
            'screen': None
        },
        'Exercise Creator': {
            'title': 'Create or Delete an Exercise',
            'screen': None
        },
        'Quit/Reset': {
            'title': 'Quit or Reset',
            'screen': None
        },
        'Record Set': {
            'title': 'Record Workout Sets',
            'screen': None
        },
        'Select Workout': {
            'title': 'Select Trainer and Workout',
            'screen': None
         },
        'Timers': {
            'title': 'A Timer and a Stopwatch',
            'screen': None
        },
        'Workout Builder': {
            'title': 'Build, Edit, or Delete a Workout',
            'screen': None
        },
        'Workout History': {
            'title': 'View Past Workouts and Sets',
            'screen': None
        },
        'Workout Trainer': {
            'title': 'Workout',
            'screen': None
        }
    }

    def __init__(self, app_data_dict):
        """
        __init__
        args: self - self object
        db - open database model object
        app_data_dict - application data dictionary
        purpose: initialize MyApp object
        """
        Logger.info('Application: __init__ called')
        self.app_data_dict = app_data_dict
        super(MuscleBuddyApp, self).__init__()

    def __exit__(self):
        """
        __exit__
        args:  self - self object
        purpose: cleanup MyApp for exit
        """
        Logger.info('Application: Application __exit__ called in MainApp')

    def build(self): # called from Kivy engine
        """
        build
        args: self - self object
        purpose: Kivy build method.  Builds and initializes the Kivy app.  Required for Kivy to run.
        """
        self.icon = Loader.loading_image = 'muscle_buddy.png'
        Logger.info('Application: build called')
        if platform == 'win':
            Window.fullscreen = True
        else:
            linux_mobile_util.set_mobile_fullscreen()
        if platform == 'android':
            Window.bind(on_keyboard=android_util.prevent_android_crash)
        self.shutdown_button_pressed_false = False
        self.reset_button_pressed_flag = False
        Loader.loading_image = 'muscle_buddy.png'
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_hue = "200"
        self.icon = 'muscle_buddy.png'
        if self.app_data_dict['workout dictionary'] and self.app_data_dict['workout dictionary'][0]['time length']:
            time_length = self.app_data_dict['workout dictionary'][0]['time length']
            hour = int(time_length // 3600)
            minute = int((time_length % 3600) // 60)
            second = int(time_length % 60)
            if 'workout time' in self.app_data_dict['global properties']:
                self.workout_timer = self.app_data_dict['global properties']['workout time']
            else:
                self.app_data_dict['global properties']['workout time'] = self.workout_timer = \
                    f'{hour:02d}:{minute:02d}:{second:02d}'
        if os.path.exists('no_load_sleep'):
            self.load_slow_resources(None)
        else:
            match platform:
                case 'android':
                    sleep_time = 4
                case 'linux':
                    machine = pplatform.machine()
                    sleep_time = 7 if machine == 'aarch64' else 2
                case _:
                    sleep_time = 3
            Clock.schedule_once(self.load_slow_resources, sleep_time)

    def fast_nav(self, nav_item_id):
        """
        fast_nav
        args: self - self object
            nav_item_id - kivy id of nav drawer item to activate for nav action
        purpose: fast nav to a screen attached to a nav drawer item
        """
        if over_press.protect(vibrate=True):
            self.root.ids['nav_menu'].reset_active_color(self.root.ids[nav_item_id])

    def load_slow_resources(self, dt):
        """
        load_slow_resources
        args: self - self object
            dt - time since last callback call
        purpose: load slow loading resources
        """
        Logger.info('view: load_slow_resource')
        unpickleable = self.app_data_dict['unpickleable']
        sound_start_time = time.time()
        unpickleable['sound'] = sound.Sound(unpickleable['database'])
        sound_load_time = time.time() - sound_start_time
        Logger.info(f'Application: Sound load time {sound_load_time}')
        properties = self.app_data_dict['global properties']
        unpickleable['dictionary manager'].load_finish_images(self.app_data_dict)
        self.classic_exercise_name = properties['classic exercise name']
        self.timed_random_muscle_confusion_exercise_name = properties['timed random muscle confusion exercise name']
        self.workout_timer = properties['workout timer']
        self.workout_set_timer = properties['workout set timer']
        soft_keyboard.init_keyboards()
        trainers = unpickleable['trainer'] = {}
        trainers['classic strength training'] = \
            workout_trainer_classic_strength_training.WorkoutTrainerClassicStrengthTraining(self.app_data_dict)
        trainers['instinctual training'] = \
            workout_trainer_instinctual_training.WorkoutTrainerInstinctualTraining(self.app_data_dict)
        trainers['timed, random, muscle confusion'] = \
            workout_trainer_timed_random_muscle_confusion.WorkoutTrainerTimedRandomMuscleConfusion(self.app_data_dict)
        trainers['timed workout with timed sets and auto advance'] = \
            workout_trainer_timed_workout_with_timed_sets_and_auto_advance.WorkoutTrainerTimedWorkoutWithTimedSetsAndAutoAdvance()
        unpickleable['about'] = self.navigation_map['About']['screen'] = about.About()
        unpickleable['config'] = self.navigation_map['Config']['screen'] = config.Config()
        unpickleable['vibrator'] = vibrator.Vibrator()
        unpickleable['exercise creator'] = self.navigation_map['Exercise Creator']['screen'] = \
            exercise_creator.ExerciseCreator(self.app_data_dict)
        unpickleable['quit/reset'] = self.navigation_map['Quit/Reset']['screen'] = quit_reset.QuitReset()
        unpickleable['set recorder'] = self.navigation_map['Record Set']['screen'] = set_recorder.SetRecorder()
        unpickleable['timers'] = self.navigation_map['Timers']['screen'] = timers.Timers()
        unpickleable['workout builder'] = self.navigation_map['Workout Builder']['screen'] = \
            workout_builder.WorkoutBuilder()
        unpickleable['workout reader'] = self.navigation_map['Workout History']['screen'] = \
            workout_reader.WorkoutReader()
        unpickleable['workout selector'] = self.navigation_map['Select Workout']['screen'] = \
            workout_selector.WorkoutSelector()
        unpickleable['confirmation popup'] = ConfirmationPopupWindow()
        unpickleable['date dialog'] = DatePicker(firstweekday=6, max_year=datetime.date.today().year+1)
        unpickleable['workout selector'].load_workout_selector()
        trainer = trainers[self.app_data_dict['workout dictionary'][properties['workout index']]['type']]
        trainer.load_workout()
        pickle_file = os.path.join('database', 'pause.pickle')
        if os.path.exists(pickle_file):
            os.remove(pickle_file)
        linux_mobile_util.disable_squeekboard()
        self.root.ids['screen_container'].clear_widgets()
        self.root.ids['screen_container'].add_widget(self.navigation_map['Select Workout']['screen'])
        self.title = self.navigation_map['Select Workout']['title']
        self.load_disable = False
        Logger.info('Application: Application load time {}'.format(time.time() - properties['application start time']))
        if platform != 'win':
            signal.signal(signal.SIGUSR1, self.process_signal)

    def on_memorywarning(self):
        """
        on_memorywarning
        args: self - self object
        purpose: do something if memory warning occurs
        """
        Logger.info('Application: on_memorywarning called!')

    def on_pause(self):
        """
        on_pause
        args: self - self object
        purpose: dump state when application is paused on Android
        returns: True
        """
        Logger.info('Application: Application paused')
        if not self.load_disable:
            self.app_data_dict['pickle time'] = time.time()
            pickle_file = os.path.join('database', 'pause.pickle')
            with open(pickle_file, 'wb') as f:
                unpickleable = self.app_data_dict['unpickleable']
                self.app_data_dict['unpickleable'] = None
                pickle.dump(self.app_data_dict, f)
                self.app_data_dict['unpickleable'] = unpickleable
        return True

    def on_resume(self): # called from Kivy engine on Android
        """
        on_resume
        args: self - self object
        purpose: restore state after an Android pause
        """
        Logger.info('Application: Application resumed')
        pickle_file = os.path.join('database', 'pause.pickle')
        if os.path.exists(pickle_file):
            os.remove(pickle_file)

    def on_start(self): # called from Kivy engine
        """
        on_start
        args: self - self object
        purpose: perform actions on application start
        """
        Logger.info('Application: on_start called')

    def on_stop(self, *kwargs):
        """
        on_stop
        args: self - self object
            *kwargs - optional arguments so it can be called from Clock
        purpose: shutdown app
        """
        Logger.info('Application: Application stopped')
        pickle_file = os.path.join('database', 'pause.pickle')
        if os.path.exists(pickle_file):
            os.remove(pickle_file)
        linux_mobile_util.enable_squeekboard()
        stopTouchApp()

    def open_settings(self, *kwargs):
        """
        open_settings
        args: self - self object
            kwargs - mystery args
        purpose: override the open_settings method to disable the F1 key
        """
        pass

    def process_signal(self, signum, frame):
        """
        process_signal
        args: self - self object
            signum - signal number
            frame - stack frame?
        purpose: use signal to simulate Android pause behavior on Linux
        """
        Logger.info('Application: signal processed')
        self.on_pause()

    def reload_workout_widgets(self, *kwargs):
        """
        reload_workout_widgets
        args: self - self object
            kwargs - unused args coming from Kivy framework
        purpose: reload widgets needed to make workout changes from workout builder take effect
        """
        unpickleable = self.app_data_dict['unpickleable']
        unpickleable['dictionary manager'].update_app_workout_dictionary()
        unpickleable['sound'].update_sound_dict()
        unpickleable['dictionary manager'].load_finish_images(self.app_data_dict)
        trainers = unpickleable['trainer']
        trainers['classic strength training'] = \
            workout_trainer_classic_strength_training.WorkoutTrainerClassicStrengthTraining(self.app_data_dict)
        trainers['timed, random, muscle confusion'] = \
            workout_trainer_timed_random_muscle_confusion.WorkoutTrainerTimedRandomMuscleConfusion(self.app_data_dict)
        trainers['timed workout with timed sets and auto advance'] = \
            workout_trainer_timed_workout_with_timed_sets_and_auto_advance.WorkoutTrainerTimedWorkoutWithTimedSetsAndAutoAdvance()
        unpickleable['workout selector'] = self.navigation_map['Select Workout']['screen'] = \
            workout_selector.WorkoutSelector()
        unpickleable['workout selector'].load_workout_selector()
        self.app_data_dict['global properties']['workout index'] = 0
        trainers[self.app_data_dict['workout dictionary'][0]['type']].load_workout()
        unpickleable['confirmation popup'].dismiss()

    def reset(self, *kwargs):
        """
        reset
        args: self - self object
            kwargs - optional arguments so it can be called form Clock
        purpose: restart application with a fresh state
        """
        Logger.info('Application: Application reset')
        pickle_file = os.path.join('database', 'pause.pickle')
        if os.path.exists(pickle_file):
            os.remove(pickle_file)
        if platform == 'android':
            android_util.reboot_android()
        else:
            self.app_data_dict['reset'] = True
            for key, scheduled_process in self.app_data_dict['unpickleable']['clock processes'].items():
                Clock.unschedule(scheduled_process)
            self.root.ids['screen_container'].clear_widgets()
            stopTouchApp()
