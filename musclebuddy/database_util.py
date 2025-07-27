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
import json
from kivy.logger import Logger

def basic_edit(db, sql, values):
    """
    basic_edit
    args: db - database object
        sql - SQL insert or update statement
        values - tuple containing values for SQL statement
    purpose: insert or update database
    """
    curs = db.cursor()
    try:
        curs.execute(sql, values)
        db.commit()
    except Exception as e:
        Logger.info('database: {}'.format(str(e)))
        Logger.info('database: {}'.format(str(sql)))
        Logger.info('database: {}'.format(str(values)))
    curs.close()

def basic_query(db, query_str, values=None):
    """
    basic_query
    args: db - database object
        query_str - query string
        values - optional tuple of values
    purpose: perform a basic query
    returns: list of dictionaries containing results
    """
    curs = db.cursor()
    if values:
        res = curs.execute(query_str, values)
    else:
        res = curs.execute(query_str)
    raw_dict = dict_encode(curs)
    curs.close()
    return raw_dict

def conditional_config_insertion(db, key, json_val):
    """
    conditional_config_insertion
    args: db - app database obj
        key - config key
        json_val - dictionary to convert into json for database storage
    purpose: initialize a missing config element
    """
    sql = "INSERT INTO config (config_key, config_json) VALUES (?, ?)"
    if not config_exists(db, key):
        json_str = json.dumps(json_val)
        basic_edit(db, sql, (key, json_str))

def config_exists(db, config_key):
    """
    config_exists
    args: db - app database object
        config_key - config key to check for
    purpose: return indicator of if config exists in config table
    returns: boolean indicator of config option existence
    """
    result = basic_query(db, 'SELECT * FROM config WHERE config_key = ?', values=(config_key,))
    return bool(result)

def create_config_table(curs):
    """
    create_config_table
    args: curs - cursor of app database
    purpose: create config table from schema
    """
    sql = """
        CREATE TABLE "config" (
            "config_key"	TEXT NOT NULL UNIQUE,
            "config_json"	TEXT NOT NULL,
            PRIMARY KEY("config_key")
        );"""
    curs.execute(sql)

def dict_encode(curs):
    """
    dict_encode
    args: curs - database cursor
    purpose: convert a query cursor into an array of dictionaries for easy parsing
    returns: list of dictionaries containing query results
    """
    columns = [i[0] for i in curs.description]
    result = []
    try:
        for row in curs:
            rowDict = {}
            for i, col in enumerate(columns):
                rowDict[col] = row[i]
            result.append(rowDict)
    except Exception as e:
        Logger.info('database: {}'.format(str(e)))
    return result

def get_config(db): # consider moving to a lib cjh
    """
    get_config
    args: db - app database obj
    purpose: retrieve config
    returns: dictionary containing app config
    """
    config_dict = {}
    results = get_config_table(db)
    for config_item in results:
        config_dict[config_item['config_key']] = json.loads(config_item['config_json'])
    return config_dict

def get_config_table(db):
    """
    get_config_table
    args: db - app database object
    purpose: retrieve application configuration
    returns: dictionary of configuration options
    """
    conditional_config_insertion(db, 'hardware keyboard', {"active": True})
    conditional_config_insertion(db, 'selection bubble', {"selection limit": 3})
    conditional_config_insertion(db, 'software keyboard', {"active": True})
    conditional_config_insertion(db, 'vibrate', {"active": True})
    conditional_config_insertion(db, 'volume', {'mute': False, 'percent': 100})
    results = basic_query(db, 'SELECT * FROM config')
    return results

def store_config(db, config):
    """
    store_config
    args: db - app database obj
        config - dictionary of configuration options
    purpose: write config to disk
    """
    update_sql = 'UPDATE config SET config_json = ? WHERE config_key = ?'
    insert_sql = 'INSERT INTO config (config_json, config_key) VALUES (?, ?)'
    for config_key, dict_obj in config.items():
        json_str = json.dumps(dict_obj)
        if config_exists(db, config_key):
            basic_edit(db, update_sql, (json_str, config_key))
        else:
            basic_edit(db, insert_sql, (json_str, config_key))
