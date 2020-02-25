from django.urls import path

from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.TaskListView.as_view(), name='index'),
    path('add_task/', views.add_task, name='add_task'),
    path('check_off/', views.check_off, name='check_off'),
    path('delete_task', views.delete_task, name='delete_task'),
]