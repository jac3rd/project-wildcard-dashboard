"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from tasks import views as task_views
from django.conf import settings
from dashboard import views

urlpatterns = [
    path('tasks/', include('tasks.urls')),
    path('admin/', admin.site.urls),
    path('social/', include('social_django.urls', namespace='social')),
    url('login/', auth_views.LoginView.as_view(), name='login'),
    url('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('add_task/', task_views.add_task, name='add_task'),
    path('dashboard/', views.dashboard, name = 'dashboard'),
    path('', views.home, name='index'),
]
