from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.serializers import ModelSerializer, StringRelatedField
from rest_framework import serializers
from .models import Task, Category, SubTask

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

    def validate_deadline(self, value):
        if value < timezone.now():
            raise ValidationError("Deadline cannot be in the past.")
        return value

class SubTaskSerializer(ModelSerializer):
    class Meta:
        model = SubTask
        fields = '__all__'

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

"""hw13 def create, def update"""
"""
class CategoryCreateSerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def validate(self, data):
        name = data.get('name')
        if name is None:
            raise ValidationError({"name": "This field is required."})

        # Проверяем уникальность
        if self.instance is not None:
            if name == self.instance.name:
                return data
            queryset = Category.objects.exclude(pk=self.instance.pk)
        else:
            queryset = Category.objects.all()

        if queryset.filter(name=name).exists():
            raise ValidationError({"name": f"Category with name '{name}' already exists."})
        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
"""
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

