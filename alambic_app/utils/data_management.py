import logging

from django.core.cache import cache

from alambic_app.forms import *

logger = logging.getLogger(__name__)


def get_forms():
    forms = []
    model = cache.get('model')
    task = cache.get('task')
    form = None

    if model == 'Text':
        form = PreprocessingText

    forms.append(('data', form))

    if task == 'C':
        form = ClassificationParameters

    forms.append(('task', form))

    forms.append(('AL', form))

    return forms
