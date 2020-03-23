from django.db import models
from social_django import models as oauth_models

# Create your models here.



class Task(models.Model):
    # These are the date formats that we attempt to parse
    attempt = ['%Y-%m-%d %H:%M:%S',  # '2006-10-25 14:30:59'
               '%Y-%m-%d %H:%M',  # '2006-10-25 14:30'
               '%Y-%m-%d',  # '2006-10-25'
               '%m/%d/%Y %H:%M:%S',  # '10/25/2006 14:30:59'
               '%m/%d/%Y %H:%M',  # '10/25/2006 14:30'
               '%m/%d/%Y',  # '10/25/2006'
               '%m/%d/%y %H:%M:%S',  # '10/25/06 14:30:59'
               '%m/%d/%y %H:%M',  # '10/25/06 14:30'
               '%m/%d/%y',
               '%Y-%m-%dT%H:%M']  # '10/25/06'
    #id = models.ForeignKey(oauth_models.uid, on_delete=models.CASCADE)
    user = models.IntegerField(default=-1)
    task_name = models.CharField(max_length=200)
    task_desc = models.CharField(max_length=400)
    start_time = models.DateTimeField('start time')
    end_time = models.DateTimeField('end time')
    completed = models.BooleanField('completed')
    link = models.URLField(default="")

    def __str__(self):
        return self.task_name
