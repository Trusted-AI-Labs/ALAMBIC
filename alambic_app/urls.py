from django.urls import path, re_path
from alambic_app.views import *

urlpatterns = [
    path('', index, name='index'),
    path('upload', upload, name='upload'),
    path('pouring', pouring, name='pouring'),
    path('setup', SetupView.as_view(), name='setup'),
    path('distillate', distillate, name='distillate'),
    path('about', about, name='about'),
    path('documentation', documentation, name='documentation'),
]
