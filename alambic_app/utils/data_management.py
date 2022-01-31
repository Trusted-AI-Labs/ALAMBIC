import logging

from django.core.cache import cache

from alambic_app.forms import *
from alambic_app.models.input_models import Data
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


def get_form_AL():
    return ActiveLearningParameters


def get_template_annotation(task):
    if task == 'C':
        temp = 'annotations/classification.html'
    else:
        raise MissingForm('No template implemented for this task')
    return temp


def get_form_annotation(task):
    if task == 'C':
        form = ClassificationAnnotationForm

    else:
        raise MissingForm('No form implemented for this task')

    return form


def get_form_and_template_annotation():
    task = cache.get('task')
    return get_form_annotation(task), get_template_annotation(task)


def get_info_data(id):
    return Data.objects.get(id=id)
