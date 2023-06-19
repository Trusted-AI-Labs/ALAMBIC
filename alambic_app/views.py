from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt

from formtools.wizard.views import SessionWizardView

from crispy_forms.utils import render_crispy_form

from celery.result import AsyncResult

from alambic_app.utils.data_management import *
from alambic_app.utils.misc import create_label_oracle, get_data_to_label, update_fold, update_repeat, \
    update_strategy, get_label, flush_outputs
from alambic_app.utils.production_results import get_performance_chart_formatted_data, generate_results_file_model, \
    get_last_statistics, get_data_results, get_analysis_chart_formatted_data, \
    generate_results_file_analysis
from alambic_app.utils.exceptions import BadRequestError
from alambic_app import tasks
from alambic_app.machine_learning import *

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
                                                  data_type=form.cleaned_data['data_type'],
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
            raise Exception("Invalid or missing job id.")
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

    if data == 'performance':
        res, max_size = get_performance_chart_formatted_data(data_type)
        return JsonResponse({'data': res, 'size': max_size}, safe=False)

    elif data == 'model':
        res = get_list_existing_instances(data_type)
        return JsonResponse(res, safe=False)

    elif data == 'analysis':
        res, max_size, strategies = get_analysis_chart_formatted_data(cache.get('task'))
        return JsonResponse({'data': res, 'size': max_size, 'strategies': strategies}, safe=False)


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
        return render(request, 'chopping.html', {'token': task_id, 'type_learning': cache.get('type_learning')})
    raise BadRequestError("Invalid server request")


def distilling(request):
    if request.method == 'GET':
        to_label = len(cache.get('to_label'))
        if to_label > 0:
            if cache.get('pre_label'):
                return HttpResponseRedirect(f"/tasting?pre_labelling=True")
            else:
                return HttpResponseRedirect(f"/tasting")
        else:
            chain_id = tasks.pipeline_ML()
            return render(request, 'distilling.html', {'token': chain_id,
                                                       'type_learning': cache.get('type_learning'),
                                                       'task': cache.get('task')
                                                       })
    raise BadRequestError("Invalid server request")


def preparing_batch(request):
    current_repeat = cache.get('current_repeat')
    max_repeat = cache.get('repeats')

    folds = cache.get('folds')
    current_fold = cache.get('current_fold')

    strategies = cache.get('query_strategies')
    current_strategy = cache.get('current_index')

    last_repeat_over = (current_repeat == max_repeat and current_strategy == len(strategies)-1)

    # finished the strategies + repeats or initialization
    if current_repeat is None or (last_repeat_over):
        fold = update_fold(folds, current_fold)
        manager = cache.get('initial_manager')
        manager.set_test_set(fold)
        current_repeat = 0
        cache.set('current_repeat', 0)
        cache.set('manager_repeat', manager)

        current_strategy = -1
        print(f"Fold {cache.get('current_fold')} : {fold}")

    if current_repeat < max_repeat or not last_repeat_over:
        manager = cache.get('manager_repeat')

        # we did all the strategies or initialization and begin a new repetition
        if current_strategy in [-1, len(strategies) - 1]:
            update_repeat(current_repeat)
            manager.initialize_dataset_analysis(cache.get('ratio_seed'), current_repeat == 0)
            cache.set('manager_repeat', manager)
            current_strategy = -1

        # next strategy
        update_strategy(current_strategy)
        current_strategy = strategies[cache.get('current_index')]
        cache.set('current_strategy', current_strategy)
        flush_outputs()
        manager.set_query_strategy(current_strategy)
        cache.set('manager', manager)

        print(f"Repeat {cache.get('current_repeat')} - Strategy {current_strategy}")
        print(f"Labelled data : {manager.labelled_indices}")
        print(f"Test data : {manager.test_set}")

    return HttpResponseRedirect('/distilling')


