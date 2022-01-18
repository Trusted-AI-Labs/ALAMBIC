import numpy as np

from modAL.uncertainty import entropy_sampling, margin_sampling, uncertainty_sampling

from alambic_app.machine_learning.preprocessing import *
from alambic_app.active_learning.stopcriterion import *
from alambic_app.active_learning.strategies import random_sampling
from alambic_app.models.results import Result

STRATEGY_MATCH = {
    'random': random_sampling,
    'uncertainty': uncertainty_sampling,
    'margin': margin_sampling,
    'entropy': entropy_sampling
}


class MLManager:
    """
    Class to handle the performance
    """

    def __init__(self, model, handler, strategy, stopcriterion):
        self.step = 1
        self.model = model
        self.handler = handler
        self.strategy = STRATEGY_MATCH[strategy]
        self.stopcriterion = stopcriterion
        self.unlabelled_dataset, self.labelled_dataset = self.get_labelled_dataset()
        self.training_set = []
        self.test_set = []
        self.y_test = []
        self.y_predicted = []

    def get_labelled_dataset(self):
        unlabelled = list(Output.objects.filter(label__isnull=True).values_list('data_id', flat=True))
        labelled = list(Output.objects.excludde(data_id__in=unlabelled).values_list('data_id', flat=True))
        return labelled, unlabelled

    def initialize_dataset(self, ratio, size_seed):
        """
        Split into training set and test set, assign them to training_set and test_set
        :param ratio: float
        :param size_seed: int, number of data points the learner will begin with in the active learning algorithm
        :return: list of ints, ids of data to label
        """
        total_data = Data.objects.all().count()
        current_ratio = len(self.labelled_dataset) / total_data
        ids_to_add = []
        # missing labelled data
        if current_ratio < ratio:
            nb_ids_to_add = (total_data * ratio) - len(self.labelled_dataset)
            ids_to_add = np.random.sample(self.unlabelled_dataset, nb_ids_to_add)
            self.test_set = ids_to_add.copy()
            self.unlabelled_dataset = [id for id in self.unlabelled_dataset if id not in ids_to_add]
        elif current_ratio > ratio:
            nb_ids_to_sample = (total_data * ratio)
            self.test_set = np.random.sample(self.labelled_dataset, nb_ids_to_sample)
            self.training_set = [id for id in self.labelled_dataset if id not in self.test_set]

        ids_to_add += self.set_seed(size_seed)
        return ids_to_add

    def set_seed(self, size_seed):
        """
        Get the seed for the active learning algorithm.
        Set the training set to have an initial size corresponding to the initial size
        :param size_seed: int, number of data points the learner begins with
        :return: list of ints, ids of the data points to label
        """
        if len(self.training_set) >= size_seed:
            self.training_set = np.random.sample(self.training_set, size_seed)
            return []
        else:
            nb_ids_to_add = size_seed - len(self.training_set)
            ids_to_add = np.random.sample(self.unlabelled_dataset, nb_ids_to_add)
            self.training_set += ids_to_add
            self.unlabelled_dataset = [id for id in self.unlabelled_dataset if id not in ids_to_add]
            return ids_to_add

    def get_y(self, lst):
        outputs = Output.objects.filter(data_id__in=lst)
        return outputs

    def set_test_set(self, lst):
        self.test_set = lst

    def get_y_test(self):
        self.y_test = self.get_y(self.test_set)

    def get_data(self, lst):
        x = []
        y = np.array(self.get_y(lst))
        for id in lst:
            x.append(self.handler[id])
        x = np.array(x)
        return x, y

    def next_step(self, data_id):
        self.training_set += [data_id]
        self.labelled_dataset += [data_id]
        self.unlabelled_dataset.remove(data_id)
        self.step += 1

    def register_result(self):
        return {
            'step': self.step,
            'labelled_data': len(self.labelled_dataset),
            'unlabelled_data': len(self.unlabelled_dataset),
            'annotated_by_human': Output.objects.filter(annotated_by_human=True).count(),
            'training_size': len(self.training_set),
            'test_size': len(self.test_set)
        }

    def train(self):
        X_train, Y_train = self.get_data(self.training_set)
        self.model.fit(X_train, Y_train)

    def predict(self):
        self.y_predicted = self.model.predict(self.test_set)

    def query(self):
        unlabelled_X, _ = self.get_data(self.unlabelled_dataset)
        query_result = self.strategy(self.model, unlabelled_X)


class ClassificationManager(MLManager):

    def __init__(self, model, handler, strategy):
        super().__init__(model, handler, strategy)
        self.type_classification = self.get_type()

    def get_type(self):
        nb_classes = Label.objects.distinct().count()
        if nb_classes > 2:
            type = "weighted"
        else:
            type = "binary"
        return type

    def get_y(self, lst):
        outputs = super().get_y(lst)
        return [outputs.get(data_id=id).label.class_id for id in lst]

    @property
    def accuracy(self):
        return sklearn.metrics.accuracy_score(self.y_test, self.y_predicted)

    @property
    def precision(self):
        return sklearn.metrics.precision_score(self.y_test, self.y_predicted)

    @property
    def recall(self):
        return sklearn.metrics.recall_score(self.y_test, self.y_predicted)

    @property
    def f1_score(self):
        return sklearn.metrics.f1_score(self.y_test, self.y_predicted, average=self.type_classification)

    @property
    def mcc(self):
        return sklearn.metrics.matthews_corrcoef(self.y_test, self.y_predicted)

    def register_result(self):
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
