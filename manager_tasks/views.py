from rest_framework.views import APIView    #hw13
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view  #hw12
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination  #hw14

from django.utils import timezone   #hw13
from django.db.models import Count  #hw12

from .serializers import TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer
from .serializers import TaskStatisticSerializer    #hw12
from .serializers import CategorySerializer, CategoryCreateSerializer
from .serializers import SubTaskCreateSerializer, SubTaskSerializer

from .models import Task, SubTask, Category


@api_view(['POST'])
def create_task(request):
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""hw12: @api_view, 
hw14: Фильтрация по дню недели, если параметр передан.
Если никакой параметр запроса не передавался - по умолчанию выводить все записи.
"""
@api_view(['GET'])
def get_all_tasks(request):
    # Получаем параметр weekday из запроса
    weekday = request.query_params.get('weekday', None)
    tasks = Task.objects.all()
    # Фильтрация по дню недели, если параметр передан
    if weekday:
        # Словарь для соответствия строки дня недели числовому значению
        weekday_map = {
            'monday': 0,
            'tuesday': 1,
            'wednesday': 2,
            'thursday': 3,
            'friday': 4,
            'saturday': 5,
            'sunday': 6
        }
        try:
            # получить номер для из словаря weekday_map
            weekday_num = weekday_map.get(weekday.lower())
            if weekday_num is None:
                return Response(
                    {'error': 'Invalid weekday. Use: monday, tuesday, wednesday, thursday, friday, saturday, sunday'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Фильтруем задачи по дню недели на основе deadline
            tasks = tasks.filter(deadline__week_day=weekday_num + 1)# Django использует 1-7 для дней недели
        except ValueError:
            return Response(
                {'error': 'Invalid weekday format'},
                        status=status.HTTP_400_BAD_REQUEST
            )

    serializer = TaskListSerializer(tasks, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_task_detail(request, pk): # pk - PrimeryKey
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)

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

""" hw 12:
@api_view(['POST'])
def create_subtask(request):
    serializer = SubTaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""

"""hw 13 Создайте классы представлений(APIView) для создания и 
получения списка подзадач (SubTaskListCreateView).
hw14: Добавить пагинацию в отображение списка подзадач. 
На одну страницу должно отображаться не более 5 объектов. 
Отображение объектов должно идти в порядке убывания даты 
(от самого последнего добавленного объекта к самому первому, '-created_at')
"""
class SubTaskListCreateView(APIView):
    """
        Get all SubTasks (GET) , create new SubTask (POST).
    """
    # Настройка пагинации
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5  # количество объектов на странице до 5

    def get(self, request):
        # все подзадачи, отсортированные по убыванию даты создания
        subtasks = SubTask.objects.all().order_by('-created_at')
        # Применяем пагинацию
        paginator = self.pagination_class()
        # для разделения списка подзадач на страницы на основе параметров запроса (например, page=1)
        paginated_subtasks = paginator.paginate_queryset(subtasks, request)

        serializer = SubTaskSerializer(paginated_subtasks, many=True)
        #return Response(serializer.data, status=status.HTTP_200_OK)
        # Возвращаем пагинированный ответ
        return paginator.get_paginated_response(serializer.data) # метод возвращает ответ
        # с пагинированными данными, включая метаданные (например, count, next, previous)

    def post(self, request):
        serializer = SubTaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""hw13 Создайте классы представлений для получения, 
обновления и удаления подзадач (SubTaskDetailUpdateDeleteView)"""
class SubTaskDetailUpdateDeleteView(APIView):
    """
    Get, update, delete SubTask by ID (GET, PUT, DELETE).
    """
    def get(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubTaskSerializer(subtask)
        return Response(serializer.data)

    def put(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SubTaskSerializer(subtask, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            subtask = SubTask.objects.get(pk=pk)
        except SubTask.DoesNotExist:
            return Response({'error': 'Subtask not found'}, status=status.HTTP_404_NOT_FOUND)
        subtask.delete()
        return Response({'message': 'Subtask was deleted'}, status=status.HTTP_204_NO_CONTENT)

"""hw14: получение списка всех подзадач по названию главной задачи и статусу подзадач
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





