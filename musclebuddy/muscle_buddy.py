#!/usr/bin/env python3
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
import pickle
#import pprint #debug 
import random
import time
from collections import OrderedDict
from kivy.config import Config
from kivy.logger import Logger, LOG_LEVELS
#local imports
import database
import database_util
import datadict
import view

def main():
    """
    main
    purpose: provide main program function for app
    """
    Config.set('graphics', 'allow_screensaver', False)
    Config.set('kivy', 'exit_on_escape', False)
    Logger.setLevel(LOG_LEVELS['info']) # change to "info" for production
    if not os.path.exists('scale.kv'):
        with open('scale.kv', 'w') as file:
            file.write('#:set window_width 360\n#:set window_height 720\n')
    random.seed()
    db = database.Database()
    dict_manager = datadict.DataDict()
    loop = True
    while loop:
        loop = run(db, dict_manager)

def run(db, dict_manager):
    """
    run
    args: db - database object
        dict_manager - dictionary manager object
    purpose: provide run function for app
    returns: boolean indicator as to if restart is required
    """
    stime = time.time()
    pickle_file = os.path.join('database', 'pause.pickle')
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as f:
            data_root = pickle.load(f)
        db.workout_uuid = data_root['global properties']['workout uuid']
    else:
        loaded_dict = dict_manager.get_workout_dict(db)
        data_root = {
            'completed workout sets': [],
            'config': loaded_dict['config'],
            'global properties': loaded_dict['global properties'],
            'images': loaded_dict['images'],
            'image overlays': dict_manager.get_image_overlays(db),
            'weight units': loaded_dict['weight units'],
            'workout dictionary': loaded_dict['workout dictionary']
        }
        data_root['global properties']['workout uuid'] = db.workout_uuid
    data_root['global properties']['application start time'] = stime
    data_root['unpickleable'] = OrderedDict([
        ('clock processes', {}),
        ('database', db),
        ('dictionary manager', dict_manager),
        ('muscle selector maps', dict_manager.get_muscle_selector_image_maps(db))
    ])
    app = view.MuscleBuddyApp(data_root)
    app.run()
    database_util.store_config(db.app_db, data_root['config'])
    Logger.info('Application: exiting to main')
#    pprint.pprint(data_root) # debug
    return True if 'reset' in data_root and data_root['reset'] else False

if __name__ == '__main__':
    main()
