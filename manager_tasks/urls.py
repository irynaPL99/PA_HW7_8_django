# manager_tasks/urls.py
from django.urls import path
from .views import get_task_statistic
from .views import get_all_categories, create_category, update_category
#from .views import create_subtask # hw12 -> hw15
from .views import SubTaskListCreateView, SubTaskDetailUpdateDeleteView # hw13  APIView->hw15 Generic View
from .views import get_subtasks_by_task_and_status #hw14
from .views import TaskListCreateView, TaskDetailUpdateDeleteView #hw15  Generic View
urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='all_tasks'), # Generic View(GET, POST)
    path('tasks/<int:pk>/', TaskDetailUpdateDeleteView.as_view(), name='task_detail'),
    path('tasks/statistic/', get_task_statistic, name='task_statistic'),

    #Пример: GET /tasks/?status=NEW&search=project&ordering=-created_at.

    # subtasks:
    path('subtasks/', SubTaskListCreateView.as_view(), name='list_create_subtask'), # hw13,15 (get,post)
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='detail_update_delete_subtask'), #hw13,15
    path('subtasks/filter/', get_subtasks_by_task_and_status, name='filter_by_task_and_status'), #hw14

    #Пример: GET /subtasks/?status=NEW&search=задача&ordering=-created_at

    # categories:
    path('categories/', get_all_categories, name='all_categories'),
    path('categories/create/', create_category, name='create_category'),
    path('categories/<int:pk>/', update_category, name='update_category'),
]