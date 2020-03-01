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
        
    def test_add_task_start_after_end(self):
        # create task
        task_name = "test_add_task_start_after_end"
        task_desc = "test_add_task_start_after_end description"
        start_time = timezone.now()
        end_time = start_time - datetime.timedelta(days=3)
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


    def test_uncheck(self):
        # create task
        task_name = "test_checked"
        task_desc = "test_checked description"
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
        resp = self.client.post('/tasks/uncheck',{'task_id':task.id})
        self.assertEqual(resp.status_code,301)
        list_of_tasks = views.TaskListView.get_queryset(self)
        # Check to make sure it is not set to completed
        self.assertIs(list_of_tasks.filter(id=task.id, completed=True).exists(), False)

    def test_delete_task(self):
        # create task
        task_name = "test_delete_task"
        task_desc = "test_delete_task description"
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(days=3)
        task = views.Task(
            id=4,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            end_time=end_time,
            completed=False)
        task.save()
        self.client.post('/tasks/delete_task',{'task_id':task.id})
        list_of_tasks = views.TaskListView.get_queryset(self)
        self.assertFalse(list_of_tasks.filter(id=task.id).exists())

    def test_delete_task_redirect(self):
        # create task
        task_name = "test_delete_task"
        task_desc = "test_delete_task description"
        start_time = timezone.now()
        end_time = start_time + datetime.timedelta(days=3)
        task = views.Task(
            id=5,
            task_name=task_name,
            task_desc=task_desc,
            start_time=start_time,
            end_time=end_time,
            completed=False)
        task.save()
        resp = self.client.post('/tasks/delete_task',{'task_id':task.id})
        self.assertEqual(resp.status_code,302)