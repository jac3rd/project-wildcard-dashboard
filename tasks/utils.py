from datetime import datetime, timedelta
from calendar import HTMLCalendar

from .models import Task

from django.urls import reverse

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    def formatday(self, day, tasks):
        tasks_per_day = tasks.filter(end_time__day=day, ).order_by('end_time')
        d = ''
        for task in tasks_per_day:
            list_group_color = ''
            if task.category == 'Homework':
                list_group_color = ' list-group-item-primary'
            elif task.category == 'Chore':
                list_group_color = ' list-group-item-warning'
            elif task.category == 'Work':
                list_group_color = ' list-group-item-danger'
            elif task.category == 'Errand':
                list_group_color = ' list-group-item-info'
            elif task.category == 'Life':
                list_group_color = ' list-group-item-success'
            elif task.category == 'Other':
                list_group_color = ' list-group-item-secondary'
            d += f'<li class="list-group-item p-2' + list_group_color + f'"> <b>{task.task_name}</b> - <i>{task.end_time.time()}</i><br/><span><form action="{reverse("tasks:move_date_backward")}" method="post" style="display:inline"><input type="hidden" name="task_id" value="{task.id}"><button class="btn btn-sm btn-warning" type="submit" formmethod="post" data-toggle="tooltip" data-placement="bottom" title="Move backward 1 day"><svg class="bi bi-arrow-left" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5.854 4.646a.5.5 0 010 .708L3.207 8l2.647 2.646a.5.5 0 01-.708.708l-3-3a.5.5 0 010-.708l3-3a.5.5 0 01.708 0z" clip-rule="evenodd"/><path fill-rule="evenodd" d="M2.5 8a.5.5 0 01.5-.5h10.5a.5.5 0 010 1H3a.5.5 0 01-.5-.5z" clip-rule="evenodd"/></svg></button></form>&nbsp<form action="{reverse("tasks:move_date_forward")}" method="post" style="display:inline"><input type="hidden" name="task_id" value="{task.id}"><button class="btn btn-sm btn-info" type="submit" formmethod="post" data-toggle="tooltip" data-placement="bottom" title="Move forward 1 day"><svg class="bi bi-arrow-right" width="1em" height="1em" viewBox="0 0 16 16" fill="currentColor" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10.146 4.646a.5.5 0 01.708 0l3 3a.5.5 0 010 .708l-3 3a.5.5 0 01-.708-.708L12.793 8l-2.647-2.646a.5.5 0 010-.708z" clip-rule="evenodd"/><path fill-rule="evenodd" d="M2 8a.5.5 0 01.5-.5H13a.5.5 0 010 1H2.5A.5.5 0 012 8z" clip-rule="evenodd"/></svg></button></form><span></li>'
        if day != 0:
            return f'<td class="col-1 p-2"><span class=\'date\'><b>{day}</b></span><ul class="list-group"> {d} </ul></td>'
        return '<td class="col-1 p-2"></td>'

    def formatweek(self, theweek, tasks):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, tasks)
        return f'<tr> {week} </tr>'

    def formatmonth(self, withyear=True, user=-1, archived=False, weekonly=False):
        tasks = Task.objects.filter(end_time__year=self.year, end_time__month=self.month, user=user, archived=archived)
        cal = f'<table class="calendar table table-hover table-bordered table-striped"><tbody>\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            if (not weekonly) or (week[0][0] <= datetime.now().day and week[week.__len__()-1][0] >= datetime.now().day):
                cal += f'{self.formatweek(week, tasks)}\n'
        cal += f'</tbody></table>'
        return cal