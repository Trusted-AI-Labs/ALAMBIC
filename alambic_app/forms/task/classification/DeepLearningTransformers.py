from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class DeepLearningClassification(CrispyWizardStep):
    origin = forms.CharField(
        required=True,
        help_text="Name for the transformer model"
    )

    learning_rate = forms.FloatField(
        default = 1e-5
    )

    num_epochs = forms.IntegerField(

    )

    train_batch_size = forms.IntegerField()
    predict_batch_size = forms.IntegerField()

    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Link for the Transformers model on Hugging Face</h2>'),
                Field('origin'),
                Field('learning_rate'),
                Field('num_epochs'),
                Field('train_batch_size'),
                Field('predict_batch_size')
            )
        )