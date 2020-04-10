from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Min
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist

from .forms import TaskForm, FilterForm
from .models import Task, Category, ShowArchived
import datetime
from graphos.renderers.gchart import LineChart, PieChart
from graphos.sources.model import SimpleDataSource
from django.db.models import DateField
from django.utils import timezone


def remove_omitted_fields():
    omitted_fields = set(['id', 'user', 'created_at', 'completed', 'archived'])
    l = []
    for field in Task._meta.get_fields():
        val = field.name
        if (val in omitted_fields):
            continue
        elif ('_' in val):
            l.append((val.replace('_', ' '), val))
            continue
        else:
            l.append((val, val))
    return l


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
            if self.request.user.is_authenticated == True:
                show_arch = ShowArchived.objects.get(user=self.request.user.id).show_archived
            else:
                return render(self.request, 'tasks/login.html')
        except:
            sa = ShowArchived()
            #sa.show_archived = False;
            sa.user = self.request.user.id
            sa.save()

        if (sort_key != 'give-default-value' and not show_arch):
            return Task.objects.filter(user=self.request.user.id, archived=False).order_by(sort_key, 'created_at')
        elif (sort_key != 'give-default-value' and show_arch):
            return Task.objects.filter(user=self.request.user.id).order_by(sort_key, 'created_at')
        elif (sort_key == 'give-default-value' and not show_arch):
            return Task.objects.filter(user=self.request.user.id, archived=False).order_by('end_time', 'created_at')
        else:
            return Task.objects.filter(user=self.request.user.id).order_by('end_time', 'created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = remove_omitted_fields()
        if self.request.user.is_authenticated == True:
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
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M')
                        curr_t.hours = request.POST.get('hours')
                        curr_t.minutes = request.POST.get('minutes')
                        curr_t.user = request.POST.get('user')
                        curr_t.completed = False
                        curr_t.link = request.POST.get('link', "")
                        curr_t.category = request.POST.get('category')
                        curr_t.save()
                if request.POST.get('repeat') == 'weekly':
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=i)
                        curr_t.hours = request.POST.get('hours')
                        curr_t.minutes = request.POST.get('minutes')
                        curr_t.user = request.POST.get('user')
                        curr_t.completed = False
                        curr_t.link = request.POST.get('link', "")
                        curr_t.save()
                elif request.POST.get('repeat') == 'monthly':
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=4 * i)
                        curr_t.hours = request.POST.get('hours')
                        curr_t.minutes = request.POST.get('minutes')
                        curr_t.link = request.POST.get('link', "")
                        curr_t.completed = False
                        curr_t.user = request.POST.get('user')
                        curr_t.save()
                elif request.POST.get('repeat') == 'annually':
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=52 * i)
                        curr_t.hours = request.POST.get('hours')
                        curr_t.minutes = request.POST.get('minutes')
                        curr_t.link = request.POST.get('link', "")
                        curr_t.completed = False
                        curr_t.user = request.POST.get('user')
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
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.completed = True
        task.date_completed = datetime.datetime.now().date()
        task.save()
    return HttpResponseRedirect(reverse('tasks:list'))


def uncheck(request):
    """
    This allows a mistakenly checked off task to be marked as uncompleted.
    :param request: A request that contains a primary key for the task being unmarked.
    :return: A redirect to our index page for tasks.
    """
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.completed = False
        task.save()
    return HttpResponseRedirect(reverse('tasks:list'))

def archive_task(request):
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        if task.archived == False:
            task.archived = True
        else:
            task.archived = False
        task.save()
    return HttpResponseRedirect(reverse('tasks:list'))

def checkbox_archived(request):
    """
        This allows a user to see his/her archived tasks.
    """
    if request.method == 'POST':
        ca = ShowArchived.objects.get(user=request.user.id)
        if ca.show_archived == False:
            ca.show_archived = True
        else:
            ca.show_archived = False;
        ca.save()
    return HttpResponseRedirect(reverse('tasks:list'))

def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST['task_id']
        try:
            task = Task.objects.get(pk=task_id)
        except:
            return HttpResponseRedirect(reverse('tasks:list'))
        task.delete()
        return HttpResponseRedirect(reverse('tasks:list'))


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
    context = {
        'tasks': Task.objects.order_by('-date')
        if request.user.is_authenticated else []
    }

    return render(request, 'tasks/task_list.html', context)


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
            # print('valid form')
            user_id = request.POST['user']
            check_values = request.POST.getlist('tag[]')
            filter_key = request.POST['filter_key']
            if (filter_key.strip() == ''):
                return render(request, 'tasks/task_list.html',
                              {'task_list': Task.objects.filter(user=user_id, archived=False).all(),
                               'fields': field_names})
            else:
                arg_dict = {}
                filtered_tasks = Task.objects.none()
                for val in check_values:
                    # arg_dict[field_names[int(val)]+'__icontains'] = filter_key
                    arg_dict = {field_names[int(val)][1] + '__icontains': filter_key}
                    # print(arg_dict)
                    filtered_tasks = filtered_tasks | Task.objects.filter(user=user_id, archived=False).all().filter(
                        **arg_dict)
                # filtered_tasks = Task.objects.all().filter(**arg_dict)
                # return HttpResponseRedirect(reverse('tasks:list'))
                return render(request, 'tasks/task_list.html', {'task_list': filtered_tasks, 'fields': field_names})
        elif 'reset-button' in request.POST:
            # print('reset filter')
            return HttpResponseRedirect(reverse('tasks:list'))
        else:
            # print('invalid form')
            return HttpResponseRedirect(reverse('tasks:list'))


def archive_finished(request):
    if request.user.is_authenticated:
        Task.objects.filter(user=request.user.id,
                            completed=True).update(archived=True, date_completed=datetime.datetime.now())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
        recently_finished = SimpleDataSource(data)
        recently_finished_chart = LineChart(recently_finished, options={'title': 'Daily Tasks Completed', 'width': 600,
                                                                        'legend': {'position': 'bottom'},
                                                                        'vAxis': {'viewWindow': {'min': 0, 'max': 25},
                                                                                  'ticks': [i for i in range(0, 26, 2)]}})
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
