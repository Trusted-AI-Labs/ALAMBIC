from django.db import models


class Result(models.Model):
    # TODO : Polymorphic model according to task ?

    step = models.IntegerField()

    # Info about the ratio of labelled vs unlabelled
    unlabelled_data = models.IntegerField()
    annotated_by_human = models.IntegerField()
    training_size = models.IntegerField()
    test_size = models.IntegerField()

    # model information
    query_strategy = models.TextField(null=True)

    # Performance indicators
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    mcc = models.FloatField(null=True)
    f1_score = models.FloatField(null=True)
    mse = models.FloatField(null=True)

    def get_nice_format(self):
        return {
            'Unlabelled data': self.unlabelled_data,
            'Data labelled by human': self.annotated_by_human,
            'Training size': self.training_size,
            'Test size': self.test_size,
            'Precision': self.precision,
            'Recall': self.recall,
            'Accuracy': self.accuracy,
            'MCC': self.mcc,
            'F1 score': self.f1_score,
            'MSE': self.mse
        }

    class Meta:
        app_label = 'alambic_app'
        db_table = 'result'
        ordering = ['step']
