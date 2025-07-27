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
from kivy.app import App
from kivy.utils import get_hex_from_color
# local imports
import stateful_clock
import tabata_timer # needed by Kivy engine
from workout_trainer import WorkoutTrainer

class WorkoutTrainerTimedWorkoutWithTimedSetsAndAutoAdvance(WorkoutTrainer):
    """
    WorkoutTrainerTimedWorkoutWithTimedSetsAndAutoAdvance
    purpose: class for creating 8 minute abs style workouts
    """
    initializing = True

    def load_workout(self):
        """
        load_workout
        args: self - self object
        purpose: load workout
        """
        app = App.get_running_app()
        unpickleable = app.app_data_dict['unpickleable']
        properties = app.app_data_dict['global properties']
        workout = app.app_data_dict['workout dictionary'][properties['workout index']]
        properties['muscle group name'] = workout['muscle group'][0]['name']
        app.tabata_workout_name = '[b]{}[/b]'.format(workout['name'])
        exercise_name = workout['active set'][0]['name']
        app.tabata_exercise_name = f'[b]{exercise_name}[/b]'
        app.tabata_workout_timer = \
            self.ids['workout_timer'].format_time(workout['time length'], get_hex_from_color((1, 1, 1)))
        self.ids['workout_timer'].state = 'not started'
        properties['tabata workout index'] = properties['workout index']
        workout['set index'] = 0
        self.next_workout_image(exercise_name)
        set_recorder = unpickleable['set recorder']
        set_recorder.ids['set_recorder_form_id'].disabled = False
        set_recorder.update_set_recorder()
        set_recorder.update_form()
        if self.initializing:
            self.ids['workout_timer'].restore_state()
            self.initializing = False
        else:
            self.ids['workout_timer'].full_reset()
            stateful_clock.unschedule_all()
            unpickleable['sound'].stop_all_sounds()
            unpickleable['stopwatch'].fix_tabata_switch()
            unpickleable['generic timer'].fix_tabata_switch()

    def next_workout_set(self, exercise_name):
        """
        next_workout_set
        args: self - self object
            exercise_name - name of exercise
        purpose: update screen for next set
        """
        app = App.get_running_app()
        app.tabata_exercise_name = f'[b]{exercise_name}[/b]'
        self.next_workout_image(exercise_name)
