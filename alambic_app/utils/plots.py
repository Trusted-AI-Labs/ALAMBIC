from typing import List, Any, Dict
from django.conf import settings

from csv import DictWriter

from alambic_app.models.results import Result


def get_performance_chart_formatted_data(data_type: str):
    results = None

    if data_type == 'classification':
        results = list(
            Result.objects.values(
                'step',
                'unlabelled_data',
                'annotated_by_human',
                'precision',
                'recall',
                'accuracy',
                'mcc',
                'f1_score'
            )
        )
    elif data_type == 'regression':
        results = list(
            Result.objects.values(
                'step',
                'unlabelled_data',
                'annotated_by_human',
                'mse'
            )
        )

    for i in range(len(results)):
        data_step = results[i]
        data_step['ratio labelled'] = float(data_step['annotated_by_human'] / data_step['unlabelled_data'])
        del data_step['annotated_by_human']
        del data_step['unlabelled_data']
        results[i] = data_step

    return results


def generate_results_file(data_type: str):
    if data_type == 'C':
        data_type = 'classification'
    elif data_type == 'R':
        data_type = 'regression'
    results = get_performance_chart_formatted_data(data_type)
    with open(f'{settings.MEDIA_URL}statistics.csv', 'w') as infile:
        csvwriter = DictWriter(infile, fieldnames=results[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(results)


def get_last_statistics():
    res = Result.objects.latest('step').get_nice_format()
    return res
