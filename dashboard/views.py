from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
import datetime
from django.contrib.auth.models import User

# Create your views here.

def home(request):
    print(User.objects.all())
    return render(request, 'home.html')