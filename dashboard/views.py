from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse



# Create your views here.


def home(request):
    return render(request, 'home.html')

def dashboard(request):
    return render(request, 'dashboard.html')
