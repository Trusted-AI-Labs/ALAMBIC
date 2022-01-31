# Add here the output model for the different types : RE, segmentation, etc.
# To coordinate with the annotation

from django.db import models
from polymorphic.models import PolymorphicModel

from alambic_app.models.managers import LabelClassificationManager, LabelRegressionManager
from alambic_app.constantes import *


class Label(PolymorphicModel):
    type = models.CharField(max_length=3, choices=TASK_CHOICES)

    @property
    def data(self):
        response = {
            'task': self.get_type_display()
        }
        return response

    class Meta:
        app_label = 'alambic_app'


class ClassificationLabel(Label):
    class_id = models.IntegerField(unique=True)
    value = models.CharField(max_length=50, unique=True)

    objects = LabelClassificationManager()

    @property
    def data(self):
        response = super().data
        response.update(
            {
                'value': self.value
            }
        )
        return response

    def __str__(self):
        return f"Class {self.value}"


class RegressionLabel(Label):
    value = models.FloatField(unique=True)

    objects = LabelRegressionManager()

    @property
    def data(self):
        response = super().data
        response.update(
            {
                'value': str(self.value)
            }
        )
        return response
