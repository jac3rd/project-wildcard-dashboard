from django.db import models
from social_django import models as oauth_models
from django.utils import timezone
import datetime

# Create your models here.

class Task(models.Model):
	user = models.IntegerField(default=-1)
	task_name = models.CharField(max_length=200)
	task_desc = models.CharField(max_length=400)
	due_date = models.DateTimeField(default=timezone.now)
	length = models.DurationField(default=datetime.timedelta(days=3))
	completed = models.BooleanField('completed')
	link = models.URLField(default="")
	HOMEWORK = 'hw'
	CHORE = 'chore'
	WORK = 'work'
	ERRAND = 'errand'
	LIFESTYLE = 'life'
	OTHERS = 'others'
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

class Category(models.Model):
	name = models.CharField(max_length=32)
	user = models.IntegerField()