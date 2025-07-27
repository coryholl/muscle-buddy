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
import time
from kivy.utils import escape_markup

def gen_set_base_string(exercise_count, set_count, workout, muscle_group, exercise):
    """
    gen_set_base_string
    args: exercise_count - count of exercise
        set_count - number of set
        workout - workout dictionary
        muscle_group - muscle group dictionary
        exercise - exercise dictionary
    purpose: generate set base string for display
    returns: set base display string
    """
    if workout['type'] == 'classic strength training':
        workout_set_string = '[b]{}.{}: [i]{}[/i][/b]\n[i]muscle group[/i]: [b]{}[/b]\n[i]exercise[/i]: [b]{}[/b]\n'.format(exercise_count, set_count, escape_markup(workout['name']), escape_markup(muscle_group['name']), escape_markup(exercise['name']))
    elif workout['type'] == 'timed, random, muscle confusion':
        workout_set_string = '[b]{}. [i]{}[/i][/b]\n[i]muscle group[/i]: [b]{}[/b]\n[i]exercise[/i]: [b]{}[/b]\n'.format(set_count, escape_markup(workout['name']), escape_markup(muscle_group['name']), escape_markup(exercise['name']))
    if exercise['target weight']:
        workout_set_string += '[i]weight[/i]: [b]{} {}[/b]\n'.format(exercise['target weight'], exercise['weight unit abbreviation'])
    return workout_set_string

def gen_spinner():
    """
    gen_spinner
    purpose: generate a simple text spinner
    returns: single char spinner string based on time
    """
    spinner = ('/','-','\\','|')
    return spinner[int(time.time() % 4)]