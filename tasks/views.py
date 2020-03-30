from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from .forms import TaskForm
from .models import Task, Category
import datetime


# Create your views here.
class TaskListView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'tasks/task_list.html'
    context_object_name = 'task_list'


    def get_queryset(self):
        print('GET REQUEST: ', self.request.GET)
        sort_key = self.request.GET.get('sort_by', 'give-default-value')
        if(sort_key == 'give-default-value'):
            return Task.objects.order_by('start_time')
        return Task.objects.order_by('-'+sort_key).reverse()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fields'] = [field.name for field in Task._meta.get_fields()]
        #context['fields'] = ['asdfasdf', 'sadfasfasd', 'asdfasf']
        #print(context)
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
            t.start_time = request.POST.get('start_time')
            t.end_time = request.POST.get('end_time')
            t.category = request.POST.get('category')
            t.link = request.POST.get('link', "")
            # Ensure that the start dates are correct
            if t.start_time < t.end_time:
                t.completed = False
                t.save()
                if request.POST.get('repeat') == 'once':
                    for i in range(1, int(request.POST['times']) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M')
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M')
                        curr_t.user = request.POST.get('user')
                        curr_t.completed = False
                        curr_t.link = request.POST.get('link', "")
                        curr_t.save()
                if request.POST.get('repeat') == 'weekly':
                    for i in range(1, int(request.POST.get('times')) + 1):
                        curr_t = Task()
                        curr_t.task_name = request.POST.get('task_name')
                        curr_t.task_desc = request.POST.get('task_desc')
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=i)
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
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=4 * i)
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
                        curr_t.start_time = datetime.datetime.strptime(t.start_time,
                                                                       '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=52 * i)
                        curr_t.end_time = datetime.datetime.strptime(t.end_time, '%Y-%m-%dT%H:%M') + datetime.timedelta(
                            weeks=52 * i)
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
        task.save()
    return HttpResponseRedirect(reverse('tasks:index'))


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
    if(request.method == 'POST'):
        form = TaskForm(request.POST)
        field_names = [field.name for field in Task._meta.get_fields()]
        if form.is_valid():
            check_values = request.POST.getlist('tag[]')
            filter_key = request.POST['filter_key']
            print('VALID', request.POST['filter_key'], check_values)

            #return HttpResponseRedirect(reverse('tasks:list'))
            return render(request, 'tasks/task_list.html', {'task_list':filtered_tasks, 'fields':field_names})
        else:
            check_values = request.POST.getlist('tag[]')
            filter_key = request.POST['filter_key']
            print('NOT VALID', request.POST['filter_key'], check_values)
            
            arg_dict = {}
            filtered_tasks = Task.objects.all().filter()
            for val in check_values:
                arg_dict[field_names[int(val)]+'__icontains'] = filter_key
                #filtered_tasks = Task.objects.all().filter(task_name__icontains=filter_key)
            filtered_tasks = Task.objects.all().filter(**arg_dict)

            #return HttpResponseRedirect(reverse('tasks:list'))
            return render(request, 'tasks/task_list.html', {'task_list':filtered_tasks, 'fields':field_names})