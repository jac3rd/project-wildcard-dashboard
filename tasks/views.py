from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from .forms import TaskForm
from .models import Task
import datetime


# Create your views here.
class TaskListView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user.id).order_by('-start_time')


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
            t.user = request.POST['user']
            t.task_name = request.POST['task_name']
            t.task_desc = request.POST['task_desc']
            t.start_time = request.POST['start_time']
            t.end_time = request.POST['end_time']
            t.link = request.POST.get('link', "")
            # Ensure that the start dates are correct
            if t.start_time < t.end_time:
                t.completed = False
                t.save()
                if request.POST['repeat'] == 'weekly':
                    for i in range(1, int(request.POST['times']) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST['task_name']
                        curr_t.task_desc = request.POST['task_desc']
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=i)
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=i)
                        curr_t.user = request.POST['user']
                        curr_t.completed = False
                        curr_t.link = request.POST.get('link', "")
                        curr_t.save()
                elif request.POST['repeat'] == 'monthly':
                    for i in range(1, int(request.POST['times']) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST['task_name']
                        curr_t.task_desc = request.POST['task_desc']
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=4 * i)
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=4 * i)
                        curr_t.link = request.POST.get('link', "")
                        curr_t.completed = False
                        curr_t.user = request.POST['user']
                        curr_t.save()
                elif request.POST['repeat'] == 'annually':
                    for i in range(1, int(request.POST['times']) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST['task_name']
                        curr_t.task_desc = request.POST['task_desc']
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=52 * i)
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=52 * i)
                        curr_t.link = request.POST.get('link', "")
                        curr_t.completed = False
                        curr_t.user = request.POST['user']
                        curr_t.save()
                return HttpResponseRedirect(reverse('tasks:list'))
    else:
        form = TaskForm()
    return render(request, 'tasks/add_task.html', {'form': form})


def calendar(request):
    return render(request, 'tasks/calendar.html')


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
    return HttpResponseRedirect(reverse('tasks:index'))


def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.delete()
    return HttpResponseRedirect(reverse('tasks:index'))


@login_required
def index(request):
    context = {
        'tasks': Task.objects.order_by('-date')
        if request.user.is_authenticated else []
    }

    return render(request, 'tasks/index.html', context)
