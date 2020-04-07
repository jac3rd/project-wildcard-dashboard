from django.contrib.auth.decorators import login_required
from django.db.models import Count, F, Min
from django.db.models.functions import Cast
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from django.views.generic import TemplateView

from .forms import TaskForm, FilterForm
from .models import Task, Category
import datetime
from graphos.renderers.gchart import LineChart
from graphos.sources.model import SimpleDataSource
from django.db.models import DateField


# Create your views here.
class TaskListView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        # print('GET REQUEST: ', self.request.GET)
        sort_key = self.request.GET.get('sort_by', 'give-default-value')

        '''
        filter_key = self.request.GET.get('filter_key', 'default')
        filter_attr = self.request.GET.get('tag[]', 'default')
        if(filter_key != 'default'):
            pass
        '''

        if (sort_key != 'give-default-value'):
            return Task.objects.filter(user=self.request.user.id, archived=False).order_by('-' + sort_key).reverse()
        return Task.objects.filter(user=self.request.user.id, archived=False).order_by('end_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = []
        for field in Task._meta.get_fields():
            val = field.name
            if (val == 'id' or val == 'user'):
                continue
            elif ('_' in val):
                context['fields'].append((val.replace('_', ' '), val))
                continue
            else:
                context['fields'].append((val, val))
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
            t.category = request.POST.get('category')
            t.link = request.POST.get('link', "")
            # Ensure that the start dates are correct
            if t.end_time >= str(datetime.datetime.now()):
                t.completed = False
                t.save()
                if request.POST.get('repeat') == 'once':
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M')
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
                        curr_t.link = request.POST.get('link', "")
                        curr_t.completed = False
                        curr_t.user = request.POST.get('user')
                        curr_t.save()
                return HttpResponseRedirect(reverse('tasks:list'))
            else:
                return render(request, 'tasks/add_task.html',
                              {'form': form, 'error_message': "Due date must be later than current time.", })
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


def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
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
        field_names = []
        for field in Task._meta.get_fields():
            val = field.name
            if (val == 'id' or val == 'user'):
                continue
            elif ('_' in val):
                field_names.append((val.replace('_', ' '), val))
                continue
            else:
                field_names.append((val, val))

        if form.is_valid():
            check_values = request.POST.getlist('tag[]')
            filter_key = request.POST['filter_key']
            if (filter_key.strip() == ''):
                return render(request, 'tasks/task_list.html', {'task_list': Task.objects.all(), 'fields': field_names})
            else:
                arg_dict = {}
                filtered_tasks = Task.objects.none()
                for val in check_values:
                    # arg_dict[field_names[int(val)]+'__icontains'] = filter_key
                    arg_dict = {field_names[int(val)][1] + '__icontains': filter_key}
                    # print(arg_dict)
                    filtered_tasks = filtered_tasks | Task.objects.all().filter(**arg_dict)
                # filtered_tasks = Task.objects.all().filter(**arg_dict)
                # return HttpResponseRedirect(reverse('tasks:list'))
                return render(request, 'tasks/task_list.html', {'task_list': filtered_tasks, 'fields': field_names})
        else:
            print('nothing to ernder')
            return HttpResponseRedirect(reverse('tasks:list'))


def archive_finished(request):
    if request.user.is_authenticated:
        Task.objects.filter(user=request.user.id,
                            completed=True).update(archived=True, date_completed=datetime.datetime.now())
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


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
    data += [[start + datetime.timedelta(days=i)] for i in range((7*weeks) + 1)]
    for i in range(1, len(data)):
        data[i] += [0 for i in range(fields)]


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
            num_fields = len(request.GET.keys())
            weeks = 2
            if 'weeks' in request.GET.keys():
                print(int(request.GET['weeks']))
                weeks = int(request.GET['weeks'])
                num_fields -= 1
            init_dates(data, num_fields, weeks)
            for field in request.GET.keys():
                if request.GET[field] == 'on' and field != 'weeks':
                    data[0].append(field)
                    retrieve_line_data(data, field, request, weeks, cntr)
                    cntr += 1
        recently_finished = SimpleDataSource(data)
        recently_finished_chart = LineChart(recently_finished, options={'title': 'Task Completion Graph'})
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
                   'avg': avg, 'valid': '', 'show_bad_prompt': 'hidden'}
        return context
    else:
        context = {'valid': 'hidden', 'show_bad_prompt': ''}
        return context


class StatsView(TemplateView):
    template_name = 'tasks/stats.html'

    def get_context_data(self, **kwargs):
        return stats(self.request)