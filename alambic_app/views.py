import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from formtools.wizard.views import SessionWizardView

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


class SetupView(SessionWizardView):
    template_name = "setup.html"
    form_list = get_forms()
    print(form_list)

    def get_context_data(self, form, **kwargs):
        context = super(SetupView, self).get_context_data(
            form=form, **kwargs)
        context.update({
            'data': cache.get('data', 0),
            'step_icons': {
                'data': 'description',
                'task': 'display_settings',
                'AL': 'co_present'
            }
        })

        return context

    def process_step(self, form):
        step_data = super().process_step(form)
        print(step_data)

        if self.steps.current == 'disease':
            pass

        return step_data

    def done(self, form_list, **kwargs):
        data_list = [form.cleaned_data for form in form_list]
        form_data = {
            'variants': data_list[0],
            # NOTE: we might allow multiple disease selection
            'diseases': data_list[1]['disease_name'],
            'submitter': self.request.user
        }
        form_data.update(data_list[2])
        ## do something with it
        return JsonResponse({'success': True})
