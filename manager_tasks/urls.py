# manager_tasks/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter   #hw16
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView #hw18 SimpleJWT
#from .views import get_task_statistic   #hw12->hw18
from .views import TaskStatisticView, MyTasksView  # hw18 permissions (TaskStatisticView), hw19 (owner, MyTasksView)
#from .views import get_all_categories, create_category, update_category -> CategoryViewSet (hw16 ModelViewSet)
#from .views import create_subtask # hw12 -> hw15
from .views import SubTaskListCreateView, SubTaskDetailUpdateDeleteView # hw13  APIView->hw15 Generic View
#from .views import get_subtasks_by_task_and_status #hw14->hw18
from .views import SubTaskStatisticView #hw18 permissions
from .views import TaskListCreateView, TaskDetailUpdateDeleteView #hw15  Generic View
from .views import CategoryViewSet #hw16 ModelViewSet
from .views import ProtectedDataView    #hw18 for testing SimpleJWT


router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category') #hw16
# exp: http://127.0.0.1:8000/api/v1/categories/


urlpatterns = [
    path('', include(router.urls)), #hw16, router
    path('tasks/', TaskListCreateView.as_view(), name='all_tasks'), # Generic View(GET, POST)
    path('tasks/<int:pk>/', TaskDetailUpdateDeleteView.as_view(), name='task_detail'),
    #path('tasks/statistic/', get_task_statistic, name='task_statistic'),   #hw12->hw18
    path('tasks/statistic/', TaskStatisticView.as_view(), name='task_statistic'),   #hw18 permissions

    #Пример: GET /tasks/?status=NEW&search=project&ordering=-created_at.

    # subtasks:
    path('subtasks/', SubTaskListCreateView.as_view(), name='list_create_subtask'), # hw13,15 (get,post)
    path('subtasks/<int:pk>/', SubTaskDetailUpdateDeleteView.as_view(), name='detail_update_delete_subtask'), #hw13,15
    #path('subtasks/filter/', get_subtasks_by_task_and_status, name='filter_by_task_and_status'), #hw14->hw18
    path('subtasks/filter/', SubTaskStatisticView.as_view(), name='filter_by_task_and_status'), #hw18 permissions

    #Пример: GET /subtasks/?status=NEW&search=задача&ordering=-created_at
    # http://127.0.0.1:8000/api/v1/subtasks/filter/?task_title=ДЗ&status=NEW
    path('my-tasks/', MyTasksView.as_view(), name='my_tasks'),  # hw19, owner

    # categories: -> router
    #path('categories/', get_all_categories, name='all_categories'),
    #path('categories/create/', create_category, name='create_category'),
    #path('categories/<int:pk>/', update_category, name='update_category'),

    #hw18 SimpleJWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedDataView.as_view(), name='protected_data'),
    # тестовый защищённый эндпоинт

]