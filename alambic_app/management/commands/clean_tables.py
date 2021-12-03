from django.core.management.base import BaseCommand
from alambic_app.models import input_models, labels


# add here the new tables as they are built

class Command(BaseCommand):
    args = 'None'
    help = 'Clean the data in the tables'

    def handle(self, *args, **options):
        # Input models
        input_models.Text.objects.all().delete()
        input_models.Image.objects.all().delete()

        input_models.Output.objects.all().delete()

        # Labels
        labels.ClassificationLabel.objects.all().delete()
        labels.RegressionLabel.objects.all().delete()
