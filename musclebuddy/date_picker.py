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
from kivy.logger import Logger
from kivymd.uix.label import MDLabel
from kivymd.uix.pickers import MDDatePicker
# local imports
import over_press

class DatePicker(MDDatePicker):
    get_color_dates_by_year_month = None

    def __init__(self, year=None, month=None, day=None, firstweekday=0, color_picker_func=None, **kwargs,):
        """
        __init__
        args: self - self object
            year - optional year to set calendar to
            month - optional month to set calendar to
            firstweekday - first day of week, 0 = Monday
            color_picker_func - function to call for setting color dates
            kwargs - mystery args
        purpose: replace default init so edit button can be disabled and hid to avoid virtual keyboard issues
        """
        self.get_color_dates_by_year_month = color_picker_func
        super().__init__(year=year, month=month, day=day, firstweekday=firstweekday, **kwargs)
        self.ids['edit_icon'].disabled = True
        self.ids['edit_icon'].icon = ''

    def change_month(self, operation: str) -> None:
        """
        change_month
        args: self - self object
            operation - next item
        purpose: fixes over press issue occurring with change_month method in MDDatePicker
        """
        Logger.info('date_picker: change_month')
        if over_press.protect(vibrate=True):
            super().change_month(operation)

    def set_selected_widget(self, widget):
        """
        set_selected_widget
        args: self - self object
            widget - widget to select
        purpose: add vibrate to date selection
        """
        Logger.info('date_picker: set_selected_widget')
        if over_press.protect(vibrate=True):
            super().set_selected_widget(widget)

    def transformation_from_dialog_select_year(self):
        """
        transformation_from_dialog_select_year
        args: self - self object
        purpose: fixes over press issue occurring with transformation_from_dialog_select_year method in MDDatePicker
        """
        Logger.info('date_picker: transformation_from_dialog_select_year')
        if over_press.protect(vibrate=True):
            super().transformation_from_dialog_select_year()

    def transformation_to_dialog_select_year(self):
        """
        transformation_to_dialog_select_year
        args: self - self object
        purpose: fixes over press issue occurring with transformation_to_dialog_select_year method in MDDatePicker
        """
        Logger.info('date_picker: transformation_to_dialog_select_year')
        if over_press.protect(vibrate=True):
            super().transformation_to_dialog_select_year()

    def update_calendar(self, year, month):
        """
        update_calendar
        args: self - self object
            year - year of datepicker calendar
            month - month of datepicker calendar
        purpose: override update_calendar to change color of dates in datepicker for days with workout data
        """
        Logger.info(f'date_picker: update_calendar {year} {month}')
        super().update_calendar(year, month)
        if not self.get_color_dates_by_year_month:
            app = App.get_running_app()
            self.get_color_dates_by_year_month = (
                app.app_data_dict['unpickleable']['database'].get_color_dates_by_year_month)
        workout_dates = self.get_color_dates_by_year_month(year, month)
        color_days = [int(row['date'][-2:]) for row in workout_dates]
        for day_widget in self._calendar_list:
            for label in day_widget.children:
                if isinstance(label, MDLabel):
                    if day_widget.text.isdigit() and int(day_widget.text) in color_days:
                        label.text_color = (1, 1, 0, 1)
                        label.bold = True
                    else:
                        label.text_color = (1, 1, 1, 1)
                        label.bold = False
