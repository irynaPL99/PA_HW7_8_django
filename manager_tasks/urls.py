# manager_tasks/urls.py
from django.urls import path
from .views import create_task, get_all_tasks, get_task_detail, get_task_statistic
from .views import get_all_categories, create_category, update_category
#from .views import create_subtask # hw12
from .views import SubTaskListCreateView, SubTaskDetailUpdateDeleteView # hw13
from .views import get_subtasks_by_task_and_status #hw14

urlpatterns = [
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/',get_all_tasks, name='all_tasks'),
    path('tasks/<int:pk>/', get_task_detail, name='task_detail'),
    path('tasks/statistic/', get_task_statistic, name='task_statistic'),

    # subtasks:
    #path('subtasks/create/', create_subtask, name='create_subtask'),   # hw12
    path('subtasks/', SubTaskListCreateView.as_view(), name='list_create_subtask'), # hw13 (get,post)
    # *.as_view() - преобразует класс представления в функцию
    # представления, которая может быть использована в маршруте
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='detail_update_delete_subtask'),
    path('subtasks/filter/', get_subtasks_by_task_and_status, name='filter_by_task_and_status'), #14


    # categories:
    path('categories/', get_all_categories, name='all_categories'),
    path('categories/create/', create_category, name='create_category'),
    path('categories/<int:pk>/', update_category, name='update_category'),
]