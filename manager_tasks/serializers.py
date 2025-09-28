import logging
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.serializers import ModelSerializer, StringRelatedField
from rest_framework import serializers
from .models import Task, Category, SubTask

logger = logging.getLogger(__name__)

"""hw12 Создайте эндпоинт для создания новой задачи. 
Задача должна быть создана с полями title, description, status, и deadline.
"""
class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        #fields = ['name']
        fields = '__all__'


"""hw13 добавьте валидацию для поля deadline, чтобы дата не могла быть в прошлом. 
Если дата в прошлом, возвращайте ошибку валидации 
"""
class TaskCreateSerializer(ModelSerializer):
    class Meta:
        model = Task
        #fields = '__all__'
        fields = ['title', 'description', 'status', 'deadline']
        read_only_fields = ['created_at']   #hw15 (add update Task als Generic View)

    def validate(self, data):
        logger.debug(f"Validating data: {data}")
        # Проверяем уникальность title для текущей даты
        existing_tasks = Task.objects.filter(
            title=data['title'],
            created_at__date=timezone.now().date()
        ).exclude(id=self.instance.id if self.instance else None)

        if existing_tasks.exists():
            raise ValidationError(
                f"Задача с названием '{data['title']}' уже существует для текущей даты."
            )
        return super().validate(data)

    def is_valid(self, raise_exception=False):
        # Убедимся, что вызываем базовый метод с правильными аргументами
        try:
            is_valid = super().is_valid(raise_exception=raise_exception)
            logger.debug(f"Validation result: {self.errors if not is_valid else 'Valid'}")
            return is_valid
        except Exception as e:
            logger.error(f"Validation failed with exception: {e}")
            raise

    # явно удаляет "created_at" из validated_data, если оно случайно попало туда
    def update(self, instance, validated_data):
        logger.debug(f"Updating instance with validated data: {validated_data}")
        # Исключаем "created_at" из обновления, так как оно read_only
        validated_data.pop('created_at', None)
        return super().update(instance, validated_data)





class SubTaskSerializer(ModelSerializer):
    task_title = serializers.CharField(source='task.title', read_only=True) # название главной(связанной) задачи

    class Meta:
        model = SubTask
        #fields = '__all__'
        fields = ['id', 'task_title', 'title', 'status', 'created_at']  # Включаем id и task.title

"""hw12 Создайте !!два!! новых эндпоинта для:
+ Получения списка задач
+ Получения конкретной задачи по её уникальному ID
"""
class TaskListSerializer(ModelSerializer):
    categories = CategorySerializer(many=True)
    class Meta:
        model = Task
        #fields = '__all__'
        fields = ['id', 'title', 'categories', 'status', 'deadline']

"""hw 13. Сериализатор  TaskDetailSerializer должен показывать все подзадачи, 
связанные с данной задачей
"""
class TaskDetailSerializer(ModelSerializer):
    categories = CategorySerializer(many=True)
    #categories = StringRelatedField(many=True)
    # StringRelatedField использует метод __str__ связанной модели
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = '__all__'

"""hw12 Статистика по задачам
3.1 общее количество задач.
3.2 количество задач по каждому статусу.
3.3 количество просроченных задач.
"""
class TaskStatisticSerializer(serializers.Serializer):
    total_tasks = serializers.IntegerField()
    tasks_by_status = serializers.DictField(child=serializers.IntegerField())
    overdue_tasks = serializers.IntegerField()


"""hw13.Создайте SubTaskCreateSerializer, 
в котором поле created_at будет доступно только для чтения (read_only). 
"""
class SubTaskCreateSerializer(ModelSerializer):
    class Meta:
        model = SubTask
        #fields = ['title', 'description','task', 'status', 'deadline']
        fields = '__all__'
        read_only_fields = ['created_at']  # Переопределяем created_at как read_only
        # не будет приниматься из данных запроса (например, из JSON в POST  или PUT -запросе)
        # будет автоматически установлено при сохранении объекта благодаря auto_now_add=True

class CategoryCreateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__' # ['name']
        # список валидаторов, которые будут применяться к данным перед сохранением
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Category.objects.all(),
                fields=['name'],
                message="Category with this name already exists."
            )
        ]
        # UniqueTogetherValidator - встроенный валидатор DRF, который проверяет уникальность комбинации полей в наборе данных.
        # Он обычно используется для моделей с несколькими полями
        # (например, unique_together = [['field1', 'field2']]), но может применяться и для одного поля

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

