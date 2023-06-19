import math
import logging

import numpy as np
import random
import sklearn
import torch
import gc

from typing import Tuple, Union

from sklearn.ensemble import RandomForestClassifier
from joblib import dump, load
from alipy.query_strategy import query_labels
from torch.nn.functional import softmax
from transformers import get_scheduler

from typing import List, Dict, Any

from django.db.models import QuerySet
from django.conf import settings

from alambic_app.active_learning import stopcriterion
from alambic_app.active_learning import strategies
from alambic_app.machine_learning.preprocessing import PreprocessingHandler
from alambic_app.machine_learning.models import *
from alambic_app.utils.misc import filter__in_preserve

from alambic_app.models.input_models import Output, Data, Label
from alambic_app.models.results import Result
from alambic import OneAccelerator

AL_ALGORITHMS_MATCH = {
    'RS': strategies.QueryInstanceRandom,
    'US': query_labels.QueryInstanceUncertainty,
    'MS': query_labels.QueryInstanceUncertainty,
    'ES': query_labels.QueryInstanceUncertainty,
    'CS': strategies.QueryInstanceCoresetGreedy
}

MODELS_MATCH = {
    'SVC': sklearn.svm.SVC,
    'RF': RandomForestClassifier,
    'loading': load
}

STOP_CRITERION_MATCH = {
    'budget': stopcriterion.budget_reached,
    'accuracy': stopcriterion.accuracy_reached,
    'final': stopcriterion.final_reached
}

logger = logging.getLogger(__name__)

