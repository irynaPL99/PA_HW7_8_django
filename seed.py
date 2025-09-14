from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
from manager_tasks.models import Task, SubTask

"""1.Создание записей:
Task:
title: "Prepare presentation".
description: "Prepare materials and slides for the presentation".
status: "New".
deadline: Today's date + 3 days.
"""
def create_task():
    task_list=[
        Task(title='Prepare presentation',
        description='Prepare materials and slides for the presentation',
        deadline= timezone.now() + timedelta(days=3))
    ]
    Task.objects.bulk_create(task_list)

# from seed import create_task
# from manager_tasks.models import Task
# create_task()
# task = Task.objects.get(title="Prepare presentation")
# print(task.title, task.status, task.deadline)
# Prepare presentation NEW 2025-09-17 21:02:28.328403+00:00

"""2.SubTasks для "Prepare presentation":
title: "Gather information".
description: "Find necessary information for the presentation".
status: "New".
deadline: Today's date + 2 days.

title: "Create slides".
description: "Create presentation slides".
status: "New".
deadline: Today's date + 1 day.
"""
def create_subtask():
    task_new=Task.objects.get(title='Prepare presentation')
    subtask_list=[
        SubTask(title='Gather information',
        description='Find necessary information for the presentation',
        task=task_new,
        deadline= timezone.now() + timedelta(days=2)),

        SubTask(title='Create slides',
        description='Create presentation slides',
        task=task_new,
        deadline= timezone.now() + timedelta(days=1)),
    ]
    SubTask.objects.bulk_create(subtask_list)


# from seed import create_subtask
# from manager_tasks.models import Task, SubTask
# create_subtask()
# task = Task.objects.get(title="Prepare presentation")
# subtasks = SubTask.objects.filter(task=task)
# for s in subtasks:
#    print(s.id, s.title, s.status, s.deadline)

"""2. Чтение записей:
Tasks со статусом "New":
Вывести все задачи, у которых статус "New".
"""
def new_tasks():
    new_tasks=Task.objects.filter(status='New').values("id","title", "description", "deadline")
    for t in new_tasks:
        print(t)


"""
SubTasks с просроченным статусом "Done":
Вывести все подзадачи, у которых статус "Done", но срок выполнения истек.
"""
def done_subtasks_lt_now():
    subtasks=(SubTask.objects.filter(status="Done", deadline__lt=timezone.now()).
              values("id","title", "description", "deadline"))
    for row in subtasks:
        print(row)

"""3.Изменение записей:
Измените статус "Prepare presentation" на "In progress".
Измените срок выполнения для "Gather information" на два дня назад.
Измените описание для "Create slides" на "Create and format presentation slides".
"""
def update_presentation_slides():
    updated_task=Task.objects.filter(title='Prepare presentation').update(status='In progress')
    print(f"task {updated_task} was updated.")
    sub1=SubTask.objects.filter(title='Gather information').update(deadline=timezone.now() - timedelta(days=2))
    print(f"SubTask {sub1} was updated.")
    sub2=SubTask.objects.filter(title='Create slides').update(description='Create presentation slides')
    print(f"SubTask {sub2} was updated.")

"""4.Удаление записей:
Удалите задачу "Prepare presentation" и все ее подзадачи.
"""
# on_delete=models.CASCADE
def delete_presentation_slides():
    try:
        task = Task.objects.get(title='Prepare presentation')
        task.delete()
        print(f"Task '{task.title}' and it's SubTask have been deleted.")
    except ObjectDoesNotExist:
        print(f"Task 'Prepare presentation' does not exist!")
