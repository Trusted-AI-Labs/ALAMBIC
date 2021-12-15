import logging

from django.core.cache import cache

from alambic_app.forms import *

logger = logging.getLogger(__name__)


def get_forms():
    forms = [None, None, None]
    model = cache.get('model')
    task = cache.get('task')
    if model == 'Text':
        forms[0] = PreprocessingText

    if task == 'Classification':
        forms[1] = None

    forms[2] = None  # active learning form

    return forms
