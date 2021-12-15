# Add here the different formats we could have (text, images, vectors)
# + eventually how they should be converted
# To coordinate with the features extraction

import numpy as np

from PIL import Image

from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField

from alambic_app.models.managers import TextManager, ImageManager
from alambic_app.models.labels import Label


class Data(PolymorphicModel):
    filename = models.TextField()  # unique for vector data, different for images and text

    @property
    def name(self):
        return self.filename

    @property
    def output(self):
        return self.output_set.all()[0]

    @property
    def data(self):
        response = {
            'filename': self.filename
        }
        response.update(self.output.data_content)

        return response

    class Meta:
        app_label = 'alambic_app'


class Text(Data):
    content = models.TextField()
    objects = TextManager()

    @property
    def data(self):
        response = super().data
        response.update(
            {
                'content': self.content
            }
        )
        return response

    class Meta:
        db_table = 'text_data'


class Image(Data):
    content = ArrayField(
        ArrayField(
            ArrayField(
                models.FloatField()
            )
        )
    )
    objects = ImageManager()

    @property
    def data(self):
        response = super().data
        response.update(
            {
                'content': self.content
            }
        )
        return response

    def as_image(self):
        return Image.fromarray(self.as_array())

    def as_array(self):
        return np.asarray(self.content).astype(np.uint8)

    class Meta:
        db_table = 'image_data'


class Output(models.Model):
    data = models.ForeignKey('Data', on_delete=models.CASCADE)
    label = models.ForeignKey('Label', on_delete=models.CASCADE, null=True)
    annotated_by_human = models.BooleanField(
        default=False)  # to allow the co-existence of the manual annotation and the automatic one
    predicted = models.BooleanField(default=False)  # ground truth or produced by model

    @property
    def data_content(self):
        response = dict()
        response.update(self.label.data)
        return response

    class Meta:
        app_label = 'alambic_app'
        db_table = 'output'
        unique_together = ['data', 'label', 'annotated_by_human', 'predicted']
