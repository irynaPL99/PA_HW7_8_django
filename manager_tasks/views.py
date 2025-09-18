from rest_framework.request import Request
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.utils import timezone
from django.db.models import Count

from .serializers import TaskCreateSerializer, TaskListSerializer, TaskDetailSerializer, TaskStatisticSerializer
from .models import Task

@api_view(['POST'])
def create_task(request):
    serializer = TaskCreateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

"""Статистика по задачам
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




