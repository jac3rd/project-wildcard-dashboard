from datetime import datetime, timedelta
from calendar import HTMLCalendar

from .models import Task

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, tasks):
        tasks_per_day = tasks.filter(end_time__day=day).order_by('end_time')
        d = ''
        for task in tasks_per_day:
            d += f'<li class="list-group-item"> {task.task_name} - {task.end_time.time()} </li>'
        if day != 0:
            return f'<td><span class=\'date\'>{day}</span><ul class="list-group"> {d} </ul></td>'
        return '<td></td>'

    def formatweek(self, theweek, tasks):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, tasks)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True):
        tasks = Task.objects.filter(end_time__year=self.year, end_time__month=self.month)
        cal = f'<table class="calendar table table-hover table-bordered table-striped"><tbody>\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, tasks)}\n'
        cal += f'</tbody></table>'
        return cal