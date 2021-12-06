import csv

import logging

from django.apps import apps

from celery import shared_task

from celery_progress.backend import ProgressRecorder

from alambic_app.models.input_models import Output
from alambic_app.constantes import *

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def upload_form_data(self, filename, model, task):
    """
    Read the file containing all the info for the data instances
    and creates the model instances corresponding to the model
    and the task
    :param filename: str, file containing the labels and paths/content
    :param model: str, type of data input
    :param task: str, type of learning task
    :return: None
    """
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
