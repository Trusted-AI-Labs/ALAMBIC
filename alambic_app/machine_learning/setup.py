import numpy as np
import random
import sklearn

from typing import List, Dict, Any

from django.db.models import QuerySet
from modAL.uncertainty import entropy_sampling, margin_sampling, uncertainty_sampling

from alambic_app.active_learning import stopcriterion
from alambic_app.active_learning import strategies
from alambic_app.machine_learning.preprocessing import PreprocessingHandler

from alambic_app.models.input_models import Output, Data, Label
from alambic_app.models.results import Result

AL_ALGORITHMS_MATCH = {
    'RS': strategies.random_sampling,
    'US': uncertainty_sampling,
    'MS': margin_sampling,
    'ES': entropy_sampling,
}

MODELS_MATCH = {
    'SVC': sklearn.svm.SVC,
    'RF': sklearn.ensemble.RandomForestClassifier,
}

STOP_CRITERION_MATCH = {
    'budget': stopcriterion.budget_reached,
    'accuracy': stopcriterion.accuracy_reached
}


class MLManager:
    """
    Class to handle the performance
    """

    def __init__(self, handler: PreprocessingHandler, model: str, strategy: str, stopcriterion: str,
                 stopcriterion_param: Any, params: dict):
        self.step = 1
        self.model = self.create_model(model, params)
        self.handler = handler
        self.strategy = AL_ALGORITHMS_MATCH[strategy]
        self.stopcriterion = STOP_CRITERION_MATCH[stopcriterion]
        self.goal = stopcriterion_param
        self.unlabelled_dataset, self.training_set = self.get_labelled_dataset()
        self.test_set = []
        self.y_test = []
        self.y_predicted = []

    @staticmethod
    def create_model(model: str, params: Dict[str, Any]):
        """
        Create the model to train with the chosen parameters
        :param model: name of the model found in MODELS_MATCH as key
        :param params: parameters of the model
        :return: parameterized model
        """
        # TODO add here parameters if necessary according to the model
        return MODELS_MATCH[model](**params)

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

    def initialize_dataset(self, ratio: float, size_seed: int) -> List[int]:
        """
        Split into training set and test set, assign them to training_set and test_set
        :param ratio: percentage of the total dataset dedicated to the test set
        :param size_seed: number of data points the learner will begin with in the active learning algorithm
        :return: list of ints, ids of data to label
        """
        total_data = Data.objects.all().count()
        current_ratio = len(self.training_set) / total_data
        ids_to_add = []

        # missing labelled data
        if current_ratio < ratio:
            nb_ids_to_add = int((total_data * ratio) - len(self.training_set))
            ids_to_add = random.sample(self.unlabelled_dataset, nb_ids_to_add)
            self.test_set = ids_to_add.copy()
            self.unlabelled_dataset = [data_id for data_id in self.unlabelled_dataset if data_id not in ids_to_add]

        elif current_ratio > ratio:
            nb_ids_to_sample = int(total_data * ratio)
            self.test_set = random.sample(self.training_set, nb_ids_to_sample)
            self.training_set = [data_id for data_id in self.training_set if data_id not in self.test_set]

        # reduce the training set to the original size
        ids_to_add += self.set_seed(size_seed)

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
        if len(self.training_set) >= size_seed:
            training_set = random.sample(self.training_set, size_seed)
            # put remaining data in the unlabelled dataset to be the candidates to be labelled in the active
            # learning process
            self.unlabelled_dataset += [data_id for data_id in self.training_set if data_id not in training_set]
            self.training_set = training_set

        else:
            nb_ids_to_add = int(size_seed - len(self.training_set))
            ids_to_add = random.sample(self.unlabelled_dataset, nb_ids_to_add)
            self.training_set += ids_to_add
            self.unlabelled_dataset = [data_id for data_id in self.unlabelled_dataset if data_id not in ids_to_add]

        return ids_to_add

    def get_y(self, lst: List[int]) -> QuerySet:
        outputs = Output.objects.filter(data_id__in=lst)
        return outputs

    def set_test_set(self, lst: List[int]):
        self.test_set = lst

    def get_y_test(self):
        self.y_test = self.get_y(self.test_set)

    def get_data(self, lst: List[int]) -> (np.ndarray, np.ndarray):
        x = []
        y = np.array(self.get_y(lst))
        for data_id in lst:
            x.append(self.handler[data_id])
        x = np.array(x)
        return x, y

    def next_step(self, data: List[int]):
        """
        Update the value of the manager to go to the next step
        :param data: list of ids labelled
        :return: None
        """
        self.update_datasets(data)
        self.step += 1

    def update_datasets(self, data: List[int]):
        self.training_set += data
        for data_id in data:
            self.unlabelled_dataset.remove(data_id)

    def register_result(self):
        return {
            'step': self.step,
            'unlabelled_data': len(self.unlabelled_dataset),
            'annotated_by_human': self.get_annotated_by_human(),
            'training_size': len(self.training_set),
            'test_size': len(self.test_set)
        }

    def train(self):
        X_train, Y_train = self.get_data(self.training_set)
        self.model.fit(X_train, Y_train)

    def predict(self):
        self.y_predicted = self.model.predict(self.test_set)

    def query(self) -> int:
        unlabelled_X, _ = self.get_data(self.unlabelled_dataset)
        query_index = self.strategy(self.model, unlabelled_X)
        return self.unlabelled_dataset[query_index]


class ClassificationManager(MLManager):

    def __init__(self, handler, model, strategy, stopcriterion, stop_criterion_param, params):
        super().__init__(handler, model, strategy, stopcriterion, stop_criterion_param, params)
        self.type_classification = self.get_type()

    @staticmethod
    def get_type():
        nb_classes = Label.objects.distinct().count()
        if nb_classes > 2:
            type = "weighted"
        else:
            type = "binary"
        return type

    def get_y(self, lst: List[int]) -> List[int]:
        outputs = super().get_y(lst)
        return [outputs.get(data_id=data_id).label.class_id for data_id in lst]

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
        return sklearn.metrics.f1_score(self.y_test, self.y_predicted, average=self.type_classification)

    @property
    def mcc(self) -> float:
        return sklearn.metrics.matthews_corrcoef(self.y_test, self.y_predicted)

    def register_result(self) -> int:
        attributes = super().register_result()
        attributes.update({
            'precision': self.precision,
            'recall': self.recall,
            'accuracy': self.accuracy,
            'f1_score': self.f1_score,
            'mcc': self.mcc
        })
        result_id = Result.objects.create(**attributes)
        return result_id
