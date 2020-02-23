import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
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

class TestCheck(TestCase):
    # Tests redirects for check off view
    def test_redirects(self):
        task = models.Task.objects.create(task_name='My test', task_desc='A test task', start_time=datetime(2012, 12, 20),
                                   end_time=datetime(2013, 1, 1), completed=False)
        task.save()
        resp = self.client.post('/tasks/check_off', {'task_id': task.id})
        self.assertEqual(resp.status_code, 301)
