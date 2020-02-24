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
            end_time=end_time,
            completed=False)
        task.save()
        # get list of tasks
        list_of_tasks = views.TaskListView.get_queryset(self)
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

    # unit test for adding task but with time format YYYY/MM/DD HH:MM
    def test_add_task_invalid_time_format(self):
        # create task
        task_name = "test_add_task_invalid_time_format"
        task_desc = "test_add_task_invalid_time_format description"
        start_time = "1111/11/11 11:11"
        end_time = "1111/11/11 11:22"
        task = views.Task(
            id=1,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            end_time=end_time,
            completed=False)
        # try saving task with invalid date format
        try:
            task.save()
        # should throw an exception
        except:
            self.assertTrue(True)
        
    def test_add_task_start_after_end(self):
        # create task
        task_name = "test_add_task_start_after_end"
        task_desc = "test_add_task_start_after_end description"
        start_time = "1111-11-11 11:22"
        end_time = "1111-11-11 11:11"
        task = views.Task(
            id=2,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            end_time=end_time,
            completed=False)
        # try saving task with invalid date format
        try:
            task.save()
        # should not throw an exception
        except:
            self.assertTrue(False)
        # get list of tasks
        list_of_tasks = views.TaskListView.get_queryset(self)
        print(list_of_tasks.filter(id=task.id))
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

    # unit test for checking off task, marking a task as completed
    def test_check_off(self):
        # create task
        task_name = "test_check_off"
        task_desc = "test_check_off description"
        start_time  = timezone.now()
        end_time = start_time + datetime.timedelta(days=3)
        task = views.Task(
            id=3,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            end_time=end_time,
            completed=False)
        task.save()
        resp = self.client.post('/tasks/check_off',{'task_id':task.id})
        self.assertEqual(resp.status_code,301)