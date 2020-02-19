from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from . import models

class TaskForm(forms.Form):
    #Reformats the html input to work with the django datetime field
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
    task_name = forms.CharField(label='Task Name', max_length=100)
    task_desc = forms.CharField(label='Task Description', max_length=200)
    start_time = forms.DateTimeField(label='Start Time', input_formats=attempt)
    end_time = forms.DateTimeField(label='End Time', input_formats=attempt)
