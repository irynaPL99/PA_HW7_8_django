# first_app/views.py

from django.shortcuts import render
from django.http import HttpResponse

def first_app_view(request):
    return HttpResponse("<h1>Hello, Irina! It's my first view!</h1>")
