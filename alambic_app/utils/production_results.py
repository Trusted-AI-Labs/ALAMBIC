from typing import List, Any, Dict
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg

from csv import DictWriter

from alambic_app.models.results import Result
from alambic_app.models.input_models import Data

from alambic_app.utils.misc import convert_id_label_to_value, get_label

from alambic_app.constantes import AL_ALGORITHMS_MATCH


def get_performance_chart_formatted_data(data_type: str):
    results = None
    total_size = 0

    if data_type == 'classification':
        results = list(
            Result.objects.values(
                'step',
                'training_size',
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
                'training_size',
                'unlabelled_data',
                'annotated_by_human',
                'mse'
            )
        )

    for i in range(len(results)):
        data_step = results[i]
        total_size = data_step['unlabelled_data'] + data_step['training_size']
        data_step['ratio labelled'] = float(data_step['training_size'] / total_size)
        del data_step['unlabelled_data']
        results[i] = data_step

    return results, total_size


def get_analysis_chart_formatted_data(data_type):
    results = dict()
    final_results = []
    measure = ''

    if data_type == 'C':
        measure = 'accuracy'

    res = list(Result.objects
               .values('training_size', 'query_strategy')
               .annotate(average_performance=Avg(measure))
               .order_by('training_size')
               )

    for result in res:
        if result['training_size'] not in results:
            results[result['training_size']] = dict()
        results[result['training_size']][AL_ALGORITHMS_MATCH[result['query_strategy']]] = result['average_performance']

    for k, v in results.items():
        res_dict = {
            'training_size': k
        }
        res_dict.update(v)
        final_results.append(res_dict)

    strategies = list(set(final_results[0].keys()) - {'training_size'})
    info = Result.objects.first()
    max_size = info.training_size + info.unlabelled_data

    return final_results, max_size, strategies


def generate_results_file_analysis():
    results = list(Result.objects.all().values())
    with open(f'{settings.MEDIA_ROOT}/statistics_analysis.csv', 'w') as infile:
        csvwriter = DictWriter(infile, fieldnames=results[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(results)


def generate_results_file_model(data_type: str):
    if data_type == 'C':
        data_type = 'classification'
    elif data_type == 'R':
        data_type = 'regression'
    results, _ = get_performance_chart_formatted_data(data_type)
    with open(f'{settings.MEDIA_ROOT}/statistics.csv', 'w') as infile:
        csvwriter = DictWriter(infile, fieldnames=results[0].keys())
        csvwriter.writeheader()
        csvwriter.writerows(results)


def get_last_statistics():
    res = Result.objects.latest('step').get_nice_format()
    return res


def get_data_results(manager):
    data_ids = list(Data.objects.all().values('id', 'filename'))

    task = cache.get('task')
    conversion_dict = convert_id_label_to_value(task)

    outputs = convert_labels(get_label([data['id'] for data in data_ids]), conversion_dict)
    outputs_manual = convert_labels(get_label([data['id'] for data in data_ids], True), conversion_dict)

    predictions = {label[0]: conversion_dict[label[1]] for label in zip(
        [data['id'] for data in data_ids],
        manager.predict(
            manager.convert_to_indices(
                [data['id'] for data in data_ids]
            )
        )
    )}

    with open(f'{settings.MEDIA_ROOT}/data_informations.csv', 'w') as outfile:
        outfile.write('id,filename,existing_label,manual_label,prediction,test_or_training\n')
        for data in data_ids:
            data_id = data['id']
            filename = data['filename']
            existing_label = outputs.get(data_id, None)
            manual_label = outputs_manual.get(data_id, None)
            prediction = predictions.get(data_id)
            test_or_training = None
            if data_id in manager.convert_to_ids(manager.labelled_indices):
                test_or_training = 'training'
            elif data_id in manager.convert_to_ids(manager.test_set):
                test_or_training = 'test'

            outfile.write(f'{data_id},{filename},{existing_label},{manual_label},{prediction},{test_or_training}\n')


def convert_labels(queryset, conversion_dict):
    task = cache.get('task')
    query = None

    if task == 'C':
        query = 'label__classificationlabel__class_id'
    elif task == 'R':
        query = 'label_id'

    labels = {label['data_id']: label[query] for label in list(queryset.values('data_id', query))}

    for k, v in labels.items():
        labels[k] = conversion_dict[v]

    return labels
