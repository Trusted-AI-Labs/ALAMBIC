from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms
from django_select2.forms import Select2Widget

from alambic_app.constantes import CLASSIFICATION_MODELS_CHOICES
from alambic_app.forms.forms import CrispyWizardStep


class ClassificationModel(CrispyWizardStep):
    model_choice = forms.ChoiceField(
        choices=CLASSIFICATION_MODELS_CHOICES,
        required=True,
        widget=Select2Widget(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Choose a model</h2>'),
                Field('model_choice')
            )
        )
