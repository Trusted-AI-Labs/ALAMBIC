from django.core.cache import cache
from django.db.models import Case, When

from alambic_app.models.input_models import Output
from alambic_app.models.labels import ClassificationLabel, RegressionLabel


def create_label_oracle(label, data, annotated_by_human=True):
    Output.objects.create(
        data=data,
        label=label,
        annotated_by_human=annotated_by_human
    )


def filter__in_preserve(queryset, field, values):
    # Found on Stackoverflow : https://stackoverflow.com/a/67265061
    preserved = Case(*[When(**{field: val}, then=pos) for pos, val in enumerate(values)])
    return queryset.filter(**{f'{field}__in': values}).order_by(preserved)


def get_data_to_label():
    ids_to_label = cache.get('to_label')
    id_data = ids_to_label.pop()
    cache.set('to_label', ids_to_label)
    return id_data


def convert_id_label_to_value(label_type):
    if label_type == 'C':
        label_data = list(ClassificationLabel.objects.all().values('class_id', 'value'))
        conversion_dict = {data['class_id']: data['value'] for data in label_data}
    elif label_type == 'R':
        label_data = list(RegressionLabel.objects.all().values('id', 'value'))
        conversion_dict = {data['id']: float(data['value']) for data in label_data}
    return conversion_dict


def get_next_fold():
    folds = cache.get('folds')
    fold = folds.pop()
    cache.set('folds', folds)
    return fold


def update_repeat():
    repeat = cache.get('current_repeat')
    repeat += 1
    cache.set('current_repeat', repeat)


def update_strategy(strategies, index):
    if index == -1 or index == len(strategies) - 1:
        return strategies[0]
    else:
        return strategies[index + 1]
