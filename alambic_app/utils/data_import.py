from alambic_app.models.input_models import *
from alambic_app.models.labels import *


def upload_form_data(filename, model, task):
    for line in filename:
        x, y = line.split()
        label = None

        # create the data instance
        if model == "Text":
            data = Text.objects.create_instance()
        else:
            pass

        # create the label with the last column if an output is present
        if y:
            if task == "Classification":
                label = ClassificationLabel.objects.create_instance()
            elif task == "Regression":
                pass

        # create output object liking data and labels
        pk_output = Output.objects.create({'data': data, 'label': label})
