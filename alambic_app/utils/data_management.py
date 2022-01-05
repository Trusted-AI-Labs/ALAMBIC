import logging

from django.core.cache import cache

from alambic_app.forms import *
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
        raise MissingForm


def get_form_task():
    task = cache.get('task')

    if task == 'C':
        return ClassificationModel
    else:
        raise MissingForm


def get_form_model(model):
    if model == "SVC":
        return SVCClassification
    elif model == "RF":
        return RFClassification
    else:
        raise MissingForm


def get_form_AL():
    return ActiveLearningParameters