def tasting(request):
    form, annotation_template = get_form_and_template_annotation()
    
    task = cache.get('task')
    model = cache.get('model')
    if task == 'C':
        if model == 'DL':
            manager = DeepLearningClassification()
        else:
            manager = ClassificationManager()
    elif task == 'R':
        pass

    if request.method == 'GET':
        params = request.GET

        # before launching the learner
        cache.set('pre_label', False)
        if "pre_labelling" in params:
            cache.set('pre_label', True)

        # active learning process
        else:
            if manager.check_criterion():
                if cache.get('type_learning') == 'analysis':
                    over = (cache.get('current_fold') == len(cache.get('folds')) and cache.get('current_repeat') == cache.get('repeats') and cache.get('current_index') == len(cache.get('query_strategies')) - 1)
                    if not over :
                        return HttpResponseRedirect("/distilling/batch")

                return HttpResponseRedirect("/spirit")

        # when we don't have to label manually, it is just done in the while loop
        # if manual, it will pass with POST and redirect to distilling
        while len(cache.get('to_label')) > 0:
            id_data = get_data_to_label()

            data = get_info_data(id_data)

            # we already have the label
            label = list(get_label([id_data]))
            if len(label) > 0:
                create_label_oracle(label.pop().label, data)
                manager.next_step([data.pk], True)
                cache.set('manager', manager)
            else:
                cache.set('current_data_labelled', data)
                return render(request, annotation_template, {'to_annotate': data, 'form': form})

        # only if we have annotated everything automatically
        return HttpResponseRedirect('/distilling')

    elif request.method == "POST":
        valid = False
        cleaned_data = None

        if form is not None:
            completed_form = form(request.POST)
            if completed_form.is_valid():
                cleaned_data = completed_form.cleaned_data['label']
                valid = True

        # when it is posting a new instance and did not use a form to do it
        # special case for RE
        else:
            cleaned_data = convert_to_label(request.POST)

        if valid:
            data = cache.get('current_data_labelled')
            create_label_oracle(cleaned_data, data)
            if cache.get('pre_label'):
                manager.update_datasets([data.pk], True)
                cache.set('manager', manager)
            else:
                manager.next_step([data.pk], True)
                cache.set('manager', manager)
            return HttpResponseRedirect('/distilling')
    raise BadRequestError("Invalid server request")


@csrf_exempt
def add_type(request):
    if request.method == 'POST':
        form_data = request.POST.dict()  # Convert to regular dict to use pop
        form_type = form_data.pop('formType')
        print(form_type, form_data)

        form = get_add_form(form_type)(form_data)

        if form.is_valid():
            form.save()
            return JsonResponse(
                {'name': form.cleaned_data['name'], 'color': form.cleaned_data['color'], 'success': True})

    elif request.method == 'GET':
        form_type = request.GET['formType']
        form = get_add_form(form_type)

    ctx = csrf(request)
    form_html = render_crispy_form(form, context=ctx)
    return JsonResponse({'success': False, 'form_html': form_html})


def success(request):
    """
    Renders the page when the stop criterion has been reached, where you can
    download the model and the results (csv + plots)
    """
    if request.method == 'GET':
        if cache.get('type_learning') == "model":
            manager = cache.get('manager')
            manager.dump()
            generate_results_file_model(cache.get('task'))
            statistics = get_last_statistics()
            get_data_results(manager)
            return render(request, 'success/spirit.html', {'stats': statistics})
        else:
            generate_results_file_analysis()
            return render(request, 'success/spirit_batch.html')
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
                'Usage': 'settings_applications',
                'Active Learning': 'co_present'
            }
        })

        return context

    def get_form(self, step=None, data=None, files=None):
        form = None

        if step is None:
            step = self.steps.current

        if step == "Task":
            form_class = get_form_task()
            form = form_class(data)

        elif step == "Model Settings":
            model_choice = self.get_cleaned_data_for_step("Task")['model_choice']
            form_class = get_form_model(model_choice)
            form = form_class(data)

        elif step == "Data" and cache.get('data', 0) > 0:
            form_class = get_form_data()
            form = form_class(data)

        elif step == "Usage":
            form_class = get_form_AL("choice")
            form = form_class(data)

        elif step == "Active Learning":
            type_AL = self.get_cleaned_data_for_step("Usage")['type_learning']
            form_class = get_form_AL(type_AL)
            form = form_class(data)

        else:
            BadRequestError("Invalid server request")

        return form

    def done(self, form_list, **kwargs):
        data_list = [form.cleaned_data for form in form_list]
        form_data = {
            'task': data_list[0],
            'model_settings': data_list[1],
            'data': data_list[2],
            'type_learning': data_list[3],
            'active': data_list[4]
        }
        if form_data['task']['model_choice'] == 'DL':
            form_data['data']['origin'] = form_data['model_settings']['origin']

        result = tasks.preprocess_and_feature_extraction(form_data)
        return HttpResponseRedirect("/chopping?id=" + result.id)
