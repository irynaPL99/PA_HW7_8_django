from rest_framework.serializers import ModelSerializer, StringRelatedField
from rest_framework import serializers
from .models import Task, Category

"""Создайте эндпоинт для создания новой задачи. 
Задача должна быть создана с полями title, description, status, и deadline.
"""
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class TaskCreateSerializer(ModelSerializer):
    class Meta:
        model = Task
        #fields = '__all__'
        fields = ['title', 'description', 'status', 'deadline']


"""Создайте !!два!! новых эндпоинта для:
+ Получения списка задач
+ Получения конкретной задачи по её уникальному ID
"""
class TaskListSerializer(ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = Task
        fields = ['title', 'categories', 'status', 'deadline']

class TaskDetailSerializer(ModelSerializer):
    categories = StringRelatedField(many=True)
    # StringRelatedField использует метод __str__ связанной модели
    class Meta:
        model = Task
        fields = '__all__'

"""Статистика по задачам
3.1 общее количество задач.
3.2 количество задач по каждому статусу.
3.3 количество просроченных задач.
"""
class TaskStatisticSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    tasks_by_status = serializers.DictField(child=serializers.IntegerField())
    overdue_tasks = serializers.IntegerField()