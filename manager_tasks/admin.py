from django.contrib import admin
from .models import Category, Task, SubTask

#class SubTaskInline(admin.TabularInline):
class SubTaskInline(admin.StackedInline):
    # TabularInline - Используется для отображения связанных объектов в
    # табличном формате.; HW11
    # StackedInline: Используется для отображения связанных объектов в
    # вертикальном формате.
    model = SubTask
    extra = 1   # количество пустых форм для ввода новых объектов
    fields = ('title', 'description', 'status', 'deadline')
    show_change_link = True


# Создание класса администратора для модели Category
class CategoryAdmin(admin.ModelAdmin):
# Определение полей, которые будут отображаться в списке объектов модели
    list_display = ('name',) #The value of 'list_display' must be a list or tuple

class TaskAdmin(admin.ModelAdmin):
    #list_display = ('title', 'status', 'deadline')
    list_display = ('short_title', 'status', 'deadline') # HW11 'short_title'
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
    inlines = [SubTaskInline]  #  inline, HW11

    #HW 11, Метод для укороченного отображения (obj.title[:10])
    def short_title(self, obj):
        return obj.title if len(obj.title) <= 10 else obj.title[:10] + "..."

    #HW 11, Подписываем колонку в админке
    short_title.short_description = 'title(<10)'

class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline')
    list_filter = ('title', 'task', 'status', 'deadline')
    list_per_page = 10

    #HW11, action: "для Подзадач -> статус Done"
    # request: Объект запроса, который включает информацию о текущем запросе.
    # queryset: Набор объектов, которые были выбраны для какого-то действия.
    def mark_as_done(self, request, queryset):
        updated_count = queryset.update(status="DONE")  # ('DONE' in DB, 'Done')
        self.message_user(request, f"{updated_count} subtask(s) marked as Done.")

    mark_as_done.short_description = "Mark selected SubTasks as Done"
    actions = [mark_as_done]

admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(SubTask, SubTaskAdmin)