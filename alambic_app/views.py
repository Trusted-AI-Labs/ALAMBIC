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
    form_list = get_default_form_list()

    # print(form_list)

    def get_context_data(self, form, **kwargs):
        context = super(SetupView, self).get_context_data(
            form=form, **kwargs)
        context.update({
            'data': cache.get('data', 0),
            'step_icons': {
                'Data': 'description',
                'Task': 'display_settings',
                'Model Settings': 'build',
                'Active Learning': 'co_present'
            }
        })

        return context

    def get_form(self, step=None, data=None, files=None):
        if step is None:
            step = self.steps.current

        if step == "Data":
            form_class = get_form_data()
            form = form_class(data)

        elif step == "Task":
            form_class = get_form_task()
            form = form_class(data)

        elif step == "Model Settings":
            model_choice = self.get_cleaned_data_for_step("Task")['model_choice']
            form_class = get_form_model(model_choice)
            form = form_class(data)

        elif step == "Active Learning":
            form_class = get_form_AL()
            form = form_class(data)

        return form

    def process_step(self, form):
        step_data = super().process_step(form)

        if self.steps.current == 'Data':
            pass

        return step_data

    def done(self, form_list, **kwargs):
        data_list = [form.cleaned_data for form in form_list]
        ## do something with it
        print(data_list)
        return JsonResponse({'success': True})
