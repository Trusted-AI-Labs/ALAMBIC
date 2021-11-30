import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect

from alambic_app.forms import *
from alambic_app.utils.data_import import *

# Create your views here.

logger = logging.getLogger(__name__)


def about(request):
    return render(request, 'about.html')


def documentation(request):
    return render(request, 'documentation.html')


def index(request):
    return render(request, 'home.html')


def upload(request):
    if request.method == 'POST':
        form = GeneralInfoInputForm(request.POST, request.FILES)
        if form.is_valid():
            upload_form_data(filename=form.input_file, model=form.model, task=form.task)
            return HttpResponseRedirect('/success')
        else:
            form = GeneralInfoInputForm()
    else:
        form = GeneralInfoInputForm()
    return render(request, 'upload_data.html', {'form': form})


def upload_success(request):
    """
    Renders the template for the page that is shown to the user after successfully submitting new data.

    :param request: Request coming from the done view
    :type request: ~django.http.HttpRequest
    :return: Rendered template for the submit success page
    :rtype: ~django.http.HttpResponse
    """
    return render(request, 'upload_success.html')


def distillate(request):
    return render(request, 'distillate.html')
