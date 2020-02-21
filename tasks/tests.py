from .models import Task
from django.test import TestCase, Client
from django.urls import reverse
from datetime import datetime


class TestCheck(TestCase):
    # Tests redirects for check off view
    def test_redirects(self):
        task = Task.objects.create(task_name='My test', task_desc='A test task', start_time=datetime(2012, 12, 20),
                                   end_time=datetime(2013, 1, 1), completed=False)
        task.save()
        resp = self.client.post('/tasks/check_off', {'task_id': task.id})
        self.assertEqual(resp.status_code, 301)
