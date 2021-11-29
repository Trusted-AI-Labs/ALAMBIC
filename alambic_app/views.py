import sys
import logging
import os

from django.shortcuts import render

# Create your views here.

logger = logging.getLogger(__name__)


def about(request):
    return render(request, 'about.html')


def documentation(request):
    return render(request, 'documentation.html')


def index(request):
    return render(request, 'home.html')


def upload(request):
    return render(request, 'upload_data.html')


def distillate(request):
    return render(request, 'distillate.html')
