import datetime
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone
from django.urls import reverse
from . import models, views
from django.contrib.auth.models import User

def create_task(user=0, task_name="generic test", task_desc="generic test description", start_time=timezone.now(), end_time=timezone.now() +  datetime.timedelta(days=1), completed=False, category=""):
    task = models.Task(
        user=user,
        task_name=task_name,
        task_desc=task_desc,
        start_time=start_time,
        end_time=end_time,
        completed=completed,
        category=category)
    task.save()
    return task

# Create your tests here.
class TaskModelTests(TestCase):
    
    # unit test for successfully adding generic task
    def test_add_task_once(self):
        # create task
        task_name = "test_add_task"
        task_desc = "test_add_task description"
        task = create_task(user=1, task_name=task_name, task_desc=task_desc)
        # get list of tasks
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

        # unit test for successfully adding generic task

    def test_add_task_start_after_end(self):
        # create task
        task_name = "test_add_task_start_after_end"
        task_desc = "test_add_task_start_after_end description"
        start_time = timezone.now()
        end_time = start_time - datetime.timedelta(days=3)
        task = create_task(user=3, task_name=task_name, task_desc=task_desc, start_time=start_time, end_time=end_time)
        # try saving task with invalid dates, but directly to database, not from view
        try:
            task.save()
        # should not throw an exception
        except:
            self.assertTrue(False)
        # get list of tasks
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.filter(id=task.id).exists(), True)

    # unit test for checking off task, marking a task as completed
    def test_check_off(self):
        # create task
        task_name = "test_check_off"
        task_desc = "test_check_off description"
        task = create_task(user=4, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post('/tasks/check_off', {'task_id': task.id})
        self.assertEqual(resp.status_code, 301)

    # unit test asserting that uncheck marks task as not completed
    def test_uncheck(self):
        # create task
        task_name = "test_checked"
        task_desc = "test_checked description"
        task = create_task(user=2, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post('/tasks/uncheck', {'task_id': task.id})
        self.assertEqual(resp.status_code, 301)
        list_of_tasks = models.Task.objects
        # Check to make sure it is not set to completed
        self.assertIs(list_of_tasks.filter(id=task.id, completed=True).exists(), False)

    # unit test asserting that delete_task removes task from database
    def test_delete_task(self):
        # create task
        task_name = "test_delete_task"
        task_desc = "test_delete_task description"
        task = create_task(user=10, task_name=task_name, task_desc=task_desc)
        task.save()
        self.client.post('/tasks/delete_task', {'task_id': task.id})
        list_of_tasks = models.Task.objects
        self.assertFalse(list_of_tasks.filter(id=task.id).exists())

    # unit test asserting that delete_task redirects the user
    def test_delete_task_redirect(self):
        # create task
        task_name = "test_delete_task_redirect"
        task_desc = "test_delete_task_redirect description"
        task = create_task(user=8, task_name=task_name, task_desc=task_desc)
        task.save()
        resp = self.client.post('/tasks/delete_task',{'task_id':task.id})
        self.assertEqual(resp.status_code,302)

    # unit test asserting that add_task_category saves the category field to a task
    def test_add_task_category(self):
        # create task
        task_name = "test_add_task_category"
        task_desc = "test_add_task_category description"
        category = "Homework"
        task = create_task(task_name=task_name, task_desc=task_desc, category=category)
        task.save()
        list_of_tasks = models.Task.objects
        self.assertIs(list_of_tasks.get(id=task.id).category == category, True)