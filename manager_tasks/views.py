from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView    #hw13
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view  #hw12
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination  #hw14

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView # hw15
from django_filters.rest_framework import DjangoFilterBackend   #hw15
from rest_framework.filters import SearchFilter, OrderingFilter #hw15

from django.utils import timezone   #hw13
from django.db.models import Count  #hw12

from .serializers import TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer
from .serializers import TaskStatisticSerializer    #hw12
from .serializers import CategorySerializer, CategoryCreateSerializer
from .serializers import SubTaskCreateSerializer, SubTaskSerializer

from .models import Task, SubTask, Category


"""hw15:
create_task, get_all_tasks -> на Generic View: класс ListCreateAPIView,
get_task_detail -> на Generic View: класс TaskDetailUpdateDeleteView
"""
# hw15 Новый класс (Generic APIView) для создания и получения списка задач
class TaskListCreateView(ListCreateAPIView):
    """
    Получение списка задач (GET) и создание новой задачи (POST).
    Поддерживает фильтрацию, поиск и сортировку.
    """
    queryset = Task.objects.all()
    serializer_class = TaskListSerializer  # Для списка задач
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]  #hw15 Подключаем фильтры
    filterset_fields = ['status', 'deadline']  # Фильтрация
    search_fields = ['title', 'description']  # Поиск
    ordering_fields = ['created_at']  # Сортировка
    ordering = ['-created_at']  # Сортировка по умолчанию: от новых к старым

    # переопределение сериалайзера для POST-запросов
    def get_serializer_class(self):
        """Используем TaskCreateSerializer для POST-запросов (create task)."""
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """Поддержка фильтрации по дню недели, как в get_all_tasks."""
        queryset = super().get_queryset()
        weekday = self.request.query_params.get('weekday', None)
        if weekday:
            weekday_map = {
                'monday': 0,
                'tuesday': 1,
                'wednesday': 2,
                'thursday': 3,
                'friday': 4,
                'saturday': 5,
                'sunday': 6
            }
            weekday_num = weekday_map.get(weekday.lower())
            if weekday_num is None:
                raise ValidationError(
                    {'error': 'Invalid weekday. Use: monday, tuesday, wednesday, thursday, friday, saturday, sunday'}
                )
            queryset = queryset.filter(deadline__week_day=weekday_num + 1)
        return queryset

#hw15:  Новый класс (Generic APIView) для получения, обновления и удаления задачи по ID
class TaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Получение (GET), обновление (PUT) и удаление (DELETE) задачи по ID.
    """
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer  # Для детального отображения задачи

    # переопределение сериалайзера для PUT-запросов
    def get_serializer_class(self):
        """Используем TaskCreateSerializer для PUT-запросов (update task by id)."""
        if self.request.method in ['PUT', 'PATCH']:
            return TaskCreateSerializer
        return self.serializer_class

    # явно создаёт сериализатор с partial=True, что указывает REST Framework на то, что это частичное обновление,
    # и не все поля модели должны быть обязательными.
    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

"""hw12 Статистика по задачам
3.1 общее количество задач.
3.2 количество задач по каждому статусу.
3.3 количество просроченных задач.
"""
@api_view(['GET'])
def get_task_statistic(request):
    # 3.1 count Tasks
    total_tasks = Task.objects.count()

    # 3.2 aggregation by status
    tasks_by_status = Task.objects.values('status').annotate(cnt=Count('id')).order_by('status')
    status_dict =  {item['status']: item['cnt'] for item in tasks_by_status}

    # 3.3 deadline < now
    overdue_tasks = Task.objects.filter(deadline__lt=timezone.now()).count()

    statistic_data = {
        'total_tasks': total_tasks,
        'tasks_by_status': status_dict,
        'overdue_tasks': overdue_tasks
    }
    serializer = TaskStatisticSerializer(statistic_data)
    return Response(serializer.data, status=status.HTTP_200_OK)

"""hw13 """
@api_view(['GET'])
def get_all_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_category(request):
    serializer = CategoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['PUT']) # клиент отправляет все поля ресурса,
# и сервер заменяет существующий объект новыми данными.
# Если какого-то поля нет в запросе, оно обычно сбрасывается
# до значения по умолчанию или null (если разрешено)
#@api_view(['PATCH']) # для частичного обновления ресурса. Клиент отправляет только те поля,
# которые нужно изменить, а остальные остаются без изменений

@api_view(['PUT'])
def update_category(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategoryCreateSerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


"""hw14: 
получение списка всех подзадач по названию главной задачи и статусу подзадач
"""
@api_view(['GET'])
def get_subtasks_by_task_and_status(request):
    """
    Get all SubTasks filtered by main task title and/or subtask status, with pagination.
    """
    # Настройка пагинации (5 объектов на страницу, как в SubTaskListCreateView)
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5

    # Получаем параметры фильтрации из запроса
    task_title = request.query_params.get('task_title', None)
    status = request.query_params.get('status', None)

    # Базовый запрос для всех подзадач, отсортированных по убыванию даты создания
    subtasks = SubTask.objects.all().order_by('-created_at')

    # Применяем фильтры, если переданы параметры
    if task_title:
        subtasks = subtasks.filter(task__title__icontains=task_title)
        # 'task' - поле ForeignKey, связывающее её с моделью Task.
        # Двойное подчеркивание (__) используется в Django ORM для обращения к связанным моделям
        # в поле__title модели Task, '__icontains' - содержится(регистроНЕзависим.) название гл.задачи

    if status:
        subtasks = subtasks.filter(status__iexact=status)
        # _iexact обеспечивает регистроНЕзависимый поиск

    # Применяем пагинацию
    paginator = pagination_class()
    paginated_subtasks = paginator.paginate_queryset(subtasks, request)

    serializer = SubTaskSerializer(paginated_subtasks, many=True)
    # Возвращаем пагинированный ответ
    return paginator.get_paginated_response(serializer.data)


"""hw15: классы SubTaskListCreateView -> на Generic Views (ListCreateAPIView)
 SubTaskDetailUpdateDeleteView -> на Generic Views (RetrieveUpdateDestroyAPIView), 
 а также добавить фильтрацию, поиск и сортировку для SubTask
"""
# Класс для создания и получения списка подзадач
class SubTaskListCreateView(ListCreateAPIView):
    """
    Получение списка подзадач (GET) и создание новой подзадачи (POST).
    Поддерживает пагинацию, фильтрацию, поиск и сортировку.
    """
    queryset = SubTask.objects.all().order_by('-created_at')
    serializer_class = SubTaskSerializer  # all SubTasks
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5  # 5 объектов на страницу (hw14)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter] #hw15
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['-created_at']  # Сортировка по умолчанию

    # переопределение сериалайзера для для POST-запросов
    def get_serializer_class(self):
        """Используем SubTaskCreateSerializer для POST-запросов (create SubTask)."""
        if self.request.method == 'POST':
            return SubTaskCreateSerializer
        return self.serializer_class

#hw15 Generic View: Класс для получения, обновления и удаления подзадачи по ID
class SubTaskDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Получение (GET), обновление (PUT) и удаление (DELETE) подзадачи по ID.
    """
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

    # переопределение сериалайзера для PUT-запросов
    def get_serializer_class(self):
        """Используем SubTaskCreateSerializer для PUT-запросов (update SubTask)."""
        if self.request.method in ['PUT', 'PATCH']:
            return SubTaskCreateSerializer
        return self.serializer_class
