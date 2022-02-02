from django.core.cache import cache
from django.db.models import Case, When

from alambic_app.models.input_models import Output


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
    print(ids_to_label)
    id_data = ids_to_label.pop()
    print(ids_to_label)
    cache.set('to_label', ids_to_label)
    return id_data
