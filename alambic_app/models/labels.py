# Add here the output model for the different types : RE, segmentation, etc.
# To coordinate with the annotation

from django.db import models
from polymorphic.models import PolymorphicModel
from alambic_app.models.managers import LabelClassificationManager, LabelRegressionManager


class Label(PolymorphicModel):
    TASKS_CHOICES = (
        ('C', 'Classification'),  # also NER and RE
        ('R', 'Regression'),
    )
    type = models.CharField(max_length=3, choices=TASKS_CHOICES)


class ClassificationLabel(Label):
    class_id = models.IntegerField(unique=True)
    value = models.CharField(max_length=50, unique=True)

    objects = LabelClassificationManager()


class RegressionLabel(Label):
    value = models.FloatField(unique=True)

    objects = LabelRegressionManager()
