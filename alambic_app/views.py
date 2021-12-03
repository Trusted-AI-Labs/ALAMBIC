import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect

from alambic_app.forms import *
from alambic_app.utils.data_management import *

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
            upload_form_data(filename=form.cleaned_data['input_file'], model=form.cleaned_data['model'],
                             task=form.cleaned_data['task'])
            return HttpResponseRedirect('upload_data/data')
    else:
        form = GeneralInfoInputForm()
    return render(request, 'upload_data.html', {'form': form})


def data(request):
    """
    Renders the template for the page that is shown to the user after successfully submitting new data.

    :param request: Request coming from the done view
    :type request: ~django.http.HttpRequest
    :return: Rendered template for the submit success page
    :rtype: ~django.http.HttpResponse
    """
    return render(request, 'data.html')


def distillate(request):
    return render(request, 'distillate.html')


def data_request(request):
    """
    View that handles data requests by delegating to the appropriate request handlers based on the request parameters.
    Expects a GET request with a data field specifying what data to retrieve.
    A second field called data_usage should specify what the data will be used for (table, chart, download, ...)
    Validates the request and delegates to appropriate handlers.

    :param request: The HTTP GET request that was made to the */data* url associated with this view
    :type request: ~django.http.HttpRequest
    :return: Either a response containing JSON with the data, or the requested file
    :rtype: ~django.http.JsonResponse
    """
    requested_data = request.GET.get('data')
    response = {}

    # print(list(request.GET.items()))

    # If there is a valid data request we continue otherwise we throw an error
    if requested_data is not None:
        data_usage = request.GET.get('data_usage')
        # Depending on what the data is for (table, chart, download, ...) a different handler is required
        if data_usage == 'chart':
            pass
        elif data_usage == 'table':
            response = JsonResponse(get_table_data(requested_data))
            # response = JsonResponse(get_table_data(requested_data))
        else:
            raise Exception(
                'Invalid data request, invalid or inexistent data_usage field')
    else:
        raise Exception(
            'Invalid data request, check if you are using GET method and providing a data field')

    return response
