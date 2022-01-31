from alambic_app.models.input_models import Output


def create_label_oracle(label, data, annotated_by_human=True):
    Output.objects.create(
        data=data,
        label=label,
        annotated_by_human=annotated_by_human
    )
