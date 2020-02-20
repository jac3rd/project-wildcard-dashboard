import datetime
from django.test import TestCase
from django.utils import timezone
from . import models, views

# Create your tests here.
class TaskModelTests(TestCase):

    # unit test for successfully adding generic task
    def test_add_task(self):
        # create task
        task_name = "test_add_task"
        task_desc = "test_add_task description"
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(days=3)
        task = views.Task(
            id=0,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            attempt = [start_time],
            end_time=end_time)
        task.save()
        # get list of tasks
        list_of_tasks = views.TaskListView.get_queryset()
        self.assertIs(list_of_tasks.contains(task), True)