from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
import datetime
from .forms import TaskForm
from .models import Task


# Create your views here.

class TaskListView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'tasks/index.html'
    context_object_name = 'task_list'

    def get_queryset(self):
        return Task.objects.order_by('start_time')


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
            t.task_name = request.POST['task_name']
            t.task_desc = request.POST['task_desc']
            t.start_time = request.POST['start_time']
            t.end_time = request.POST['end_time']
            # Ensure that the start dates are correct
            if t.start_time < t.end_time:
                t.completed = False
                t.save()
                return HttpResponseRedirect(reverse('tasks:index'))
    else:
        form = TaskForm()
    return render(request, 'tasks/add_task.html', {'form': form})


def check_off(request):
    if request.method == 'POST':
        print(request.POST)
        task_id = request.POST['task_id']
        task = Task.objects.get(pk=task_id)
        task.completed = True
        task.save()
    return HttpResponseRedirect(reverse('tasks:index'))

def index(request):
    context = {
        'tasks': Task.objects.order_by('-date')
        if request.user.is_authenticated else []
    }

    return render(request, 'tasks/index.html', context)