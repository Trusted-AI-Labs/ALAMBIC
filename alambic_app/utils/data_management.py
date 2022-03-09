import logging

from django.core.cache import cache
from django.apps import apps

from alambic_app.forms import *
from alambic_app.models.input_models import Data
from alambic_app.models.labels import RelationLabel
from alambic_app.utils.exceptions import MissingForm

logger = logging.getLogger(__name__)


def get_default_form_list():
    return [('Data', PreprocessingText),
            ('Task', ClassificationModel),
            ('Model Settings', SVCClassification),
            ('Active Learning', ActiveLearningParameters)]


def get_form_data():
    model = cache.get('model')

    if model == 'Text':
        return PreprocessingText
    else:
        raise MissingForm("Form for the specified data not found.")


def get_form_task():
    task = cache.get('task')

    if task == 'C':
        return ClassificationModel
    else:
        raise MissingForm("Form for the specified task not found")


def get_form_model(model):
    if model == "SVC":
        return SVCClassification
    elif model == "RF":
        return RFClassification
    else:
        raise MissingForm("Form for the specified model not found")


def get_form_AL(step):
    if step == 'choice':
        return ActiveLearningTaskChoice
    elif step == "analysis":
        return ActiveLearningAnalysisParameters
    elif step == "model":
        return ActiveLearningParameters
    else:
        raise MissingForm("Form for the specific task not found")


def get_template_annotation(task):
    if task == 'C':
        temp = 'annotations/classification.html'
    elif task == 'RE':
        temp = 'annotations/relation_extraction.html'
    else:
        raise MissingForm('No template implemented for this task')
    return temp


def get_form_annotation(task):
    if task == 'C':
        form = ClassificationAnnotationForm

    elif task == 'RE':
        form = None

    else:
        raise MissingForm('No form implemented for this task')

    return form


def get_form_and_template_annotation():
    task = cache.get('task')
    return get_form_annotation(task), get_template_annotation(task)


def get_add_form(data_type):
    form = None
    if data_type == 'EntityType':
        form = NewEntityForm

    elif data_type == 'RelationType':
        form = NewRelationForm
    return form


def get_info_data(id):
    return Data.objects.get(id=id)


def get_list_existing_instances(model_type):
    model = apps.get_model(app_label='alambic_app', model_name=model_type)
    return list(model.objects.all().values())


def convert_to_label(data):
    task = cache.get('task')
    if task == 'RE':
        return RelationLabel.objects.create_instance(data=data)


def create_instance(model_type, data):
    model = apps.get_model(app_label='alambic_app', model_name=model_type)
    return model.objects.create(**data)
