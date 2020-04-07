from django.db import models
from social_django import models as oauth_models
import datetime
from django.urls import reverse


# Create your models here.

class Task(models.Model):
	user = models.IntegerField(default=-1)
	task_name = models.CharField(max_length=200)
	task_desc = models.CharField(max_length=400)
	end_time = models.DateTimeField('end time')
	length = models.DurationField('length', default=datetime.timedelta(hours=3))
	completed = models.BooleanField('completed')
	date_completed = models.DateField('date_completed', null=True)
	archived = models.BooleanField('archived', default=False)
	link = models.URLField(default="")
	HOMEWORK = 'Homework'
	CHORE = 'Chore'
	WORK = 'Work'
	ERRAND = 'Errand'
	LIFESTYLE = 'Life'
	OTHERS = 'Other'
	CATEGORIES = [
		(HOMEWORK, 'Homework'),
		(CHORE, 'Chore'),
		(WORK, 'Work'),
		(ERRAND, 'Errand'),
		(LIFESTYLE, 'Lifestyle'),
		(OTHERS, 'Others'),
	]
	category = models.CharField(
		null=True,
		blank=True,
		choices=CATEGORIES,
		max_length=32,
	)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return self.task_name

	@property
	def get_html_url(self):
		# url = reverse('task_edit', args=(self.id))
		# return f'<p>{self.task_name}</p><a href="{url}">edit</a>'
		return f'<p>{self.task_name}</p><a href="#">edit</a>'

class Category(models.Model):
    name = models.CharField(max_length=32)
    user = models.IntegerField()


# class Level(models.Model):
# 	level = models.IntegerField(default=1)
# 	xp = models.IntegerField(default=0)
#     user = models.IntegerField(primary_key=True)
