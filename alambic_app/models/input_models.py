# Add here the different formats we could have (text, images, vectors)
# + eventually how they should be converted
# To coordinate with the features extraction

from django.db import models
from polymorphic.models import PolymorphicModel
from django.contrib.postgres.fields import ArrayField

from alambic_app.models.managers import TextManager, ImageManager


class Data(PolymorphicModel):
    filename = models.FilePathField()  # unique for vector data, different for images and text

    @property
    def name(self):
        return self.filename

    @property
    def get_y(self):
        return self.y


class Text(Data):
    content = models.TextField()
    objects = TextManager()

    class Meta:
        db_table = 'text_data'


class Image(Data):
    content = ArrayField(ArrayField(models.FloatField()))
    objects = ImageManager()

    class Meta:
        db_table = 'image_data'


class Output(models.Model):
    data = models.ForeignKey('Data', on_delete=models.CASCADE, related_name='y')
    label = models.ForeignKey('Label', on_delete=models.CASCADE, null=True)
    annotated_by_human = models.BooleanField(default=False)

    class Meta:
        db_table = 'output'
        unique_together = ['data', 'label', 'annotated_by_human']
