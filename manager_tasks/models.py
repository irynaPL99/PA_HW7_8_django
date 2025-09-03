from django.db import models

"""Модель Category:
Описание: Категория выполнения.
Поля:
name: Название категории.
"""
class Category(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name="Название категории",
                            help_text="Категория выполнения")
    def __str__(self):
        return self.name

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

    title = models.CharField(max_length=100, unique_for_date='created_at')
    description = models.TextField(blank=True) #blank=True-может быть не указано
    categories = models.ManyToManyField(Category, related_name='tasks', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NEW')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

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

    def __str__(self):
        return self.title
