from django.db import models


class Result(models.Model):
    # TODO : Polymorphic model according to task ?

    step = models.IntegerField()

    # Info about the ratio of labelled vs unlabelled
    unlabelled_data = models.IntegerField()
    annotated_by_human = models.IntegerField()
    training_size = models.IntegerField()
    test_size = models.IntegerField()

    # Performance indicators
    cross_val = models.BooleanField()  # done with cross-val ?
    precision = models.FloatField(null=True)
    recall = models.FloatField(null=True)
    accuracy = models.FloatField(null=True)
    mcc = models.FloatField(null=True)
    f1_score = models.FloatField(null=True)
    mse = models.FloatField(null=True)

    class Meta:
        app_label = 'alambic_app'
        db_table = 'result'
