from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
import datetime


# Create your views here.

def home(request):
    return render(request, 'home.html', {})