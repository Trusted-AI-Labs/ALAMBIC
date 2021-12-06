from django.urls import path, re_path
from alambic_app.views import *

urlpatterns = [
    path('', index, name='index'),
    path('upload', upload, name='upload'),
    path('upload/data', data, name='data'),
    path('data_request', data_request, name='data_request'),
    path('pouring', pouring, name='pouring'),
    path('distillate', distillate, name='distillate'),
    path('about', about, name='about'),
    path('documentation', documentation, name='documentation'),
]
