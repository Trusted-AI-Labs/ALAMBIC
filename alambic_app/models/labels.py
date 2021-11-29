# Add here the output model for the different types : RE, segmentation, etc.
# To coordinate with the annotation

from django.db import models


class Label(models.Model):
    TASKS_CHOICES = (
        ('C', 'Classification'),  # also NER and RE
        ('R', 'Regression'),
    )
    type = models.CharField(max_length=1, choices=TASKS_CHOICES)
    value = models.TextField(null=True, blank=False)

    def get_value(self):
        """
        Convert the value into the desired format according to the type of task
        :return: value in the desired format
        """
        if self.type == 'R':
            return float(self.value)
        return self.value
