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
    #path('delete_task', views.delete_task, name='delete_task'),
    #url(r'^sort_tasks/*', views.sort_tasks, name='sort_tasks'),
    path('delete_task/', views.delete_task, name='delete_task'),
    path('add_category/', views.add_category, name='add_category'),
    path('delete_category/', views.delete_category, name='delete_category'),
    path('filter_tasks/', views.filter_tasks, name='filter_tasks'),
    path('archive_finished/', views.archive_finished, name='archive_finished'),
    path('stats/', views.StatsView.as_view(), name='stats'),
    path('calendar/', views.CalendarView.as_view(), name='calendar'),
    path('archive_task/', views.archive_task, name='archive_task'),
    path('check_archived/', views.checkbox_archived, name='check_archived'),
    path('move_date_backward/', views.move_date_backward, name='move_date_backward'),
    path('move_date_forward/', views.move_date_forward, name='move_date_forward'),
]