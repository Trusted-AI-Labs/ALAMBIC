import csv

import logging

from django.apps import apps
from django.core.cache import cache

from celery import shared_task, chain, signature, uuid
from celery.exceptions import TimeoutError
from celery.result import AsyncResult

from celery_progress.backend import ProgressRecorder

from alambic_app.models.input_models import Output
from alambic_app.constantes import *
from alambic_app.machine_learning.preprocessing import PreprocessingHandler
from alambic_app.machine_learning.setup import ClassificationManager
from alambic_app.utils.exceptions import TaskIdNotFoundError

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def upload_form_data(self, filename, model, task):
    """
    Read the file containing all the info for the data instances
    and creates the model instances corresponding to the model
    and the task
    :param self: task celery
    :param filename: str, file containing the labels and paths/content
    :param model: str, type of data input
    :param task: str, type of learning task
    :return: None
    """
    cache.set('model', model)
    cache.set('task', task)
    infile = open(filename, encoding='utf-8')
    reader = csv.DictReader(infile, delimiter='\t')
    nb_rows = len(list(reader))
    infile.seek(0)
    reader = csv.DictReader(infile, delimiter='\t')
    progress_recorder = ProgressRecorder(self)

    for line in reader:
        label = line['label']

        if 'file' in reader.fieldnames:
            data_dict = {'filename': f"{DATA_PATH}/{line['file']}"}
        else:
            data_dict = {'content': line['content']}

        # create the data instance
        data_model = apps.get_model(app_label='alambic_app', model_name=model)

        data = data_model.objects.create_instance(**data_dict)

        # create the label with the last column if an output is present
        if label:
            label_model = apps.get_model(app_label='alambic_app', model_name=LABEL_MATCH[task])
            label_data = {
                'type': task,
                'value': label
            }
            label = label_model.objects.create_instance(**label_data)

        # create output object liking data and labels, with False for annotated by human and False for predicted
        Output.objects.create(**{'data': data, 'label': label})

        # update progress observer
        progress_recorder.set_progress(reader.line_num + 1, nb_rows)
    cache.set('data', nb_rows)


def preprocess_and_feature_extraction(form_data):
    task_id = uuid()
    data = form_data.get('data')

    chopping_pipeline = [run_preprocess.si(data), create_ML_manager.s(args=(form_data,))]

    init_pipeline(chopping_pipeline, task_id, run_pipeline_task_refs, run_pipeline_done)

    return chain(chopping_pipeline).apply_async(task_id=task_id)


def pipeline_ML():
    """
    Launch the pipeline for the active learning loop
    :return: id of the celery chain with the tasks of the pipeline
    """
    task_id = uuid()
    manager = cache.get('manager')

    distilling_pipeline = [train.si(manager), predict.s(), register_result.s(), query.s()]

    init_pipeline(distilling_pipeline, task_id, run_pipeline_task_refs, run_pipeline_done)

    return chain(distilling_pipeline).apply_async(task_id=task_id)


@shared_task
def run_preprocess(operations):
    """
    Celery task for the extraction of the features and the preprocessing of the data
    :param operations: list of str, names of the different operations to do
    :return: the handler containing all the features
    """
    handler = PreprocessingHandler(operations)
    handler.create_features()
    return handler


@shared_task
def create_ML_manager(form_data, handler):
    """
    Create a manager to handle the training, prediction, query selection and the related dataset
    :param form_data: dict, contained all the information for the active learning process
    :param handler: PreprocessingHandler
    :return: lst, empty or str, containing the ids to label
    """
    model = form_data.get('task')['model_choice']
    params_model = form_data.get('model_settings')
    query_strategy = form_data.get('active')['query_strategy']
    stop_criterion = form_data.get('active')['stop_criterion']
    ratio = form_data.get('active')['ratio_test']
    size_seed = form_data.get('active')['size_seed']

    task = cache.get('task')
    if task == 'Classification':
        manager = ClassificationManager(handler, model, query_strategy, stop_criterion, params_model)
    elif task == 'Regression':
        pass

    cache.set('manager', manager)
    ids_to_label = manager.initialize_dataset(ratio, size_seed)

    return ids_to_label


@shared_task
def train(manager):
    """
    Train the model
    :param manager: MLManager
    :return: MLManager
    """
    manager.train()
    return manager


@shared_task
def predict(manager):
    """
    Predict the test set and store the result
    :param manager: MLManager
    :return: MLManager
    """
    manager.predict()
    return manager


@shared_task
def query(manager):
    """
    Choose the query of interest among the unlabelled dataset
    :param manager: MLManager
    :return: MLManager
    """
    cache.set('manager', manager)  # update manager in cache
    return manager.query()


@shared_task
def register_result(manager):
    """
    Store the result measures in the database
    :param manager: MLManager
    :return: MLManager
    """
    manager.register_result()
    return manager


@shared_task
def run_pipeline_task_refs(task_refs):
    return task_refs


@shared_task
def run_pipeline_done():
    return True


def get_pipeline_task_refs(pipeline_chain_id, timeout=10.0):
    """
    Shamelessly found in ORVAL code, by Alexandre Renaud
    Get the list of tasks references
    """
    try:
        return run_pipeline_task_refs.AsyncResult(get_task_ref_id(pipeline_chain_id)).get(timeout=timeout)
    except TimeoutError as e:
        raise TaskIdNotFoundError(e)


def get_pipeline_result(pipeline_chain_id, target_task):
    """
    Shamelessly found in ORVAL code, by Alexandre Renaud
    Get a result from a specific task in a chain
    """
    task = get_pipeline_task_refs(pipeline_chain_id).get(target_task.name)
    if task:
        task_id = task["id"]
        result = target_task.AsyncResult(task_id).get()
        return result
    else:
        return None


def get_task_ref_id(task_id):
    return task_id + "_0"


def get_task_signature(task_name):
    return signature(task_name)


def init_pipeline(pipeline_tasks, chain_id, task_ref_task, done_task, error_callback=None):
    """
    Shamelessly found in ORVAL code, by Alexandre Renaud
    Launch a chain of tasks with references of them
    """
    task_refs = {}
    step = 1
    for task_signature in pipeline_tasks:
        task = task_signature.type
        task_id = chain_id + "_" + str(step)
        task_signature.set(task_id=task_id)
        if error_callback:
            task_signature.on_error(error_callback())
        task_refs[task.name] = {"step": step, "id": task_id}
        step += 1
    pipeline_status_task = task_ref_task.si(task_refs)
    pipeline_status_task.set(task_id=get_task_ref_id(chain_id))
    pipeline_tasks.insert(0, pipeline_status_task)
    pipeline_tasks.append(done_task.si())
