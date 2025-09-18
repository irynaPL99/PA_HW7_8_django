# manager_tasks/urls.py
from django.urls import path
from .views import create_task, get_all_tasks, get_task_detail, get_task_statistic

urlpatterns = [
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/',get_all_tasks, name='all_tasks'),
    path('tasks/<int:pk>/', get_task_detail, name='task_detail'),
    path('tasks/statistic/', get_task_statistic, name='task_statistic'),
]