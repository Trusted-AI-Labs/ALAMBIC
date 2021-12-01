from alambic_app.models.input_models import *
from alambic_app.models.labels import *


def upload_form_data(filename, model, task):
    for line in filename:
        line = line.strip().split('\t')
        x, y = line[:-1], line[-1]
        label = None
        label_data = {'type': task}

        # create the data instance
        if model == "Text":
            data = Text.objects.create_instance({'filename': x})
        elif model == "Image":
            data = Image.objects.create_instance({'filename': x})
        else:
            raise Exception("Invalid Option chosen for data creation")

        # create the label with the last column if an output is present
        if y:
            if task == "C":
                label_data['value'] = y
                label_data['class_id'] = ClassificationLabel.objects.get_id(y)
                label = ClassificationLabel.objects.create_instance(label_data)
            elif task == "R":
                label_data['value'] = float(y)
                label = RegressionLabel.objects.create_instance(label_data)

        # create output object liking data and labels
        output = Output.objects.create({'data': data, 'label': label})
