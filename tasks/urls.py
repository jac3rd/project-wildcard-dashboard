from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'tasks'
urlpatterns = [
    path('', views.TaskListView.as_view(), name='index'),
    path('list/', views.TaskListView.as_view(), name='list'),
    path('add_task/', views.add_task, name='add_task'),
    path('check_off/', views.check_off, name='check_off'),
    path('uncheck/', views.uncheck, name='uncheck'),
    path('delete_task', views.delete_task, name='delete_task'),
    #url(r'^sort_tasks/*', views.sort_tasks, name='sort_tasks'),
    path('delete_task/', views.delete_task, name='delete_task'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('filter_tasks/', views.filter_tasks, name='filter_tasks'),
]