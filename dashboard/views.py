from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
import datetime


# Create your views here.

class HomeView(generic.ListView):
    """
    Used to display the current tasks the user has assigned
    """
    template_name = 'home.html'
    #context_object_name = 'home'