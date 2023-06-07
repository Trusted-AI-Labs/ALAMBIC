from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class DeepLearningClassification(CrispyWizardStep):
    origin = forms.CharField(
        required=True,
        help_text="Name for the transformer model"
    )

    learning_rate = forms.FloatField(
        min_value=0,
        max_value=1,
        initial = 1e-5,
        required=True,
        help_text='Learning rate of the model',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 0.0001
            }
        )
    )

    num_epochs = forms.IntegerField(
        min_value=1,
        max_value=1000,
        initial=10,
        required=True,
        help_text='Number of epochs',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 1
            }
        )
    )

    train_batch_size = forms.IntegerField(
        min_value=1,
        max_value=1000,
        initial=16,
        required=True,
        help_text='Size of the batches during training',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 1
            }
        )
    )
    predict_batch_size = forms.IntegerField(
        min_value=1,
        max_value=1000,
        initial=32,
        required=True,
        help_text='Size of the batches during prediction and evaluation',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 1
            }
        )
    )

    
    
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