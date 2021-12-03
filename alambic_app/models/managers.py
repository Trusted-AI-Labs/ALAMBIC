import logging

from PIL import Image
from numpy import asarray

from polymorphic.models import PolymorphicManager


class TextManager(PolymorphicManager):

    def create_instance(self, **kwargs):
        with open(kwargs['filename']) as infile:
            kwargs['content'] = ' '.join(infile.readlines())  # just a big long string

        return self.create(**kwargs)


class ImageManager(PolymorphicManager):

    def create_instance(self, **kwargs):
        kwargs['content'] = asarray(Image.open(kwargs['filename'])).tolist()  # convert in numpy array

        return self.create(**kwargs)


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

    def get_id(self, value):
        """
        :return: The ID that will be assigned to the new class label
        :rtype: int
        """
        instance = self.filter(value=value)
        if len(instance) > 0:
            return instance[0].class_id

        last_id = self.get_queryset().order_by('class_id').last().class_id if len(self.get_queryset()) > 0 else -1
        return last_id + 1

    def create_instance(self, **kwargs):
        kwargs['class_id'] = self.get_id(kwargs['value'])

        return super().create_instance(**kwargs)


class LabelRegressionManager(LabelManager):
    model = 'RegressionLabel'

    def create_instance(self, **kwargs):
        kwargs['value'] = float(kwargs['value'])

        return super().create_instance(**kwargs)
