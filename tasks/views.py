from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Min, Sum, Avg
from django.db.models.functions import Cast, Extract
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from djqscsv import render_to_csv_response
from django.views.generic import TemplateView, ListView
from django.core.exceptions import ObjectDoesNotExist

from .forms import TaskForm, FilterForm
from .models import Task, Category, ShowArchived
import datetime
from graphos.renderers.gchart import LineChart, PieChart
from graphos.sources.model import SimpleDataSource
from django.db.models import DateField
from django.utils import safestring
from .utils import Calendar
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib.parse import urlparse
from math import floor


def remove_omitted_fields():
    omitted_fields = set(['id', 'user', 'created_at', 'completed', 'archived'])
    l = []
    for field in Task._meta.get_fields():
        val = field.name
        if val in omitted_fields:
            continue
        elif '_' in val:
            l.append((val.replace('_', ' '), val))
            continue
        else:
            l.append((val, val))
    return l


class SummaryView(generic.ListView):
    model = Task
    template_name = 'tasks/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_list = Task.objects.filter(user=self.request.user.id, archived=False,
                                        end_time__gte=datetime.datetime.now())
        task_list = task_list.order_by('end_time')
        d = get_date(self.request.GET.get('day', None))
        cal = Calendar(d.year, d.month)
        tasks_left = 0
        est_hours = 0
        est_minutes = 0
        state = 0
        for week in cal.monthdayscalendar(cal.year, cal.month):
            if week[0] <= datetime.datetime.now().day <= week[week.__len__() - 1]:
                curr_week = week
        for task in task_list:
            if task.end_time.day in curr_week:
                if not task.completed:
                    tasks_left += 1
                    est_hours += task.hours
                    est_minutes += task.minutes
                else:
                    state += 1
        task_list = task_list[:5]
        est_hours += floor(est_minutes / 60)
        est_minutes %= 60
        html_cal = cal.formatmonth(withyear=True, weekonly=True, user=self.request.user.id)
        context['task_list'] = task_list
        context['calendar'] = safestring.mark_safe(html_cal)
        context['tasks_left'] = tasks_left
        context['est_hours'] = est_hours
        context['est_minutes'] = est_minutes
        context['state'] = state
        return context


