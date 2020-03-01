from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.TaskListView.as_view(), name='index'),
    path('list/', views.TaskListView.as_view(), name='list'),
    path('add_task/', views.add_task, name='add_task'),
    path('check_off/', views.check_off, name='check_off'),
]