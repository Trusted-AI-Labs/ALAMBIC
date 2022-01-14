from random import sample

from alambic_app.machine_learning.preprocessing import *
from alambic_app.models.results import Result


class MLManager:
    """
    Class to handle the performance
    """

    def __init__(self, model, ):
        self.step = 1
        self.model = model
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
            ids_to_add = sample(self.unlabelled_dataset, nb_ids_to_add)
            self.test_set = ids_to_add.copy()
            self.unlabelled_dataset = [id for id in self.unlabelled_dataset if id not in ids_to_add]
        elif current_ratio > ratio:
            nb_ids_to_sample = (total_data * ratio)
            self.test_set = sample(self.labelled_dataset, nb_ids_to_sample)
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
            self.training_set = sample(self.training_set, size_seed)
            return []
        else:
            nb_ids_to_add = size_seed - len(self.training_set)
            ids_to_add = sample(self.unlabelled_dataset, nb_ids_to_add)
            self.training_set += ids_to_add
            self.unlabelled_dataset = [id for id in self.unlabelled_dataset if id not in ids_to_add]
            return ids_to_add

    def add_to_training(self, data_id):
        self.training_set += [data_id]

    def get_y(self, lst):
        outputs = Output.objects.filter(data_id__in=lst)
        return outputs

    def add_to_labelled(self, data_id):
        self.labelled_dataset += [data_id]
        self.unlabelled_dataset.remove(data_id)

    def set_test_set(self, lst):
        self.test_set = lst

    def register_result(self):
        raise NotImplementedError("This is only implemented in subclasses")

    def launch_ml(self):
        self.model.fit()


class ClassificationManager(MLManager):

    def __init__(self, model):
        super().__init__(model)
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
