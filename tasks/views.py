from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from .forms import TaskForm
from .models import Task

# Create your views here.

class TaskListView(generic.ListView):
    template_name = 'tasks/index.html'
    context_object_name = 'task_list'
    def get_queryset(self):
        return Task.objects.order_by('start_time')

def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            t = Task()
            t.task_name = request.POST['task_name']
            t.task_desc = request.POST['task_desc']
            t.start_time = request.POST['start_time']
            t.end_time = request.POST['end_time']
            t.completed = False
            t.save()
            return HttpResponseRedirect(reverse('tasks:index'))
        else:
            form = TaskForm()
        return render(request, 'tasks/index.html', {'form':form})