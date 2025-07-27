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
import copy
import os
from kivy.app import App
from kivy.core.image import Image as CoreImage
from kivy.uix.image import AsyncImage, Image
# local imports
import database_util
import workout_trainer_util

class DataDict:
    """
    datadict
    purpose: data dictionary object object containing data access logic of application
    """

    def build_classic_sets(self, workout):
        """
        build_classic_sets
        args: self - self object
            workouts - workout dictionary
        purpose: build out working sets for classic style trainers
        """
        workout['carousel widgets'] = []
        workout_sets = []
        for group_sort_index, muscle_group in enumerate(workout['muscle group']):
            for exercise_count, exercise in enumerate(muscle_group['exercises']):
                set_count = exercise['set count'] if exercise['set count'] else 1
                for set_number in range(set_count):
                    exercise_set = copy.deepcopy(exercise)
                    exercise_set['group sort index'] = group_sort_index
                    exercise_set['recorded'] = False
                    exercise_set['exercise count'] = exercise_count + 1
                    exercise_set['set number'] = set_number + 1
                    carousel_label_text = '[b]{}.[/b]{}[i]{}'.format(
                        exercise_set['group sort index'] + 1, workout_trainer_util.gen_set_base_string(
                                exercise_set['exercise count'], exercise_set['set number'],
                                workout, muscle_group, exercise), self.gen_reps_string(exercise))
                    kv = """
SetLabel:
    halign: 'center'
    valign: 'bottom'
    markup: True
    text: '{}'
""".format(carousel_label_text.replace('\n', '\\n').replace('\'', "\\'"))
                    exercise_set['kv set widget'] = kv
                    workout_sets.append(exercise_set)
        sort1 = sorted(workout_sets, key=lambda x: x['exercise count'])
        sort2 = sorted(sort1, key=lambda x: x['set number'])
        sort3 = sorted(sort2, key=lambda x: x['group sort index'])
        workout['active set'] = sort3
        workout['set widgets'] = [row['kv set widget'] for row in workout['active set']]

    def build_tabata_sets(self, workout):
        """
        build_tabata_sets
        args: self - self object
            workout - workout dictionary
        purpose: build out working sets for 8 min abs style trainers
        """
        tabata_seconds = 0
        for muscle_group in workout['muscle group']:
            for exercise in muscle_group['exercises']:
                tabata_seconds += exercise['set timer']
                exercise_set = copy.deepcopy(exercise)
                exercise_set['recorded'] = False
                workout['active set'].append(exercise_set)
        workout['time length'] = tabata_seconds
        for exercise in workout['active set']:
            exercise['end time'] = tabata_seconds
            tabata_seconds -= exercise['set timer']

    def build_trmc_sets(self, workout, global_properties):
        """
        build_trmc_sets
        args: self - self object
            workout - workout dictionary
            global_properties - application properties dictionary
        purpose: add session set list to workout
        """
        workout['active set'] = global_properties['timed random muscle confusion sets']
        workout['carousel widgets'] = global_properties['timed random muscle confusion carousel widgets']
        workout['set widgets'] = global_properties['timed random muscle confusion set widgets']

    def build_work_sets(self, workout_dict, global_properties):
        """
        build_work_sets
        args: self - self object
            workout_dict - workout dictionary list
            global_properties - app global properties dictionary
        purpose: build out working sets for trainers and set recorder to use in exercise session
        """
        for workout in workout_dict:
            if workout['type'] == 'classic strength training':
                self.build_classic_sets(workout)
            elif workout['type'] == 'timed, random, muscle confusion':
                self.build_trmc_sets(workout, global_properties)
            elif workout['type'] == 'timed workout with timed sets and auto advance':
                self.build_tabata_sets(workout)

    def build_workout_dictionary(self, raw_dict):
        """
        build_workout_dictionary
        args: self - self object
            raw_dict - raw dictionary of query of workout dict view
        purpose: generate workout data dictionary
        returns: populated workout dictionary
        """
        workouts = []
        for row in raw_dict:
            if not any(row['workout_program_name'] == workout['name'] for workout in workouts):
                workouts.append(
                    {
                        'active set': [],
                        'alarm sound file': row['workout_program_alarm_sound_file'],
                        'finish image file': row['workout_type_finish_image_file_name'],
                        'image file': row['workout_type_image_file_name'],
                        'muscle group': [self.gen_muscle_group(row)],
                        'name': row['workout_program_name'],
                        'set carousel index': 0,
                        'set recorder index': 0,
                        'set widgets': [],
                        'time length': row['workout_program_time_length'],
                        'type': row['workout_type_type'],
                        'type name': row['workout_type_name']
                    })
            elif not any(row['exercise_set_group_name'] == muscle_group['exercise muscle group key']
                         for muscle_group in workouts[-1]['muscle group']):
                workouts[-1]['muscle group'].append(self.gen_muscle_group(row))
            if not any(row['muscle_images_file_name'] == image['file name']
                         for image in workouts[-1]['muscle group'][-1]['images']):
                workouts[-1]['muscle group'][-1]['images'].append({'file name': row['muscle_images_file_name']})
            if not any(row['exercise_set_exercise_name'] == exercise['name']
                         for exercise in workouts[-1]['muscle group'][-1]['exercises']):
                workouts[-1]['muscle group'][-1]['exercises'].append(self.gen_exercise_set(row))
        self.get_image_dict = {}
        return workouts

    def gen_exercise_set(self, row):
        """
        gen_exercise_set
        args: self - self object
            row - dict containing workout dict row
        purpose: generate the dictionary of a workout's set
        returns: dictionary of a workout set
        """
        return {
            'alarm sound file': row['exercise_set_alarm_sound_file'],
            'built view': None,
            'images': [{}],
            'left reps': row['exercise_set_left_reps'],
            'left weight': row['exercise_set_left_weight'],
            'name': row['exercise_set_exercise_name'],
            'right reps': row['exercise_set_right_reps'],
            'right weight': row['exercise_set_right_weight'],
            'set count': row['exercise_set_set_count'],
            'set timer': row['exercise_set_set_timer'],
            'sort index': row['exercise_set_sort_index'],
            'target reps': row['exercise_set_target_reps'],
            'target weight': row['exercise_set_target_weight'],
            'weight unit abbreviation': row['weight_units_name_abbreviation'],
            'weight unit kilogram conversion': row['weight_units_kilogram_conversion'],
            'weight unit name': row['weight_units_name']
        }

    def gen_reps_string(self, exercise):
        """
        gen_reps_string
        args: self - self object
            exercise - dictionary of exercise set
        purpose: generate a string for showing sets
        returns: format string for reps or time limit of work set
        """
        if exercise['target reps']:
            return f'[i]reps[/i]: [b]{exercise["target reps"]}[/b]'
        elif exercise['set timer']:
            minute = int(exercise['set timer']) // 60
            second = int(exercise['set timer']) % 60
            return f'[i]time[/i]: [b]{minute:02d}:{second:02d}[/b]'
        elif exercise['left reps'] or exercise['right reps']:
            return f'[i]reps[/i]: [b]{exercise["left reps"]}/{exercise["right reps"]}[/b]'
        else:
            return ''

    def get_global_properties_dict(self, workout_dict):
        """
        get_global_properties_dict
        args: self - self object
            workout_dict - workout data dictionary
        purpose: setup the global properties dictionary
        returns: dictionary containing global properties
        """
        return {
            'classic exercise index': 0,
            'classic exercise name': '',
            'classic workout index': None,
            'clocks': {},
            'end time': 0,
            'exercise': None,
            'generic timer': '',
            'generic timer end time': 0,
            'generic timer time left': 0,
            'generic timer time length': 60,
            'generic timer state': 'not started',
            'get workout time event': None,
            'last button press time': 0,
            'muscle group name': None,
            'navigation tab': 'Select Workout',
            'navigation screen': 0,
            'pause time': 0,
            'rest end time': 0,
            'rest time left': 0,
            'rest time length': 60,
            'rest timer state': 'not started',
            'rotate exercise image event': None,
            'selector workout index': 0,
            'set count': 0,
            'set end time': 0,
            'set carousel index': 0,
            'set recorder focused widget': None,
            'set recorder index': None,
            'set recorder states': {},
            'set time left': 0,
            'set timer state': 'not started',
            'tabata end time': 0,
            'tabata exercises': [],
            'tabata exercise index': 0,
            'tabata set timer': '',
            'tabata time left': 0,
            'tabata timer': '',
            'tabata timer state': 'not started',
            'tabata workout index': None,
            'time left': 0,
            'timed random muscle confusion carousel widgets': [],
            'timed random muscle confusion exercise name': '',
            'timed random muscle confusion sets': [],
            'timed random muscle confusion set widgets': [],
            'timed random muscle confusion workout index': None,
            'timer started': False,
            'trainer index': 0,
            'trainer image index': 0,
            'widget registry': {},
            'workout end time': 0,
            'workout index': 0,
            'workout rest timer': '',
            'workout set': '',
            'workout set timer': '',
            'workout set widgets': [],
            'workout time left': 0,
            'workout timer': '',
            'workout timer state': 'not started'
        }

    def get_image_overlays(self, db):
        """
        get_image_overlays
        args: self - self object
            db - open database object
        purpose: build dictionary of image overlays for creating muscle images:
        """
        raw_overlays = db.get_exercise_muscle_image_overlays()
        overlay_dict = {}
        for overlay in raw_overlays:
            exercise_name = overlay['exercise_muscles_exercise_name']
            if exercise_name not in overlay_dict:
                overlay_dict[exercise_name] = {}
            orientation = overlay['muscle_images_orientation']
            if orientation not in overlay_dict[exercise_name]:
                overlay_dict[exercise_name][orientation] = {}
            focus = overlay['muscle_images_focus']
            if focus not in overlay_dict[exercise_name][orientation]:
                overlay_dict[exercise_name][orientation][focus] = []
            overlay_dict[exercise_name][orientation][focus].append(overlay['muscle_images_file_name'])
        raw_anatomy = db.get_body_muscle_image_template()
        overlay_dict['Master'] = {}
        for anatomy in raw_anatomy:
            overlay_dict['Master'][anatomy['muscle_images_orientation']] = anatomy['muscle_images_file_name']
        return overlay_dict

    def gen_muscle_group(self, row):
        """
        gen_muscle_group
        args: self - self object
            row - dict containing workout dict row
        purpose: generate dictionary of a workout's muscle group  
        returns: dictionary of a workout muscle group
        """
        return {
            'exercise muscle group key': row['exercise_set_group_name'],
            'exercises': [self.gen_exercise_set(row)],
            'name': row['exercise_set_muscle_group_name'],
            'images': [
                {
                    'file name': row['muscle_images_file_name']
                }
            ]
        }

    def get_muscle_selector_image_maps(self, db):
        """
        get_muscle_selector_overlays
        args: self - self object
            db - open database object
        purpose: build dictionary of image maps for use in muscle selector
        """
        image_maps = db.get_muscle_map_images()
        muscle_maps = {}
        for image_map in image_maps:
            muscle_group_name = image_map['muscle_images_muscle_group_name']
            if muscle_group_name not in muscle_maps:
                muscle_obj = muscle_maps[muscle_group_name] = {}
                muscle_obj['exercise creator image state'] = muscle_obj['instinctual trainer image state'] = \
                    muscle_obj['workout builder image state'] = 'not selected'
            else:
                muscle_obj = muscle_maps[muscle_group_name]
            if image_map['muscle_images_orientation'] not in muscle_obj:
                muscle_obj[image_map['muscle_images_orientation']] = {}
            muscle_obj[image_map['muscle_images_orientation']][image_map['muscle_images_focus']] = {
                    'core image': CoreImage(os.path.join('images', image_map['muscle_images_file_name']),
                        keep_data=True),
                    'image atlas': image_map['muscle_images_atlas'],
                    'image file': image_map['muscle_images_file_name']
                }
        return muscle_maps

    def get_weight_unit_dict(self, db):
        """
        get_weight_unit_dict
        args: self - self object
            db - database object
        purpose: create weight cross reference dictioanry
        returns: dictionary containing weight unit translation data
        """
        weight_units = db.get_weight_units()
        weight = {}
        for weight_unit in weight_units:
            weight[weight_unit['weight_units_name']] = {
                'abbreviation': weight_unit['weight_units_name_abbreviation'],
                'kilogram conversion': weight_unit['weight_units_kilogram_conversion'],
                'name': weight_unit['weight_units_name']
            }
        return weight

    def get_workout_dict(self, db):
        """
        get_workout_dict
        args: self - self object
            db - database object
        purpose: create workout dictionary from database
        returns: workout dictionary
        """
        raw_dict = db.get_data_dict_database()
        workout_dict = self.build_workout_dictionary(raw_dict)
        global_properties = self.get_global_properties_dict(workout_dict)
        self.build_work_sets(workout_dict, global_properties)
        data_dict = {
            'config': database_util.get_config(db.app_db),
            'global properties': global_properties,
            'images': self.get_image_dict,
            'weight units': self.get_weight_unit_dict(db),
            'workout dictionary': workout_dict
        }
        return data_dict

    def load_finish_images(self, data_dict):
        """
        load_finish_images
        args: self - self object
            workout_dict - data dictionary of workouts
        purpose: load finish reward images to cache for performance purposes
        """
        image_objs = {}
        for workout in data_dict['workout dictionary']:
            if workout['finish image file'] and workout['finish image file'] not in image_objs:
                image_objs[workout['finish image file']] = (Image(source=os.path.join('images',
                    workout['finish image file']), mipmap=True, fit_mode='contain', anim_delay=-1) if
                    workout['finish image file'].lower().endswith('.gif') else AsyncImage(source=os.path.join('images',
                    workout['finish image file']), mipmap=True, fit_mode='contain'))
        data_dict['unpickleable']['finish image widget'] = image_objs

    def none_to_val(self, val):
        """
        none_str
        args: self - self object
            val - value to check
        purpose: convert Nones to empty strings
        returns: value if not None else empty string
        """
        return '' if val is None else str(val)

    def update_app_workout_dictionary(self):
        """
        update_app_workout_dictionary
        args: self - self object
        purpose: updated workout data dictionary after workout change in workout builder
        """
        app = App.get_running_app()
        db = app.app_data_dict['unpickleable']['database']
        raw_dict = db.get_data_dict_database()
        workout_dict = self.build_workout_dictionary(raw_dict)
        global_properties = app.app_data_dict['global properties']
        self.build_work_sets(workout_dict, global_properties)
        app.app_data_dict['workout dictionary'] = workout_dict