class Singleton (type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MLManager(metaclass=Singleton):
    """
    Class to handle the performance
    """

    def __init__(self, handler: PreprocessingHandler, model: str, batch_size: int, stopcriterion: str,
                 stopcriterion_param: Any, params: dict):
        self.step = 0
        self.handler = handler

        logger.info("----- Create model -----")
        self.model = self.create_model(model, params)
        logger.info("----- Model created -----")

        self.stopcriterion = STOP_CRITERION_MATCH[stopcriterion]
        self.goal = stopcriterion_param
        self.batch_size = batch_size

        self.unlabelled_indices, self.labelled_indices = self.get_labelled_dataset()
        self.indices_to_ids = {k: v for k, v in enumerate(self.labelled_indices + self.unlabelled_indices)}
        self.ids_to_indices = {v: k for k, v in self.indices_to_ids.items()}
        self.test_set = []

        logger.info("----- Get data -----")

        self.X = self.get_x(self.labelled_indices + self.unlabelled_indices)
        self.Y = np.array(self.get_y(self.convert_to_indices(self.labelled_indices + self.unlabelled_indices)))

        logger.info("----- Got data -----")
        self.y_train = []
        self.y_test = []
        self.y_predicted = []
        self.strategy_name = ''
        self.strategy = ''

    def convert_to_ids(self, lst):
        return [self.indices_to_ids[idx] for idx in lst]

    def convert_to_indices(self, lst):
        return [self.ids_to_indices[ids] for ids in lst]

    def create_model(self,model: str, params: Dict[str, Any]):
        """
        Create the model to train with the chosen parameters
        :param model: name of the model found in MODELS_MATCH as key
        :param params: parameters of the model
        :return: parameterized model
        """
        # TODO add here parameters if necessary according to the model
        return MODELS_MATCH[model](**params)

    def create_folds(self, k):
        lst_splits = []
        splits = sklearn.model_selection.StratifiedKFold(k, shuffle=True, random_state=2).split(
            np.array(self.labelled_indices), np.array(self.get_y(self.convert_to_indices(self.labelled_indices))))
        for _, test_index in splits:
            lst_splits.append(np.array(self.labelled_indices)[test_index].tolist())
        return lst_splits

    def set_query_strategy(self, strategy):
        kwargs = dict()
        measures = {
            'ES': 'entropy',
            'MS': 'margin',
            'US': 'least_confident'
        }
        if strategy in ('MS', 'ES', 'US'):
            kwargs.update({'measure': measures[strategy]})

        self.strategy_name = strategy
        self.strategy = AL_ALGORITHMS_MATCH[strategy](self.X, self.Y, **kwargs)

    def check_criterion(self):
        return self.stopcriterion(self.goal, self)

    @staticmethod
    def get_annotated_by_human():
        return Output.objects.filter(annotated_by_human=True).count()

    @staticmethod
    def get_labelled_dataset():
        unlabelled = list(Output.objects.filter(label__isnull=True).values_list('data_id', flat=True))
        labelled = list(Output.objects.exclude(data_id__in=unlabelled).values_list('data_id', flat=True))
        return unlabelled, labelled

    def initialize_dataset(self, ratio: Union[float,int], size_seed: int) -> List[int]:
        """
        Split into training set and test set, assign them to labelled_indices and test_set
        :param ratio: percentage of the total dataset dedicated to the test set, or total number of sampes for test set
        :param size_seed: number of data points the learner will begin with in the active learning algorithm
        :return: list of ints, ids of data to label
        """
        total_data = Data.objects.all().count()
        ids_to_add = []
        is_ratio_float = isinstance(ratio, float)
        if is_ratio_float:
            current_ratio = len(self.labelled_indices) / total_data
        else:
            current_ratio = len(self.labelled_indices)
        

        # missing labelled data
        if current_ratio < ratio:
            if is_ratio_float:
                nb_ids_to_add = int((total_data * ratio) - len(self.labelled_indices))
            else:
                nb_ids_to_add = int(ratio - len(self.labelled_indices))
            ids_to_add = random.sample(self.unlabelled_indices, nb_ids_to_add)
            self.test_set = ids_to_add.copy()
            self.unlabelled_indices = [data_id for data_id in self.unlabelled_indices if data_id not in ids_to_add]

        elif current_ratio >= ratio:
            if is_ratio_float:
                nb_ids_to_sample = int(total_data * ratio)
            else:
                nb_ids_to_sample = int(ratio)
            self.test_set = random.sample(self.labelled_indices, nb_ids_to_sample)
            self.labelled_indices = [data_id for data_id in self.labelled_indices if data_id not in self.test_set]

        # reduce the training set to the original size
        ids_to_add += self.set_seed(size_seed)

        # translate the data_ids to their position in the X array
        self.test_set = self.convert_to_indices(self.test_set)
        self.labelled_indices = self.convert_to_indices(self.labelled_indices)
        self.unlabelled_indices = self.convert_to_indices(self.unlabelled_indices)

        return ids_to_add

    def set_seed(self, size_seed: int) -> List[int]:
        """
        Get the seed for the active learning algorithm.
        Set the training set to have an initial size corresponding to the initial size
        Put the rest of the remaining labelled dataset to the unlabelled dataset
        :param size_seed: number of data points the learner begins with
        :return: ids of the data points to label
        """
        ids_to_add = []

        # enough labelled data
        if len(self.labelled_indices) >= size_seed:
            training_set = random.sample(self.labelled_indices, size_seed)
            # put remaining data in the unlabelled dataset to be the candidates to be labelled in the active
            # learning process
            self.unlabelled_indices += [data_id for data_id in self.labelled_indices if data_id not in training_set]
            self.labelled_indices = training_set

        else:
            nb_ids_to_add = int(size_seed - len(self.labelled_indices))
            ids_to_add = random.sample(self.unlabelled_indices, nb_ids_to_add)
            self.labelled_indices += ids_to_add
            self.unlabelled_indices = [data_id for data_id in self.unlabelled_indices if data_id not in ids_to_add]

        return ids_to_add

    def initialize_dataset_analysis(self, ratio_seed: float, first: bool):
        # flush out all the annotation
        if not first:
            self.test_set = self.convert_to_ids(self.test_set)
        Output.objects.filter(annotated_by_human=True).delete()
        self.step = 1
        self.labelled_indices = list(
            Output.objects.exclude(data_id__in=self.test_set).values_list('data_id', flat=True))
        self.labelled_indices, self.unlabelled_indices = sklearn.model_selection.train_test_split(self.labelled_indices,
                                                                                                  train_size=ratio_seed,
                                                                                                  shuffle=True)
        self.y_test = []
        self.test_set = self.convert_to_indices(self.test_set)
        self.labelled_indices = self.convert_to_indices(self.labelled_indices)
        self.unlabelled_indices = self.convert_to_indices(self.unlabelled_indices)

    def get_x(self, lst: List[int], format=None):
        return self.handler.get_x(lst, format)

    def get_y(self, lst: List[int], annotated_by_human=None) -> QuerySet:
        outputs = filter__in_preserve(Output.objects, 'data_id', self.convert_to_ids(lst))
        if annotated_by_human is not None:
            outputs = outputs.filter(annotated_by_human=annotated_by_human)
        return outputs

    def set_test_set(self, lst: List[int]):
        self.test_set = lst

    def get_data(self, lst: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        x = self.X[np.asarray(lst)]
        y = self.Y[np.asarray(lst)].astype(float)
        return x, y

    def next_step(self, data: List[int], annotated_by_human=None):
        """
        Update the value of the manager to go to the next step
        :param data: list of ids labelled
        :return: None
        """
        self.update_datasets(data, annotated_by_human)
        self.step += 1

    def update_datasets(self, data: List[int], annotated_by_human=None):
        converted_ids = self.convert_to_indices(data)
        self.labelled_indices += converted_ids
        new_y = self.get_y(converted_ids, annotated_by_human=annotated_by_human)
        for i in range(len(converted_ids)):
            data_id = converted_ids[i]
            self.unlabelled_indices.remove(data_id)
            self.Y[data_id] = new_y[i]

    def register_result(self, repeat=None, cross_val=None):
        if self.y_test == []:  # initialize the y_test
            self.y_test = self.Y[np.asarray(self.test_set)].astype(float)
        result = {
            'step': self.step,
            'query_strategy': self.strategy_name,
            'unlabelled_data': len(self.unlabelled_indices),
            'annotated_by_human': self.get_annotated_by_human(),
            'training_size': len(self.labelled_indices),
            'test_size': len(self.test_set)
        }
        if repeat is not None:
            result.update({'repeat': repeat})
        if cross_val is not None:
            result.update({'cross_val': cross_val})
        return result

    def train(self):
        X_train, Y_train = self.get_data(self.labelled_indices)
        self.model.fit(X_train, Y_train)

    def predict(self, lst):
        return self.model.predict(self.X[np.asarray(lst)])

    def performance_predict(self):
        self.y_predicted = self.predict(self.test_set)

    def query(self):
        query_index = self.strategy.select(label_index=self.labelled_indices,
                                           unlabel_index=self.unlabelled_indices,
                                           model=self.model,
                                           batch_size=self.batch_size)
        return self.convert_to_ids(query_index)

    def dump(self):
        dump(self.model, f'{settings.MEDIA_ROOT}/model.joblib.gz', compress='gzip')


class ClassificationManager(MLManager):

    def __init__(self, handler, model, batch_size, stopcriterion, stop_criterion_param, params):
        super().__init__(handler, model, batch_size, stopcriterion, stop_criterion_param, params)

    @staticmethod
    def get_type():
        nb_classes = Label.objects.distinct().count()
        if nb_classes > 2:
            type = "weighted"
        else:
            type = "binary"
        return type

    def get_y(self, lst: List[int], annotated_by_human=None) -> List[int]:
        outputs = super().get_y(lst, annotated_by_human)
        return list(outputs.values_list('label__classificationlabel__class_id', flat=True))

    @property
    def accuracy(self) -> float:
        return sklearn.metrics.accuracy_score(self.y_test, self.y_predicted)

    @property
    def precision(self) -> float:
        return sklearn.metrics.precision_score(self.y_test, self.y_predicted)

    @property
    def recall(self) -> float:
        return sklearn.metrics.recall_score(self.y_test, self.y_predicted)

    @property
    def f1_score(self) -> float:
        return sklearn.metrics.f1_score(self.y_test, self.y_predicted, average=self.get_type())

    @property
    def mcc(self) -> float:
        return sklearn.metrics.matthews_corrcoef(self.y_test, self.y_predicted)

    def register_result(self, repeat=None, cross_val=None) -> int:
        attributes = super().register_result(repeat, cross_val)
        attributes.update({
            'precision': self.precision,
            'recall': self.recall,
            'accuracy': self.accuracy,
            'f1_score': self.f1_score,
            'mcc': self.mcc
        })
        result_id = Result.objects.create(**attributes)
        return result_id


class DeepLearningClassification(ClassificationManager):
    
    def __init__(self, handler, model, batch_size, stopcriterion, stop_criterion_param, params):
        self.factory = ModelFactory(params['origin'])
        self.accelerator = OneAccelerator()
        self.model = None
        self.params = params
        self.first = True
        super().__init__(handler, model, batch_size, stopcriterion, stop_criterion_param, params)
        self.first = False
        self.labelled_indices.sort()
        self.unlabelled_indices.sort()

        # order should be conserved
        self.indices_to_ids = {k: v for k, v in zip(range(len(self.labelled_indices)+len(self.unlabelled_indices)), range(1,len(self.labelled_indices)+len(self.unlabelled_indices)+1))}
        self.ids_to_indices = {v: k for k, v in self.indices_to_ids.items()}

        all_set = self.convert_to_indices(self.labelled_indices+self.unlabelled_indices)
        all_set.sort()
        self.X = self.handler.get_x(all_set)
        self.Y = np.array(self.get_y(all_set))
    
    def get_x(self, lst, format='np'):
        if self.first:
            return []
        return super().get_x(lst, format)
    
    def get_y(self, lst, annotated_by_human=None):
        if self.first:
            return []
        return super().get_y(lst, annotated_by_human)
    
    def get_data(self, lst: List[int]):
        x = self.get_x(lst, format='torch')
        y = self.Y[np.asarray(lst)]

        return self.handler.get_dataloader(
            data=x, 
            labels=y, 
            batch_size=self.params['train_batch_size'], 
            shuffle=False
        )
    
    def update_datasets(self, data: List[int], annotated_by_human=None):
        super().update_datasets(data, annotated_by_human)
        self.labelled_indices.sort()
        self.unlabelled_indices.sort()

        # reset the model
        self.model = self.create_model()
    
    def create_model(self, model=None, params=None):
        #with self.accelerator.main_process_first():
        self.accelerator.clear()
        self.model = self.factory.produce(self.model)
        gc.collect()
        torch.cuda.empty_cache()

    def train(self):
        self.create_model()

        dataloader = self.get_data(self.labelled_indices)
        optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.params['learning_rate'])
        num_training_steps = self.params['num_epochs'] * len(dataloader)
        num_warm_steps = int(num_training_steps * self.params['warmup_proportion'])
        lr_scheduler = get_scheduler(
            "linear",
            optimizer=optimizer,
            num_warmup_steps=num_warm_steps,
            num_training_steps=num_training_steps,
        )

        logger.info("--- Setup data ---")
        logger.info(self.accelerator.num_processes)

        self.model, optimizer, dataloader, lr_scheduler = self.accelerator.prepare(
            self.model, optimizer, dataloader, lr_scheduler
        )

        logger.info("--- Begin training ---")

        for _ in range(self.params['num_epochs']):
            self.model.train()
            for batch in dataloader:
                self.model.zero_grad(set_to_none=True)
                outputs = self.model(**batch)
                loss = outputs.loss
                self.accelerator.backward(loss)

                optimizer.step()
                lr_scheduler.step()

        del optimizer, dataloader, lr_scheduler
        gc.collect()
        torch.cuda.empty_cache()

    def predict(self, lst, predictions_only=False):
        self.model.eval()
        dataloader = self.handler.get_dataloader(
            data=self.get_x(lst), 
            labels=None,
            batch_size=self.params['predict_batch_size'], 
            shuffle=False)
        dataloader = self.accelerator.prepare(dataloader)

        results = []
        ids_added = set()
        for batch in dataloader:
            with torch.no_grad():
                outputs = self.model(**batch)
                probabilities = softmax(outputs.logits, dim=1)
                predictions = torch.argmax(probabilities, dim=-1)
                if predictions_only:
                    predictions, indices = self.accelerator.gather((predictions, indices))
                    predictions, indices = predictions.tolist(), indices.tolist()
                    # to avoid adding information about indices already present, due to the loop of indices in the dataloader
                    new_predictions = []
                    for i in range(len(predictions)):
                        if indices[i] not in ids_added:
                            new_predictions.append(predictions[i])
                            ids_added.add(indices[i])
                    results.extend(new_predictions)
                else:
                    probabilities, predictions, indices = self.accelerator.gather((probabilities, predictions, indices))
                    probabilities, predictions, indices = probabilities.tolist(), predictions.tolist(), indices.tolist()
                    # to avoid adding information about indices already present, due to the loop of indices in the dataloader
                    new_predictions, new_probabilities = [], []
                    for i in range(len(predictions)):
                        if indices[i] not in ids_added:
                            new_predictions.append(predictions[i])
                            new_probabilities.append(probabilities[i])
                            ids_added.add(indices[i])
                    results.extend(zip(new_probabilities, new_predictions))

                    del new_probabilities

                del probabilities, predictions, outputs, new_predictions
                gc.collect()

        return results

    def predict_proba(self, lst):
        self.model.eval()
        dataloader = self.handler.get_dataloader(
            data=self.get_x(lst),
            labels=None,
            batch_size=self.params['predict_batch_size'], 
            shuffle=False)
        dataloader = self.accelerator.prepare(dataloader)

        results = []
        ids_added = set()
        for batch in dataloader:
            with torch.no_grad():
                outputs = self.model(**batch)
                probabilities = softmax(outputs.logits, dim=1)
                probabilities, indices = self.accelerator.gather((probabilities, indices))
                probabilities, indices = probabilities.tolist(), indices.tolist()

                # to avoid duplicates due to dataloader looping
                new_probabilities, new_indices = [],[]
                for i in range(len(probabilities)):
                    index = indices[i]
                    if index not in ids_added:
                        new_probabilities.append(probabilities[i])
                        ids_added.add(index)
                        new_indices.append(index)
                results.extend(zip(new_probabilities,new_indices))

                del probabilities, outputs, indices, new_indices, new_probabilities
                gc.collect()


        return results

    def get_embeddings(self, lst):
        self.model.eval()
        dataloader = self.handler.get_dataloader(
            data=self.get_x(lst),
            labels=None,
            batch_size=self.params['predict_batch_size'], 
            shuffle=False)
        dataloader = self.accelerator.prepare(dataloader)
       
        embeddings = []
        ids_added = set()
        for batch in dataloader:
            with torch.no_grad():
                outputs = self.model(**batch)
                embedding = torch.mean(outputs.hidden_states[-1], dim=1).squeeze()
                embedding, indices = self.accelerator.gather((embedding, indices))
                embedding, indices = embedding.tolist(), indices.tolist()

                new_embeddings, new_indices = [], []
                for i in range(len(embedding)):
                    index = indices[i]
                    if index not in ids_added:
                        new_embeddings.append(embedding[i])
                        ids_added.add(index)
                        new_indices.append(index)
                embeddings.extend(zip(new_embeddings, new_indices))

                del embedding, outputs, indices, new_embeddings, new_indices
                gc.collect()

        embeddings = np.asarray(embeddings)

        return embeddings
    
    def dump(self):
        self.factory.save_model(self.model)
