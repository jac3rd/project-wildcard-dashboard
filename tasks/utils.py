from datetime import datetime, timedelta
from calendar import HTMLCalendar

from .models import Event

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, tasks):
        tasks_per_day = event.filter(start_time_day=day)
        d = ''
        for task in tasks_per_day:
            d += f'<li class="calendar_list"> {task.get_html_url} </li>'
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    def formatweek(self, theweek):
        return super().formatweek(theweek)