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
import sqlite3
import uuid
from kivy.logger import Logger
# local imports
import database_util

class Database:
    """
    database
    purpose: database object containing model of application
    """
    app_db = None
    workout_db = None
    workout_uuid = None

    def __init__(self):
        """
        __init__
        args: self - self object
        purpose: initialize database object
        """
        if not os.path.exists('database'):
            os.makedirs('database')
        app_db_file = os.path.join('database', 'app.sqlite3')
        self.app_db = sqlite3.connect(app_db_file) if os.path.exists(app_db_file) else \
            self.create_app_database(app_db_file)
        workout_db_file = os.path.join('database', 'workout.sqlite3')
        self.workout_db = sqlite3.connect(workout_db_file) if os.path.exists(workout_db_file) else \
            self.create_workout_database(workout_db_file)
        self.workout_uuid = str(uuid.uuid1())
    
    def __exit__(self):
        """
        __exit__
        args: self - self object
        purpose: close database upon application exit
        """
        self.app_db.commit()
        self.app_db.close()
        self.workout_db.commit()
        self.workout_db.close()

    def create_app_database(self, database_file_name):
        """
        create_app_database
        args: self - self object
            database_file_name - database file name
        purpose: create an fresh Muscle Buddy app database
        returns: open sqlite3 database object for the app database
        """
        conn = sqlite3.connect(database_file_name)
        curs = conn.cursor()
        database_util.create_config_table(curs)
        self.create_exercise_muscles_table(curs)
        self.create_exercise_set_table(curs)
        self.create_exercise_table(curs)
        self.create_muscle_images_table(curs)
        self.create_weight_units_table(curs)
        self.create_workout_program_table(curs)
        self.create_workout_type_table(curs)
        self.create_sound_files_view(curs)
        self.create_workout_data_dictionary_view(curs)
        conn.commit()
        curs.close()
        return conn

    def create_exercise_muscles_table(self, curs):
        """
        create_exercise_muscles_table
        args: self - self object
            curs - cursor of app database
        purpose: create exercise_muscles table from schema
        """
        sql = """
            CREATE TABLE "exercise_muscles" (
	            "exercise_muscles_exercise_name"	    TEXT NOT NULL,
	            "exercise_muscles_muscle_group_name"	TEXT NOT NULL,
	            "exercise_muscles_muscle_focus"	        TEXT NOT NULL,
	            "exercise_muscles_id"	                INTEGER,
	            PRIMARY KEY("exercise_muscles_id"       AUTOINCREMENT)
            );"""
        curs.execute(sql)
        sql = """
            INSERT INTO exercise_muscles (
                exercise_muscles_exercise_name, 
                exercise_muscles_muscle_group_name, 
                exercise_muscles_muscle_focus)
            VALUES('rest', 'Rest', 'rest')
        """
        curs.execute(sql)

    def create_exercise_set_table(self, curs):
        """
        create_exercise_set_table
        args: self - self object
            curs - cursor of app database
        purpose: create exercise_set table from schema
        """
        sql = """
            CREATE TABLE "exercise_set" (
	            "exercise_set_workout_program_name"	    TEXT NOT NULL,
	            "exercise_set_workout_program_type"	    TEXT NOT NULL,
	            "exercise_set_muscle_group_name"	    TEXT NOT NULL,
	            "exercise_set_exercise_name"	        TEXT NOT NULL,
	            "exercise_set_group_name"	            TEXT,
	            "exercise_set_target_weight"	        REAL,
	            "exercise_set_weight_units_name"	    TEXT,
	            "exercise_set_body_weight_indicator"	INTEGER,
	            "exercise_set_target_reps"	            INTEGER,
	            "exercise_set_set_timer"	            INTEGER,
	            "exercise_set_alarm_sound_file"	        TEXT,
	            "exercise_set_left_weight"	            REAL,
	            "exercise_set_right_weight"	            REAL,
	            "exercise_set_left_reps"	            INTEGER,
	            "exercise_set_right_reps"	            INTEGER,
	            "exercise_set_set_count"	            INTEGER,
	            "exercise_set_sort_index"	            INTEGER,
	            "exercise_set_id"	                    INTEGER NOT NULL UNIQUE,
	            PRIMARY KEY("exercise_set_id" AUTOINCREMENT)
            );"""
        curs.execute(sql)
        sql = """
            INSERT INTO exercise_set (
                exercise_set_workout_program_name, 
                exercise_set_workout_program_type, 
                exercise_set_muscle_group_name, 
                exercise_set_exercise_name)
            VALUES ('You know what you want to do.  Just do it.', 'instinctual training', '', 'rest')
        """
        curs.execute(sql)

    def create_exercise_table(self, curs):
        """
        create_exercise_table
        args: self - self object
            curs - cursor of app database
        purpose: create exercise table from schema
        """
        sql = """
            CREATE TABLE "exercise" (
	        "exercise_name"	TEXT NOT NULL UNIQUE,
	        "exercise_id"	INTEGER NOT NULL UNIQUE,
	        PRIMARY KEY("exercise_id" AUTOINCREMENT)
            );"""
        curs.execute(sql)

    def create_muscle_images_table(self, curs):
        """
        create_muscle_images_table
        args: self - self object
            curs - cursor of app database
        purpose: create muscle_images table from schema
        """
        sql = """
            CREATE TABLE "muscle_images" (
	            "muscle_images_muscle_group_name"	TEXT NOT NULL,
	            "muscle_images_file_name"	        TEXT NOT NULL,
	            "muscle_images_orientation"	        TEXT,
	            "muscle_images_focus"	            INTEGER,
	            "muscle_images_atlas"	            TEXT,
	            "muscle_images_id"	                INTEGER NOT NULL UNIQUE,
	            PRIMARY KEY("muscle_images_id" AUTOINCREMENT)
            );"""
        curs.execute(sql)
        sql = """
            INSERT INTO muscle_images (
                muscle_images_muscle_group_name, 
                muscle_images_file_name,
                muscle_images_orientation,
                muscle_images_focus) 
            VALUES 
                ('Abdominals', 'muscular-anatomy-front.primary-abs.png', 'front', 'primary'),
                ('Abdominals', 'muscular-anatomy-front.secondary-abs.png', 'front', 'secondary'),
                ('Biceps', 'muscular-anatomy-front.primary-biceps.png', 'front', 'primary'),
                ('Biceps', 'muscular-anatomy-front.secondary-biceps.png', 'front', 'secondary'),
                ('Calves', 'muscular-anatomy-back.primary-calves.png', 'back', 'primary'),
                ('Calves', 'muscular-anatomy-front.primary-calves.png', 'front', 'primary'),
                ('Calves', 'muscular-anatomy-back.secondary-calves.png', 'back', 'secondary'),
                ('Calves', 'muscular-anatomy-front.secondary-calves.png', 'front', 'secondary'),
                ('Deltoids', 'muscular-anatomy-back.primary-deltoids.png', 'back', 'primary'),
                ('Deltoids', 'muscular-anatomy-front.primary-deltoids.png', 'front', 'primary'),
                ('Deltoids', 'muscular-anatomy-back.secondary-deltoids.png', 'back', 'secondary'),
                ('Deltoids', 'muscular-anatomy-front.secondary-deltoids.png', 'front', 'secondary'),
                ('Forearm', 'muscular-anatomy-back.primary-forearms.png', 'back', 'primary'),
                ('Forearm', 'muscular-anatomy-front.primary-forearms.png', 'front', 'primary'),
                ('Forearm', 'muscular-anatomy-back.secondary-forearms.png', 'back', 'secondary'),
                ('Forearm', 'muscular-anatomy-front.secondary-forearms.png', 'front', 'secondary'),
                ('Gluteus', 'muscular-anatomy-back.primary-gluteus.png', 'back', 'primary'),
                ('Gluteus', 'muscular-anatomy-back.secondary-gluteus.png', 'back', 'secondary'),
                ('Hamstring', 'muscular-anatomy-back.primary-hamstrings.png', 'back', 'primary'),
                ('Hamstring', 'muscular-anatomy-back.secondary-hamstrings.png', 'back', 'secondary'),
                ('Latissimus Dorsi', 'muscular-anatomy-front.primary-latissimus-dorsi.png', 'front', 'primary'),
                ('Latissimus Dorsi', 'muscular-anatomy-back.primary-latissimus-dorsi.png', 'back', 'primary'),
                ('Latissimus Dorsi', 'muscular-anatomy-back.secondary-latissimus-dorsi.png', 'back', 'secondary'),
                ('Latissimus Dorsi', 'muscular-anatomy-front.secondary-latissimus-dorsi.png', 'front', 'secondary'),
                ('Leg Abductor', 'muscular-anatomy-back.primary-outer-abductors.png', 'back', 'primary'),
                ('Leg Abductor', 'muscular-anatomy-front.primary-outer-abductor.png', 'front', 'primary'),
                ('Leg Abductor', 'muscular-anatomy-back.secondary-outer-abductors.png', 'back', 'secondary'),
                ('Leg Abductor', 'muscular-anatomy-front.secondary-outer-abductor.png', 'front', 'secondary'),
                ('Leg Adductor', 'muscular-anatomy-front.primary-inner-abductors.png', 'front', 'primary'),
                ('Leg Adductor', 'muscular-anatomy-back.primary-inner-abductors.png', 'back', 'primary'),
                ('Leg Adductor', 'muscular-anatomy-back.secondary-inner-abductors.png', 'back', 'secondary'),
                ('Leg Adductor', 'muscular-anatomy-front.secondary-inner-abductors.png', 'front', 'secondary'),
                ('Master', 'muscular-anatomy-front.png', 'front', ''),
                ('Master', 'muscular-anatomy-back.png', 'back', ''),
                ('Obliques', 'muscular-anatomy-back.primary-obliques.png', 'back', 'primary'),
                ('Obliques', 'muscular-anatomy-front.primary-obliques.png', 'front', 'primary'),
                ('Obliques', 'muscular-anatomy-back.secondary-obliques.png', 'back', 'secondary'),
                ('Obliques', 'muscular-anatomy-front.secondary-obliques.png', 'front', 'secondary'),
                ('Pectorals', 'muscular-anatomy-front.primary-pectorals.png', 'front', 'primary'),
                ('Pectorals', 'muscular-anatomy-front.secondary-pectorals.png', 'front', 'secondary'),
                ('Quadriceps', 'muscular-anatomy-front.primary-quadriceps.png', 'front', 'primary'),
                ('Quadriceps', 'muscular-anatomy-front.secondary-quadriceps.png', 'front', 'secondary'),
                ('Rest', 'rest.png', 'rest', 'rest'),
                ('Rotator Cuff', 'muscular-anatomy-back.primary-infraspinatus-subscapularis.png', 'back', 'primary'),
                ('Rotator Cuff', 'muscular-anatomy-back.secondary-infraspinatus-subscapularis.png', 'back', 'secondary'),
                ('Trapezius', 'muscular-anatomy-front.primary-trapezius.png', 'front', 'primary'),
                ('Trapezius', 'muscular-anatomy-back.primary-trapezius.png', 'back', 'primary'),
                ('Trapezius', 'muscular-anatomy-back.secondary-trapezius.png', 'back', 'secondary'),
                ('Trapezius', 'muscular-anatomy-front.secondary-trapezius.png', 'front', 'secondary'),
                ('Triceps', 'muscular-anatomy-front.primary-triceps.png', 'front', 'primary'),
                ('Triceps', 'muscular-anatomy-back.primary-triceps.png', 'back', 'primary'),
                ('Triceps', 'muscular-anatomy-back.secondary-triceps.png', 'back', 'secondary'),
                ('Triceps', 'muscular-anatomy-front.secondary-triceps.png', 'front', 'secondary');
        """
        curs.execute(sql)

    def create_set_tuple(self, ex):
        """
        create_set_tuple
        args: self - self object
            ex - exercise set to be tupled
        purpose: create a tuple for inserts and updates
        returns: exercise_set in a tuple
        """
        return [ex['name'],
                ex['trainer'],
                ex['workout name'],
                ex['target weight'],
                ex['target reps'],
                ex['weight unit name'],
                ex['left weight'],
                ex['right weight'],
                ex['left reps'],
                ex['right reps'],
                ex['time'],
                ex['left time'],
                ex['right time'],
                ex['set number'],
                self.workout_uuid]

    def create_sound_files_view(self, curs):
        """
        create_sound_files_view
        args: self - self object
            curs - cursor of app database
        purpose: create sound_files view from schema
        """
        sql = """
            CREATE VIEW "sound_files" AS 
            SELECT workout_program_alarm_sound_file AS sound_file
            FROM workout_program
            WHERE workout_program_alarm_sound_file IS NOT NULL
            UNION
            SELECT exercise_set_alarm_sound_file
            FROM exercise_set
            WHERE exercise_set_alarm_sound_file IS NOT NULL
        """
        curs.execute(sql)

    def create_weight_units_table(self, curs):
        """
        create_weight_units_table
        args: self - self object
            curs - cursor of app database
        purpose: create weight_units table from schema
        """
        sql = """
            CREATE TABLE "weight_units" (
	            "weight_units_name"	                TEXT NOT NULL UNIQUE,
	            "weight_units_name_abbreviation"	TEXT NOT NULL UNIQUE,
	            "weight_units_kilogram_conversion"	REAL NOT NULL,
	            "weight_units_id"	                INTEGER NOT NULL UNIQUE,
	            PRIMARY KEY("weight_units_id" AUTOINCREMENT)
            );"""
        curs.execute(sql)
        sql = """
            INSERT INTO weight_units (
                weight_units_name, 
                weight_units_name_abbreviation, 
                weight_units_kilogram_conversion) 
            VALUES 
                ('kilogram', 'kg', '1.0'),
                ('gram', 'g', '0.001'),
                ('ounce', 'oz', '0.02834952'),
                ('pound', 'lbs', '0.4535924');
        """
        curs.execute(sql)

    def create_workout_data_dictionary_view(self, curs):
        """
        create_workout_data_dictionary_view
        args: self - self object
            curs - cursor of app database
        purpose: create workout_data_dictionary view from schema
        """
        sql = """
            CREATE VIEW "workout_data_dictionary" AS 
            SELECT * FROM workout_type
            JOIN workout_program ON workout_program_type = workout_type_type
            JOIN exercise_set ON exercise_set_workout_program_name = workout_program_name AND
                exercise_set_workout_program_type = workout_program_type
            JOIN exercise_muscles ON exercise_muscles_exercise_name = exercise_set_exercise_name
            JOIN muscle_images ON muscle_images_muscle_group_name = exercise_muscles_muscle_group_name AND
                muscle_images_focus = exercise_muscles_muscle_focus
            LEFT JOIN weight_units ON weight_units_name = exercise_set_weight_units_name
            ORDER BY workout_type_name, workout_program_name, exercise_set_sort_index
        """
        curs.execute(sql)

    def create_workout_database(self, database_file_name):
        """
        create_workout_database
        args: self - self object
        purpose: create workout database
        returns: open workout database object
        """
        conn = sqlite3.connect(database_file_name)
        curs = conn.cursor()
        sql = """
            CREATE TABLE "workout" (
	            "exercise_date"	        TEXT NOT NULL,
	            "exercise_name"	        TEXT NOT NULL,
	            "trainer"	            TEXT,
	            "workout_name"	        TEXT,
	            "weight"	            REAL,
	            "reps"	                INTEGER,
	            "weight_unit"	        TEXT,
	            "left_weight"	        REAL,
	            "right_weight"	        REAL,
	            "left_reps"	            INTEGER,
	            "right_reps"	        INTEGER,
	            "set_count"	            INTEGER NOT NULL,
	            "body_weight_exercise"	INTEGER,
	            "key"	                TEXT NOT NULL,
	            "exercise_epoch"	    NUMERIC NOT NULL,
	            "time"	                INTEGER,
	            "left_time"	            INTEGER,
	            "right_time"	        INTEGER
        );"""
        curs.execute(sql)
        curs.execute('CREATE INDEX "exercise_date" ON "workout" ("exercise_date")')
        curs.execute('CREATE INDEX "exercise_name" ON "workout" ("exercise_name")')
        curs.execute('CREATE UNIQUE INDEX "workout_index" ON "workout" ("key", "set_count", "trainer", "workout_name")')
        conn.commit()
        curs.close()
        return conn

    def create_workout_program_table(self, curs):
        """
        create_workout_program_table
        args: self - self object
            curs - cursor of app database
        purpose: create workout_program table from schema
        """
        sql = """
            CREATE TABLE "workout_program" (
	            "workout_program_name"	            TEXT NOT NULL UNIQUE,
	            "workout_program_type"	            TEXT NOT NULL,
	            "workout_program_time_length"	    INTEGER,
	            "workout_program_alarm_sound_file"	TEXT,
	            "workout_program_id"	            INTEGER NOT NULL UNIQUE,
	            PRIMARY KEY("workout_program_id" AUTOINCREMENT)
            );"""
        curs.execute(sql)
        sql = """
            INSERT INTO workout_program (workout_program_name, workout_program_type) 
            VALUES ('You know what you want to do.  Just do it.', 'instinctual training')
        """
        curs.execute(sql)

    def create_workout_type_table(self, curs):
        """
        create_workout_type_table
        args: self - self object
            curs - cursor of app database
        purpose: create workout_type table from schema
        """
        sql = """
            CREATE TABLE "workout_type" (
	            "workout_type_name"	                    TEXT NOT NULL UNIQUE,
	            "workout_type_type"	                    TEXT NOT NULL,
	            "workout_type_image_file_name"	        TEXT NOT NULL,
	            "workout_type_finish_image_file_name"	TEXT,
	            "workout_type_id"	                    INTEGER NOT NULL UNIQUE,
	            PRIMARY KEY("workout_type_id" AUTOINCREMENT)
        ); """
        curs.execute(sql)
        sql = """
            INSERT INTO workout_type (
                workout_type_name, 
                workout_type_type, 
                workout_type_image_file_name, 
                workout_type_finish_image_file_name) 
            VALUES 
                ('Timed, Random, Muscle Confusion', 'timed, random, muscle confusion', 
                    'timed_random_muscle_confusion.png', 'clean_and_jerk_success_animation.reduced.gif'),
                ('Timed Workout with Timed Sets and Auto Advance', 'timed workout with timed sets and auto advance', 
                    'timed_workout_with_timed_sets_and_auto_advance.png', 'clean_and_jerk_success_animation.reduced.gif'),
                ('Classic Strength Training', 'classic strength training', 'eugen_sandow.jpeg', ''),
                ('Instinctual Training', 'instinctual training', 'instinctual_training.png', '');
        """
        curs.execute(sql)

    def delete_exercise(self, exercise_name):
        """
        delete_exercise
        args: self - self object
            exercise_name - name of exercise
        purpose: delete exercise from exercise table
        """
        return database_util.basic_edit(self.app_db, 'DELETE FROM exercise WHERE exercise_name = ?', (exercise_name,))

    def delete_exercise_group(self, workout_type, workout_program_name, exercise_group_name):
        """
        delete_exercise_group
        args: self - self object
            workout_type - workout type
            workout_program_name - name of workout program
            exercise_group_name - name of exercise group
        purpose: delete exercises that makeup an exercise group
        """
        Logger.info('workout_program: delete_exercise_group {}, {}, {}'.format(workout_type, workout_program_name, exercise_group_name))
        sql = """
            DELETE FROM exercise_set
            WHERE exercise_set_workout_program_type = ? AND
                exercise_set_workout_program_name = ? AND
                exercise_set_group_name = ?"""
        return database_util.basic_edit(self.app_db, sql,(workout_type, workout_program_name, exercise_group_name))

    def delete_exercise_muscle_mapping(self, exercise_name):
        """
        delete_exercise_muscle_mapping
        args: self - self object
            exercise_name - name of exercise
        purpose: delete rows of muscle mapping for exercise
        """
        return database_util.basic_edit(self.app_db, 'DELETE FROM exercise_muscles WHERE exercise_muscles_exercise_name = ?',
            (exercise_name,))

    def delete_workout_program_head(self, workout_type, workout_program_name):
        """
        delete_workout_program_head
        args: self - self object
            workout_type - type of workout program
            workout_program_name - name of workout program
        purpose: delete workout program header
        """
        sql = """
            DELETE FROM workout_program
            WHERE workout_program_type = ? AND
                workout_program_name = ?"""
        return database_util.basic_edit(self.app_db, sql,(workout_type, workout_program_name))

    def delete_workout_program_exercise_sets(self, workout_type, workout_program_name):
        """
        delete_workout_program_exercise_sets
        args: self - self object
            workout_type - type of workout program
            workout_program_name - name of workout program
        purpose: delete workout program exercise sets
        """
        sql = """
            DELETE FROM exercise_set
            WHERE exercise_set_workout_program_type = ? AND
                exercise_set_workout_program_name = ?"""
        return database_util.basic_edit(self.app_db, sql,(workout_type, workout_program_name))

    def get_body_muscle_image_template(self):
        """
        get_body_muscle_image_template
        args: self - self object
        purpose: retrieve muscle anatomy images
        returns: dictionary containing muscle anatomy images
        """
        return database_util.basic_query(self.app_db,
            "SELECT * FROM muscle_images WHERE muscle_images_muscle_group_name = 'Master'")

    def get_color_dates_by_year_month(self, year, month):
        """
        get_color_dates_by_year_month
        args: self - self object
            year - year of selection
            month - month of selection
        purpose: map color selection to workout history query for generic use
        """
        return self.get_workout_dates_by_year_month(year, month)

    def get_data_dict_database(self):
        """
        get_data_dict_database
        args: self - self object
        purpose: retrieve data to build workout data dictionary
        returns: dictionary of workout data dict view
        """
        return database_util.basic_query(self.app_db, 'SELECT * FROM workout_data_dictionary')

    def get_exercise(self, exercise_name):
        """
        get_exercise
        args: self - self object
            exercise_name - name of exercise
        purpose: get exercise
        returns: dictionary in list of exercise
        """
        sql = 'SELECT * FROM exercise WHERE exercise_name = ?'
        return database_util.basic_query(self.app_db, sql, values=(exercise_name,))

    def get_exercise_muscle_image_overlays(self):
        """
        get_exercise_muscle_image_overlays
        args: self - self object
        purpose: retrieve image overlays for creating color coded musculature images
        returns: dictionary containing image file names for muscle groups
        """
        sql = """
            SELECT * 
            FROM exercise_muscles 
            JOIN muscle_images ON muscle_images_muscle_group_name = exercise_muscles_muscle_group_name AND 
                muscle_images_focus = exercise_muscles_muscle_focus"""
        return database_util.basic_query(self.app_db, sql)

    def get_exercise_set(self, workout_type, workout_name, exercise_group_name, exercise_name):
        """
        get_exercise_set
        args: self - self object
            workout_type - workout type indicator
            workout_name - name of workout program
            exercise_group_name - exercise group name
            exercise_name - name of exercise
        purpose: retrieve row showing
        """
        sql = """
            SELECT exercise_set_workout_program_type AS workout_type,
        	    exercise_set_workout_program_name AS workout_name,
        	    exercise_set_group_name AS exercise_group,
        	    exercise_set_exercise_name AS exercise_name,
        	    exercise_set_weight_units_name AS weight_unit,
        	    exercise_set_target_reps AS reps,
        	    exercise_set_set_timer AS timer,
        	    exercise_set_target_weight AS weight,
        	    exercise_set_left_weight AS left_weight,
        	    exercise_set_right_weight AS right_weight,
        	    exercise_set_left_reps AS left_reps,
        	    exercise_set_right_reps AS right_reps,
        	    exercise_set_set_count AS count,
        	    exercise_set_sort_index AS sort_index
            FROM exercise_set
            WHERE workout_type = ? AND
        	    workout_name = ? AND
        	    exercise_group = ? AND
        	    exercise_name = ?"""
        return database_util.basic_query(self.app_db, sql,
            values=(workout_type, workout_name, exercise_group_name, exercise_name))

    def get_exercise_set_group(self, workout_type, workout_name, exercise_group_name):
        """
        get_exercise_set_group
        args: self - self object
            workout_type - type of workout
            workout_name - workout name
            exercise_group_name - name of exercise set group
        purpose: retrieve an exercise set group
        returns: list of dicts containing the matching exercise group sets
        """
        sql = """
            SELECT *
            FROM exercise_set
            WHERE exercise_set_workout_program_type = ? AND
                exercise_set_workout_program_name = ? AND
                exercise_set_group_name = ?
            ORDER BY exercise_set_sort_index ASC"""
        return database_util.basic_query(self.app_db, sql, values=(workout_type, workout_name, exercise_group_name))

    def get_exercises(self, exercise_name_part, limit):
        """
        get_exercises
        args: self - self object
            exercise_name_part - start of exercise name to search for
            limit - max num of lines to return
        purpose: get list of exercises
        returns: list of exercises
        """
        query_val = exercise_name_part + '%'
        sql = 'SELECT * FROM exercise WHERE exercise_name LIKE ? ORDER BY exercise_name ASC LIMIT ?'
        return database_util.basic_query(self.app_db, sql, values=(query_val, limit))

    def get_exercises_by_muscle(self, muscle_name):
        """
        get_exercise_by_muscle
        args: self - self object
            muscle_name - name of muscle
        purpose: retrieve the muscles of an exercise
        returns: data dict of exercises for set muscle
        """
        sql =  """
            SELECT * 
            FROM exercise_muscles 
            WHERE exercise_muscles_muscle_group_name = ? AND 
                exercise_muscles_muscle_focus = 'primary' 
            ORDER BY exercise_muscles_exercise_name"""
        return database_util.basic_query(self.app_db, sql, values=(muscle_name,))

    def get_muscle_by_exercise(self, exercise_name):
        """
        get_muscle_by_exercise
        args: self - self object
            exercise_name - exercise name to retrieve muscles for
        purpose: retrieve the muscle mappings for an exercise
        returns: array of dictionaries of muscle name and focus of the exercise muscles
        """
        sql = """
            SELECT DISTINCT exercise_muscles_muscle_group_name AS muscle_name,
    	        exercise_muscles_muscle_focus AS focus
            FROM exercise_muscles
            JOIN muscle_images ON muscle_images_muscle_group_name = exercise_muscles_muscle_group_name AND
	            muscle_images_focus = exercise_muscles_muscle_focus
            WHERE exercise_muscles_exercise_name = ?"""
        return database_util.basic_query(self.app_db, sql, values=(exercise_name,))

    def get_muscle_map_images(self):
        """
        get_muscle_overlay_images
        args: self - self object
        purpose: return muscle image database
        returns: returns muscle image data in a dictionary
        """
        return database_util.basic_query(self.app_db, 'SELECT * FROM muscle_images')

    def get_set(self, set_count, trainer, workout_name):
        """
        get_set
        args: self - self object
            set_count - number of set
            trainer - type of the trainer for the set
            workout_name - name of workout
        purpose: find set
        """
        return database_util.basic_query(self.workout_db,
            'SELECT * FROM workout WHERE key = ? AND set_count = ? AND trainer = ? AND workout_name = ?',
            values=(self.workout_uuid, set_count, trainer, workout_name))

    def get_sound_files(self):
        """
        get_sound_files
        args: self - self object
        purpose: return a dict of all the sound files in the database
        returns: dictionary of sound file names
        """
        return database_util.basic_query(self.app_db, 'SELECT * FROM sound_files')

    def get_suggestion_set(self, exercise_name):
        """
        get_suggestion_set
        args: self - self object
            exercise_name - name of exercise to perform match
        purpose: return the most recent first set of historic workouts
        returns: single
        """
        sql = """
            SELECT * 
            FROM workout 
            WHERE exercise_name = ? 
            ORDER BY exercise_date DESC, exercise_epoch ASC 
            LIMIT 1"""
        return database_util.basic_query(self.workout_db, sql, values=(exercise_name,))

    def get_weight_units(self):
        """
        get_weight_units
        args: self - self object
        purpose: return weight unit data
        returns: returns weight unit data in a dictionary
        """
        return database_util.basic_query(self.app_db, 'SELECT * FROM weight_units')

    def get_workout_dates_by_year_month(self, year, month):
        """
        get_workout_dates_by_year_month
        args: self - self object
            year - year to match on
            month - month to match on
        purpose: return list of workout days for datepicker cosmetics
        returns: list of dictionaries of ISO format date strings
        """
        date_str = f'{year:04}-{month:02}-%'
        sql = 'SELECT DISTINCT exercise_date AS date FROM workout WHERE exercise_date LIKE ?'
        return database_util.basic_query(self.workout_db, sql, values=(date_str,))

    def get_workout_history(self):
        """
        get_workout_history
        args: self - self object
        purpose: return historical exercises
        returns: dictionary containing past workouts
        """
        sql = 'SELECT * FROM workout ORDER BY exercise_date DESC, exercise_epoch ASC'
        return database_util.basic_query(self.workout_db, sql)

    def get_workout_program(self, workout_type, workout_name):
        """
        get_workout_program
        args: self - self object
            workout_type - type of workout to retrieve
            workout_name - name of workout to retrieve
        purpose: retrieve data for a workout
        returns: list of dictionaries containing workout data
        """
        sql = """
            SELECT DISTINCT 
                exercise_set_exercise_name AS exercise_name,
                exercise_set_group_name AS exercise_group_name,
                exercise_set_left_reps AS left_reps,
                exercise_set_left_weight AS left_weight,
                exercise_set_muscle_group_name AS muscle_group,
                exercise_set_right_reps AS right_reps,
                exercise_set_right_weight AS right_weight,
                exercise_set_set_count AS set_count,
                exercise_set_set_timer AS set_time,
                exercise_set_sort_index AS order_index,
                exercise_set_target_reps AS target_reps,
                exercise_set_target_weight AS target_weight,
                exercise_set_weight_units_name AS weight_units,
                workout_program_time_length AS workout_time
            FROM workout_data_dictionary
            WHERE workout_type_type = ? AND
    	        workout_program_name = ?
    	    ORDER BY {}order_index ASC""".format('exercise_group_name, ' if
                workout_type == 'timed, random, muscle confusion' else '')
        return database_util.basic_query(self.app_db, sql, values=(workout_type, workout_name))

    def get_workout_program_head(self, workout_type, workout_name):
        """
        get_workout_program_head
        args: self - self object
            workout_type - type of workout
            workout_name - workout name
        purpose: retrieve workout program
        returns: workout program
        """
        sql = """
            SELECT * 
            FROM workout_program 
            WHERE workout_program_name = ? AND 
                workout_program_type = ? """
        return database_util.basic_query(self.app_db, sql, values=(workout_name, workout_type))

    def get_workout_program_heads(self, workout_type):
        """
        get_workout_program_heads
        args: self - self object
            workout_type - workout type to query
        purpose: retrieve all workout program heads for a workout type
        returns: dictionary of workout_program table matching workout type
        """
        sql = """
            SELECT *
            FROM workout_program
            WHERE workout_program_type = ?
            ORDER BY workout_program_name"""
        return database_util.basic_query(self.app_db, sql, values=(workout_type,))

    def get_workout_program_selector_bubble(self, workout_name_part, workout_type, limit):
        """
        get_workout_program_selector_bubble
        args: self - self object
            workout_name - front part of workout name
            workout_type - type of workout
            limit - query limit
        purpose: retrieve possible matching workouts for workout builder
        returns: a list of matching workout names for workout selection bubble
        """
        query_val = workout_name_part + '%'
        sql = """
            SELECT workout_program_name 
            FROM workout_program 
            WHERE workout_program_name LIKE ? AND 
                workout_program_type = ? 
            ORDER BY workout_program_name ASC
            LIMIT ?"""
        return database_util.basic_query(self.app_db, sql, values=(query_val, workout_type, limit))

    def get_workout_types(self):
        """
        get_workout_types
        args: self - self object
        purpose: return list of workout types 
        returns: workout type data dictionary list
        """
        return database_util.basic_query(self.app_db, 'SELECT * FROM workout_type')

    def insert_workout_set(self, workout_type, workout_name, set_row):
        """
        insert_workout_set
        args: self - self object
            workout_type - type of workout
            workout_name - name of workout
            set_row - dictionary containing set data
        purpose: insert a workout program set row
        """
        workout_program = self.get_workout_program_head(workout_type, workout_name)
        if workout_program:
            sql = """
                INSERT INTO exercise_set (
                    exercise_set_alarm_sound_file,
                    exercise_set_exercise_name,
                    exercise_set_group_name,
                    exercise_set_left_reps,
                    exercise_set_left_weight,
                    exercise_set_muscle_group_name,
                    exercise_set_right_reps,
                    exercise_set_right_weight,
                    exercise_set_set_count,
                    exercise_set_set_timer,
                    exercise_set_sort_index,
                    exercise_set_target_reps,
                    exercise_set_target_weight,
                    exercise_set_weight_units_name,
                    exercise_set_workout_program_name,
                    exercise_set_workout_program_type)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            values = (set_row['alarm_file'], set_row['exercise_name'], set_row['exercise_group_name'],
                set_row['left_reps'], set_row['left_weight'], set_row['muscle_group'], set_row['right_reps'],
                set_row['right_weight'], set_row['set_count'], set_row['set_time'], set_row['insert_sort_index'],
                set_row['target_reps'], set_row['target_weight'], set_row['weight_units'], workout_name, workout_type)
            database_util.basic_edit(self.app_db, sql, values)
        else:
            Logger.info('database: ERROR insert_workout_set called with missing workout program header table row')

    def store_exercise(self, exercise_name):
        """
        store_exercise
        args: self - self object
            exercise_name - name of exercise
        purpose: insert a new exercise into the exercise database
        """
        results = database_util.basic_query(self.app_db, 'SELECT * FROM exercise WHERE exercise_name = ?',
            values=(exercise_name,))
        if not results:
            sql = 'INSERT INTO exercise (exercise_name) VALUES(?)'
            database_util.basic_edit(self.app_db, sql, (exercise_name,))

    def store_exercise_muscle_mapping(self, exercise_name, muscle_name, focus):
        """
        store_exercise_muscle_mapping
        args: self - self object
            exercise_name - name of exercise
            muscle_name - name of muscle group
            focus - primary or secondary muscle focus
        purpose: insert or update exercise muscle mapping
        """
        sql = """
            SELECT * 
            FROM exercise_muscles 
            WHERE exercise_muscles_exercise_name = ? AND 
            exercise_muscles_muscle_group_name = ?"""
        results = database_util.basic_query(self.app_db, sql, values=(exercise_name, muscle_name))
        if results:
            sql = """
                UPDATE exercise_muscles 
                SET exercise_muscles_muscle_focus = ? 
                WHERE exercise_muscles_exercise_name = ? AND 
                    exercise_muscles_muscle_group_name = ?"""
        else:
            sql = """
                INSERT INTO exercise_muscles (
                    exercise_muscles_muscle_focus, 
                    exercise_muscles_exercise_name, 
                    exercise_muscles_muscle_group_name) 
                VALUES(?, ?, ?)"""
        database_util.basic_edit(self.app_db, sql, (focus, exercise_name, muscle_name))

    def store_set(self, exercise_set):
        """
        store_set
        args: self - self object
            exercise_set - exercise set dictionary
        purpose: record set to database
        """
        db_set = self.get_set(exercise_set['set number'], exercise_set['trainer'], exercise_set['workout name'])
        set_array = self.create_set_tuple(exercise_set)
        if db_set:
            sql = """UPDATE workout
                SET exercise_date = DATE('now', 'localtime'),
                    exercise_epoch = STRFTIME('%s'),
                    exercise_name = ?,
                    trainer = ?,
                    workout_name = ?,
                    weight = ?,
                    reps = ?,
                    weight_unit = ?,
                    left_weight = ?,
                    right_weight = ?,
                    left_reps = ?,
                    right_reps = ?,
                    time = ?,
                    left_time = ?,
                    right_time = ?
                WHERE set_count = ? AND
                    key = ? AND
                    trainer = ? AND
                    workout_name = ?"""
            set_array.append(exercise_set['trainer'])
            set_array.append(exercise_set['workout name'])
        else:
            sql = """INSERT INTO workout(
                    exercise_date, 
                    exercise_epoch, 
                    exercise_name, 
                    trainer, 
                    workout_name, 
                    weight, 
                    reps, 
                    weight_unit, 
                    left_weight, 
                    right_weight, 
                    left_reps, 
                    right_reps, 
                    time, 
                    left_time, 
                    right_time, 
                    set_count, 
                    key)
                VALUES (DATE('now', 'localtime'), STRFTIME('%s'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        database_util.basic_edit(self.workout_db, sql, tuple(set_array))

    def store_workout_program_head(self, workout_type, workout_name, length, alarm_file):
        """
        store_workout_program_head
        args: self - self object
            workout_type - type of workout
            workout_name - name of workout
            length - length of workout can be None
            alarm_file - sound file name of alarm
        purpose: create or update a workout program header row
        """
        workout_program = self.get_workout_program_head(workout_type, workout_name)
        if workout_program:
            sql = """
                UPDATE workout_program
                SET workout_program_time_length = ?, 
                    workout_program_alarm_sound_file = ?
                WHERE workout_program_type = ? AND
                    workout_program_name = ?"""
        else:
            sql = """
                INSERT INTO workout_program(
                    workout_program_time_length, 
                    workout_program_alarm_sound_file,
                    workout_program_type, 
                    workout_program_name)
                VALUES(?, ?, ?, ?)"""
        values =  (length, alarm_file, workout_type, workout_name)
        database_util.basic_edit(self.app_db, sql, values)
