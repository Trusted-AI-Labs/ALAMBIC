import logging

from polymorphic.models import PolymorphicManager


class TextManager(PolymorphicManager):

    def create_instance(self, **kwargs):
        pass


class ImageManager(PolymorphicManager):
    pass


### LABELS

class LabelManager(PolymorphicManager):
    model = None

    def find_instance(self, **kwargs):
        return self.filter(**kwargs)

    def create_instance(self, **kwargs):

        instance = self.find_instance(**kwargs)

        if len(instance) > 0:
            return instance[0]
        else:
            return self.create(**kwargs)


class LabelClassificationManager(LabelManager):
    model = 'ClassificationLabel'


class LabelRegressionManager(LabelManager):
    model = 'RegressionLabel'
