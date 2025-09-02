# first_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
#Django ожидает, что в модуле first_app.views
    # есть функция или класс с именем "first_app_view"
path('first/', views.first_app_view, name='first_app'),
]