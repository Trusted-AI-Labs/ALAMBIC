# Add here the different formats we could have (text, images, vectors)
# + eventually how they should be converted
# To coordinate with the features extraction

from django.db import models
from polymorphic.models import PolymorphicModel

from managers import DataManager
from labels import Label


class Data(PolymorphicModel):
    filename = models.FilePathField()  # unique for vector data, different for images and text
    objects = DataManager()

    @property
    def name(self):
        return self.filename

    @property
    def get_y(self):
        return self.y


class Text(Data):
    content = models.TextField()


class Output(models.Model):
    data = models.ForeignKey('Data', on_delete=models.CASCADE, related_name='y')
    label = models.ForeignKey('Label', on_delete=models.CASCADE)
    annotated_by_human = models.BooleanField(default=False)
