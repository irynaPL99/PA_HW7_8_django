from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User  # hw19

"""Модель Category:
Описание: Категория выполнения.
Поля:
name: Название категории.
"""
#hw16: кастомный менеджер для модели Category,
# метод get_queryset(), по умолчанию - только неудалённые записи (где is_deleted=False)
class CategoryManager(models.Manager):
    """Кастомный менеджер для фильтрации НЕудалённых категорий."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    name = models.CharField(max_length=30, verbose_name="Название категории:",
                            help_text="Категория выполнения (срочность)")
    #hw16 Soft Deletion:
    is_deleted = models.BooleanField(default=False, verbose_name="Удалена")
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата удаления")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания") #hw17, field for pagination

    def delete(self, *args, **kwargs):
        """Мягкое удаление: помечает категорию как удалённую и устанавливает дату."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    objects = CategoryManager()  # Используем кастомный менеджер по умолчанию

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'task_manager_category'
        verbose_name = 'Category'
        unique_together = [['name']]


"""Task
title: Название задачи. Уникально для даты. 
description: Описание задачи.   
categories: Категории задачи. Многие ко многим.
status: Статус задачи. Выбор из: New, In progress, Pending, Blocked, Done
deadline: Дата и время дедлайн.
created_at: Дата и время создания. Автоматическое заполнение.
"""
class Task(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In progress'),
        ('PENDING', 'Pending'),
        ('BLOCKED', 'Blocked'),
        ('DONE', 'Done'),
    ]
    # 28-09-2025 убран "unique_for_date='created_at'",
    # не проходила валидация при изменении задания. Перенесено в серилиалайзер
    #title = models.CharField(max_length=100, unique_for_date='created_at')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True) #blank=True-может быть не указано
    categories = models.ManyToManyField(Category, related_name='tasks', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')  # hw19

    def __str__(self):
        return self.title

    # 28-09-2025проверка на уникальность поля в пределах даты.
    # только при прямом сохранении через Django(admin)
    def clean(self):
        if not self.created_at:  # Если объект ещё не сохранён
            created_at_date = timezone.now().date()
        else:
            created_at_date = self.created_at.date()
        existing_tasks = Task.objects.filter(
            title=self.title,
            created_at__date=created_at_date
        ).exclude(id=self.id)

        if existing_tasks.exists():
            raise ValidationError(
                f"Задача с названием '{self.title}' уже существует для текущей даты."
            )

    class Meta:
        db_table = 'task_manager_task'  #  # Задаем имя таблицы в базе данных
        ordering = ['-created_at'] # Сортировка по убыванию даты создания
        verbose_name = 'Task' # Человекочитаемое имя модели: 'Task'
        #unique_together = [['title']] # Уникальность по полю 'title' или комбинация полей
        # не используем здесь, так как валидация вынесена в сериалайзер

"""Модель SubTask:
Описание: Отдельная часть основной задачи (Task).
Поля:
title: Название подзадачи.
description: Описание подзадачи.
task: Основная задача. Один ко многим.
status: Статус задачи. Выбор из: New, In progress, Pending, Blocked, Done
deadline: Дата и время дедлайн.
created_at: Дата и время создания. Автоматическое заполнение
"""
class SubTask(models.Model):
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('IN_PROGRESS', 'In progress'),
        ('PENDING', 'Pending'),
        ('BLOCKED', 'Blocked'),
        ('DONE', 'Done'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    task = models.ForeignKey(Task, related_name='subtasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                              related_name='subtasks')  # hw19

    def __str__(self):
        return self.title
