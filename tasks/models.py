from django.db import models

# Create your models here.
class Task(models.Model):
    task_name = models.CharField(max_length=200)
    task_desc = models.CharField(max_length=400)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    def __str__(self):
        return self.task_name
