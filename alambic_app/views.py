import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from alambic_app.utils.data_management import *
from alambic_app.utils.exceptions import BadRequestError
from alambic_app.tasks import upload_form_data

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
            result = upload_form_data.delay(filename=form.cleaned_data['input_file'], model=form.cleaned_data['model'],
                                            task=form.cleaned_data['task'])
            return HttpResponseRedirect("/pouring?id=" + result.id)
    else:
        form = GeneralInfoInputForm()
    return render(request, 'upload_data.html', {'form': form})


def pouring(request):
    if request.method == 'GET':
        params = request.GET
        if "id" not in params:
            raise BadRequestError("Missing job id")
        task_id = params["id"]
        return render(request, "pouring.html", {"token": task_id})
    raise BadRequestError("Invalid server request")


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


class SetupView(TemplateView):
    template_name = "setup.html"
    data_form, learning_form, active_form = get_forms()

    def get_context_data(self, **kwargs):
        context = super(SetupView, self).get_context_data(**kwargs)
        context['data'] = cache.get('data', 0)

        return context
