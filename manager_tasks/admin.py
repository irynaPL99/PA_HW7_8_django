from django.contrib import admin
from .models import Category, Task, SubTask

# Создание класса администратора для модели Category
class CategoryAdmin(admin.ModelAdmin):
# Определение полей, которые будут отображаться в списке объектов модели
    list_display = ('name',) #The value of 'list_display' must be a list or tuple

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline')
    # Задание полей, по которым будет производиться поиск
    search_fields = ('title', 'status')
    # Добавление боковых фильтров для быстрого поиска по указанным полям
    list_filter = ('title', 'status', 'deadline')
    # Определение порядка сортировки объектов в админке
    #ordering = ('status',)
    # Определение порядка и набора полей, которые будут отображаться
    # в форме редактирования объекта
    #fields = ('title', 'status', 'deadline')
    # Определение количества объектов, отображаемых на одной странице в списке
    list_per_page = 3

class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline')
    list_filter = ('title', 'task', 'status', 'deadline')
    list_per_page = 10

admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)