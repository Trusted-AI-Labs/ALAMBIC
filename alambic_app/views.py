import logging

from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from formtools.wizard.views import SessionWizardView

from alambic_app.utils.data_management import *
from alambic_app.utils.misc import create_label_oracle
from alambic_app.utils.plots import get_performance_chart_formatted_data
from alambic_app.utils.exceptions import BadRequestError
from alambic_app import tasks

from celery.result import AsyncResult


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
            result = tasks.upload_form_data.delay(filename=form.cleaned_data['input_file'],
                                                  model=form.cleaned_data['model'],
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


def job_status(request):
    """
    Shamelessly found in ORVAL code, by Alexandre Renaud
    Keep track of progress of pipelines
    """
    if request.method == 'GET':
        params = request.GET
        if "token" not in params:
            raise ValidationError("Invalid or missing job id.")
        job_id = params["token"]
        result = AsyncResult(job_id)
        if result.status == "SUCCESS":
            return JsonResponse({"token": job_id, "status": result.status})
        else:
            task_refs = tasks.get_pipeline_task_refs(job_id)
            success_counter = 0
            for task, task_ref in sorted(task_refs.items(), key=lambda kv: kv[1]["step"]):
                task_id = task_refs[task]["id"]
                result = tasks.get_task_signature(task).AsyncResult(task_id)
                if result.status == "FAILURE":
                    return JsonResponse({"id": job_id, "status": result.status})
                elif result.status == "SUCCESS":
                    success_counter += 1
            progress_status = "RUNNING..."  # ({0:.0f}%)".format(float(success_counter * 100)/len(task_refs))
            return JsonResponse(
                {"id": job_id,
                 "status": progress_status,
                 "current_step": success_counter + 1,
                 "total_steps": len(task_refs)}
            )
    raise BadRequestError("Invalid server request")


def data_request(request):
    data = request.GET.get('data')
    data_type = request.GET.get('data_type')
    res = None

    if data == 'performance':
        res = get_performance_chart_formatted_data(data_type)

    return JsonResponse(res)


def chopping_ingredients(request):
    """
    Renders template page for the feature extraction and preprocessing
    Inspired by : https://stackoverflow.com/questions/17649976/celery-chain-monitoring-the-easy-way
    """
    if request.method == 'GET':
        params = request.GET
        if "id" not in params:
            raise BadRequestError("Missing job id")
        task_id = params["id"]
        return render(request, 'chopping.html', {'token': task_id})
    raise BadRequestError("Invalid server request")


def distilling(request):
    if request.method == 'GET':
        ids_to_label = cache.get('to_label')
        if len(ids_to_label) > 0:
            to_label = ids_to_label.pop()
            cache.set('to_label', ids_to_label)
            return HttpResponseRedirect(f"/tasting?pre_labelling={to_label}")
        else:
            chain_id = tasks.pipeline_ML()
            return render(request, 'distilling.html', {'token': chain_id})
    raise BadRequestError("Invalid server request")


def tasting(request):
    form, annotation_template = get_form_and_template_annotation()
    manager = cache.get('manager')
    if request.method == 'GET':
        params = request.GET
        cache.set('pre_label', False)
        if "pre_labelling" in params:
            id_data = params['pre_labelling']
            cache.set('pre_label', True)
        else:
            if "id" not in params:
                raise BadRequestError("Missing result id")
            chain_id = params["id"]
            if manager.check_criterion():
                return HttpResponseRedirect(f"/spirit?id={chain_id}")

            id_data = tasks.get_pipeline_result(chain_id, tasks.query)
        data = get_info_data(id_data)
        cache.set('current_data_labelled', data)
        return render(request, annotation_template, {'to_annotate': data, 'form': form})

    elif request.method == "POST":
        print(request.GET)
        completed_form = form(request.POST)
        if completed_form.is_valid():
            data = cache.get('current_data_labelled')
            create_label_oracle(completed_form.cleaned_data['label'], data)
            if cache.get('pre_label'):
                manager.update_datasets([data.pk])
            else:
                manager.next_step([data.pk])
            return HttpResponseRedirect('/distilling')
    raise BadRequestError("Invalid server request")


def success(request):
    """
    Renders the page when the stop criterion has been reached, where you can
    download the model and the results (csv + plots)
    """
    if request.method == 'GET':
        params = request.GET
        if "id" not in params:
            raise BadRequestError("Missing result id")
        result_id = params["id"]
        return render(request, 'spirit.html', {'token': result_id})
    raise BadRequestError("Invalid server request")


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
        form = None

        if step is None:
            step = self.steps.current

        if step == "Data" and cache.get('data', 0) > 0:
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

        else:
            BadRequestError("Invalid server request")

        return form

    def process_step(self, form):
        step_data = super().process_step(form)

        if self.steps.current == 'Data':
            pass

        return step_data

    def done(self, form_list, **kwargs):
        data_list = [form.cleaned_data for form in form_list]
        ## do something with it
        form_data = {
            'data': data_list[0],
            'task': data_list[1],
            'model_settings': data_list[2],
            'active': data_list[3]
        }
        result = tasks.preprocess_and_feature_extraction(form_data)
        return HttpResponseRedirect("/chopping?id=" + result.id)