# Create your views here.
class TaskListView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        sort_key = self.request.GET.get('sort_by', 'give-default-value')

        """
        show_arch is used to determine whether to filter out archived tasks
        If current user does not have ShowArchived model, make one
        """
        show_arch = False
        try:
            if self.request.user.is_authenticated:
                show_arch = ShowArchived.objects.get(user=self.request.user.id).show_archived
            else:
                return render(self.request, 'tasks/login.html')
        except:
            sa = ShowArchived()
            # sa.show_archived = False;
            sa.user = self.request.user.id
            sa.save()

        if sort_key != 'give-default-value' and not show_arch:
            return Task.objects.filter(user=self.request.user.id, archived=False).order_by(sort_key, 'created_at')
        elif sort_key != 'give-default-value' and show_arch:
            return Task.objects.filter(user=self.request.user.id).order_by(sort_key, 'created_at')
        elif sort_key == 'give-default-value' and not show_arch:
            return Task.objects.filter(user=self.request.user.id, archived=False).order_by('end_time', 'created_at')
        else:
            return Task.objects.filter(user=self.request.user.id).order_by('end_time', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = remove_omitted_fields()
        if self.request.user.is_authenticated:
            context['sa'] = ShowArchived.objects.get(user=self.request.user.id)
        return context


@login_required
def add_task(request):
    """
    Used to add a task to the personal dashboard
    :param request: The form posting from the add_task.html page
    :return: A redirect depending on whether or not the input was good
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = Task()
            t.user = request.POST.get('user')
            t.task_name = request.POST.get('task_name')
            t.task_desc = request.POST.get('task_desc')
            t.end_time = request.POST.get('end_time')
            t.hours = request.POST.get('hours')
            t.minutes = request.POST.get('minutes')
            t.category = request.POST.get('category')
            t.link = request.POST.get('link', "")
            # Ensure that the start dates are correct
            if t.end_time < str(datetime.datetime.now()):
                return render(request, 'tasks/add_task.html',
                              {'form': form, 'error_message': "Due date must be later than current time.", })
            elif int(t.minutes) < 0 or int(t.minutes) >= 60 or int(t.hours) < 0:
                return render(request, 'tasks/add_task.html',
                              {'form': form,
                               'error_message': "Please enter valid time values! (Hours >= 0 and 0 <= Min <= 59)", })
            else:
                t.completed = False
                t.save()
                if request.POST.get('repeat') == 'once':
                    multiplier = 0
                elif request.POST.get('repeat') == 'weekly':
                    multiplier = 1
                elif request.POST.get('repeat') == 'monthly':
                    multiplier = 4
                elif request.POST.get('repeat') == 'annually':
                    multiplier = 52
                for i in range(1, int(request.POST.get('times')) + 1):
                    curr_t = Task()
                    curr_t.task_name = request.POST.get('task_name')
                    curr_t.task_desc = request.POST.get('task_desc')
                    curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                        weeks=i * multiplier)
                    curr_t.hours = request.POST.get('hours')
                    curr_t.minutes = request.POST.get('minutes')
                    curr_t.user = request.POST.get('user')
                    curr_t.completed = False
                    curr_t.link = request.POST.get('link', "")
                    curr_t.save()
                return HttpResponseRedirect(reverse('tasks:list'))
    else:
        form = TaskForm()
    return render(request, 'tasks/add_task.html', {'form': form})


def check_off(request):
    """
    This allows you to check off a completed task.
    :param request: A request that contains a primary key for the task being completed.
    :return: A redirect to our index page for tasks.
    """
    url_path_from = 'tasks:list'
    if request.method == 'POST':
        url_path_from = list(filter(None, urlparse(request.META.get('HTTP_REFERER')).path.split("/")))
        url_path_from = ':'.join(url_path_from)
        if url_path_from == 'tasks' or url_path_from == "":
            url_path_from = 'tasks:index'
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.completed = True
        task.date_completed = datetime.datetime.now().date()
        task.save()
    return HttpResponseRedirect(reverse(url_path_from))


def uncheck(request):
    """
    This allows a mistakenly checked off task to be marked as uncompleted.
    :param request: A request that contains a primary key for the task being unmarked.
    :return: A redirect to our index page for tasks.
    """
    url_path_from = 'tasks:list'
    if request.method == 'POST':
        url_path_from = list(filter(None, urlparse(request.META.get('HTTP_REFERER')).path.split("/")))
        url_path_from = ':'.join(url_path_from)
        if url_path_from == 'tasks' or url_path_from == "":
            url_path_from = 'tasks:index'
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.completed = False
        task.save()
    return HttpResponseRedirect(reverse(url_path_from))


def archive_task(request):
    url_path_from = 'tasks:list'
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        if not task.archived:
            task.archived = True
        else:
            task.archived = False
        task.save()
    return HttpResponseRedirect(reverse(url_path_from))


def checkbox_archived(request):
    """
        This allows a user to see his/her archived tasks.
    """
    url_path_from = 'tasks:list'
    if request.method == 'POST':
        url_path_from = list(filter(None, urlparse(request.META.get('HTTP_REFERER')).path.split("/")))
        url_path_from = ':'.join(url_path_from)
        if url_path_from == 'tasks':
            url_path_from = 'tasks:index'
        ca = ShowArchived.objects.get(user=request.user.id)
        if not ca.show_archived:
            ca.show_archived = True
        else:
            ca.show_archived = False;
        ca.save()
    return HttpResponseRedirect(reverse(url_path_from))


def delete_task(request):
    url_path_from = 'tasks:list'
    if request.method == 'POST':
        task_id = request.POST['task_id']
        try:
            task = Task.objects.get(pk=task_id)
        except Http404:
            return HttpResponseRedirect(reverse(url_path_from))
        task.delete()
        return HttpResponseRedirect(reverse(url_path_from))


def add_category(request):
    if request.method == 'POST':
        category = Category()
        category.name = request.POST['name']
        category.user = request.POST['user']
        category.save()
    return HttpResponse("add_category")


def delete_category(request):
    if request.method == 'POST':
        id = request.POST['id']
        category = Category.objects.get(pk=id)
        category.delete()
    return HttpResponse("delete_category")


@login_required
def index(request):
    if request.user.is_authenticated:
        tasks = {
            'tasks': Task.objects.order_by('-end_time')
        }
        context = {**tasks, **progress(request)}
    else:
        context = {'tasks': []}
    return render(request, 'tasks/landing.html', context)


@require_POST
@csrf_exempt
def move_date_backward(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id', default=-1)
        try:
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return HttpResponse("ObjectDoesNotExist:task_move_date_backward")
        task.end_time -= datetime.timedelta(days=1)
        task.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_POST
@csrf_exempt
def move_date_forward(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id', default=-1)
        try:
            task = Task.objects.get(pk=task_id)
        except ObjectDoesNotExist:
            return HttpResponse("ObjectDoesNotExist:task_move_date_forward")
        task.end_time += datetime.timedelta(days=1)
        task.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


'''
def sort_tasks(request):
    if(request.method == 'GET'):
        sort_key = request.GET["sort_by"]
        ordered_tasks = Task.objects.all().order_by('-'+sort_key).reverse()
        return render(request, 'tasks/task_list.html', {'task_list':ordered_tasks, 'fields':[field.name for field in Task._meta.get_fields()]})
        #return HttpResponseRedirect(reverse('tasks:index', kwargs={'task_list':ordered_tasks, 'fields':[field.name for field in Task._meta.get_fields()]}))
    return HttpResponseRedirect(reverse('tasks:index'))
'''


def filter_tasks(request):
    if (request.method == 'POST'):
        form = FilterForm(request.POST)
        field_names = remove_omitted_fields()
        if form.is_valid():
            user_id = request.POST['user']
            check_values = request.POST.getlist('tag[]')
            filter_key = request.POST['filter_key']
            if filter_key.strip() == '':
                return render(request, 'tasks/task_list.html',
                              {'task_list': Task.objects.filter(user=user_id, archived=False).all(),
                               'fields': field_names})
            else:
                filtered_tasks = Task.objects.none()
                for val in check_values:
                    arg_dict = {field_names[int(val)][1] + '__icontains': filter_key}
                    filtered_tasks = filtered_tasks | Task.objects.filter(user=user_id, archived=False).all().filter(
                        **arg_dict)
                return render(request, 'tasks/task_list.html',
                              {'task_list': filtered_tasks.order_by('end_time', 'created_at'), 'fields': field_names})
        elif 'reset-button' in request.POST:
            return HttpResponseRedirect(reverse('tasks:list'))
        else:
            return HttpResponseRedirect(reverse('tasks:list'))


def archive_finished(request):
    if request.user.is_authenticated:
        Task.objects.filter(user=request.user.id,
                            completed=True).update(archived=True, date_completed=datetime.datetime.now())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def get_pie(request):
    if 'pie_category' not in request.GET or request.GET['pie_category'] == 'all':
        pie_data = [['Task Type', "Completed"]]
        non_zero = False
        for cat in ['Homework', 'Chore', 'Work', 'Errand', 'Lifestyle', 'Others']:
            num_completed = len(Task.objects.filter(user=request.user.id, completed=True, category=cat))
            pie_data.append([cat, num_completed])
            non_zero = (num_completed > 0) or non_zero
        if non_zero:
            pie = PieChart(SimpleDataSource(pie_data),
                           options={'title': 'Tasks Completed by Category', 'width': 400}).as_html()
        else:
            pie = "No completed tasks to display."
    else:
        pie_data = [["Task Status", "Count"]]
        num_completed = len(
            Task.objects.filter(user=request.user.id, completed=True, category=request.GET['pie_category']))
        num_uncompleted = len(
            Task.objects.filter(user=request.user.id, completed=False, category=request.GET['pie_category']))
        completed_late = len(
            Task.objects.filter(user=request.user.id, completed=True, date_completed__gt=F('end_time'),
                                category=request.GET['pie_category']))
        uncompleted_late = len(Task.objects.filter(user=request.user.id, end_time__lt=datetime.datetime.now(),
                                                   date_completed__isnull=True, category=request.GET['pie_category']))
        pie_data.append(['Completed On-time', num_completed - completed_late])
        pie_data.append(['Completed Late', completed_late])
        pie_data.append(['Uncompleted & On-time', num_uncompleted - uncompleted_late])
        pie_data.append(['Uncompleted & Late', uncompleted_late])
        non_zero = (num_completed > 0) or (num_uncompleted > 0) or (completed_late > 0) or (uncompleted_late > 0)
        if non_zero:
            pie = PieChart(SimpleDataSource(pie_data),
                           options={'title': request.GET['pie_category'] + " On-Time Completion Rate",
                                    'width': 400}).as_html()
        else:
            pie = "No completed tasks to display for the " + request.GET['pie_category'].lower() + " category."
    return pie


# Below are two methods that help with constructing the line graph
def retrieve_line_data(data, field, request, weeks=2, index=1):
    if field == 'all':
        recentTasks = Task.objects.filter(user=request.user.id, completed=True,
                                          date_completed__gt=datetime.datetime.now() - datetime.timedelta(
                                              weeks=weeks)).annotate(
            date_only=Cast('date_completed', DateField())).values(
            'date_only').annotate(total=Count('date_only')).order_by('date_only')
    else:
        recentTasks = Task.objects.filter(user=request.user.id, completed=True, category=field,
                                          date_completed__gt=datetime.datetime.now() - datetime.timedelta(
                                              weeks=weeks)).annotate(
            date_only=Cast('date_completed', DateField())).values(
            'date_only').annotate(total=Count('date_only')).order_by('date_only')
    i = 1
    for dates in recentTasks:
        while data[i][0] != dates['date_only']:
            i += 1
        data[i][index] += int(dates['total'])
        i += 1


def init_dates(data, fields, weeks=2):
    start = datetime.datetime.now().date() - datetime.timedelta(weeks=weeks)
    data += [[start + datetime.timedelta(days=i)] for i in range((7 * weeks) + 1)]
    for i in range(1, len(data)):
        data[i] += [0 for i in range(fields)]


# This helper function contstructs the context for the StatsView
def stats(request):
    data = [
        ['Date']
    ]
    if Task.objects.filter(user=request.user.id):
        if not request.GET:
            data[0].append('Tasks Completed')
            init_dates(data, 1)
            retrieve_line_data(data, 'all', request)
            # A counter to keep track of where in the date array we are
        else:
            cntr = 1
            weeks = 2
            if 'weeks' in request.GET.keys():
                weeks = int(request.GET['weeks'])
            if 'category' in request.GET:
                num_fields = len(request.GET.getlist('category'))
                init_dates(data, num_fields, weeks)
                for field in request.GET.getlist('category'):
                    data[0].append(field)
                    retrieve_line_data(data, field, request, weeks, cntr)
                    cntr += 1
            else:
                num_fields = 1
                init_dates(data, num_fields, weeks)
                data[0].append('all')
                retrieve_line_data(data, 'all', request, weeks, cntr)
                cntr += 1
        pie = get_pie(request)
        recently_finished = SimpleDataSource(data)
        recently_finished_chart = LineChart(recently_finished, options={'title': 'Daily Tasks Completed', 'width': 600,
                                                                        'legend': {'position': 'bottom'},
                                                                        'vAxis': {'viewWindow': {'min': 0, 'max': 25},
                                                                                  'ticks': [i for i in
                                                                                            range(0, 26, 2)]}})
        completed = len(Task.objects.filter(user=request.user.id, completed=True))
        late = len(Task.objects.filter(user=request.user.id, date_completed__gt=F('end_time'))
                   | Task.objects.filter(user=request.user.id, end_time__lt=datetime.datetime.now(),
                                         date_completed__isnull=True))
        completed_late = len(
            Task.objects.filter(user=request.user.id, completed=True, date_completed__gt=F('end_time')))
        ratio_on_time = ((completed - completed_late) * 100) / max(late + completed - completed_late, 1)
        first_completed = Task.objects.all().aggregate(Min('date_completed'))[
            'date_completed__min']
        if first_completed:
            beginning_of_time = (datetime.datetime.now().date() - first_completed).days + 1
            avg = round((completed / max(beginning_of_time, 1)), 3)
        else:
            avg = 0
        context = {'chart': recently_finished_chart, 'completed': completed,
                   'ratio_on_time': round(ratio_on_time, 3),
                   'avg': avg, 'valid': '', 'show_bad_prompt': 'hidden', 'pie': pie, 'categories': Task.CATEGORIES}
        return context
    else:
        context = {'valid': 'hidden', 'show_bad_prompt': ''}
        return context


class StatsView(TemplateView):
    template_name = 'tasks/stats.html'

    def get_context_data(self, **kwargs):
        return stats(self.request)


def as_csv(request):
    if request.user.is_authenticated:
        user_task_records = Task.objects.filter(user=request.user.id).values(
            *[str(field.name) for field in Task._meta.get_fields() if field.name != "id" and field.name != "user"])
        return render_to_csv_response(user_task_records)
    else:
        raise Http404("No user found.")


class CalendarView(ListView):
    model = Task
    template_name = 'tasks/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('day', None))
        user = self.request.user.id
        cal = Calendar(d.year, d.month)
        html_cal = cal.formatmonth(withyear=True, user=user)
        if d.month < 12:
            cal_next = Calendar(d.year, d.month + 1)
        else:
            cal_next = Calendar(d.year + 1, 1)
        html_cal_next = cal_next.formatmonth(withyear=True, user=user)
        context['calendar'] = safestring.mark_safe(html_cal)
        context['calendar_next'] = safestring.mark_safe(html_cal_next)
        return context


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime.date(year, month, day=1)
    return datetime.datetime.today()


def progress(request):
    start_of_week = datetime.datetime.today() - datetime.timedelta(
        days=datetime.datetime.today().isoweekday() % 7)
    tasks_left_this_week = Task.objects.filter(user=request.user.id, completed=False,
                                               end_time__gte=start_of_week,
                                               end_time__lte=start_of_week + datetime.timedelta(days=6)
                                               )
    # print(tasks_left_this_week.values('hours').aggregate(total=Sum('hours')))
    estimated_hours = tasks_left_this_week.aggregate(total=Sum('hours'))['total']
    estimated_minutes = tasks_left_this_week.aggregate(total=Sum('minutes'))['total']
    if estimated_minutes and estimated_hours:
        estimated_hours += estimated_minutes // 60
        estimated_minutes %= 60
    else:
        estimated_hours = 0
        estimated_minutes = 0
    weekly = Task.objects.filter(completed=True).annotate(week=Extract('date_completed', 'week'),
                                                          year=Extract('date_completed', 'year')).values('year',
                                                                                                         'week').annotate(
        per_week=Count('week')).aggregate(avg=Avg('per_week'))
    tasks_done_this_week = Task.objects.filter(user=request.user.id, completed=True,
                                               date_completed__gte=start_of_week,
                                               date_completed__lte=start_of_week + datetime.timedelta(days=6)
                                               ).count()
    if weekly['avg'] < tasks_done_this_week:
        emoji = ':('
    elif weekly['avg'] == tasks_done_this_week:
        emoji = ': |'
    else:
        emoji = ':)'
    context = {'state': emoji, 'tasks_left': tasks_left_this_week.count(), 'est_hours': estimated_hours,
               'est_minutes': estimated_minutes}
    return context
