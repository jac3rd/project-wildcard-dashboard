from django import forms

class TaskForm(forms.Form):
    task_name = forms.CharField(label='Task Name', max_length=100)
    task_desc = forms.CharField(label='Task Description', max_length=200)
    start_time = forms.DateTimeField(label='Start Time')
    end_time = forms.DateTimeField(label='End Time')