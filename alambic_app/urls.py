from django.urls import path, re_path
from alambic_app.views import *

urlpatterns = [
    path('', index, name='index'),
    path('upload', upload, name='upload'),
    path('pouring', pouring, name='pouring'),
    path('setup', SetupView.as_view(), name='setup'),
    path('job/status', job_status, name='job_status'),
    path('chopping', chopping_ingredients, name='chopping'),
    path('distilling', distilling, name='distilling'),
    path('tasting', tasting, name='tasting'),
    path('spirit', success, name='spirit'),
    path('about', about, name='about'),
    path('documentation', documentation, name='documentation'),
]
