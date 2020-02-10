from django.shortcuts import render
from django.views import generic
from .models import Task

# Create your views here.

class Task_ListView(generic.ListView):
    template_name = 'tasks/index.html'
    context_object_name = 'task_list'
    def get_queryset(self):
        return Task.objects.order_by('start_date')