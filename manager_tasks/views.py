from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils import timezone
from django.db.models import Count

from .serializers import TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer
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

"""hw12: @api_view"""
@api_view(['GET'])
def get_all_tasks(request):
    tasks = Task.objects.all()
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
"""
class SubTaskListCreateView(APIView):
    """
        Get all SubTasks (GET) , create new SubTask (POST).
    """
    def get(self, request):
        subtasks = SubTask.objects.all()
        serializer = SubTaskSerializer(subtasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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




