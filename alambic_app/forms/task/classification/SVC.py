from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class SVCClassification(CrispyWizardStep):
    C = forms.FloatField(
        min_value=0,
        max_value=10,
        required=True,
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 0.1
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Support Vector Classification</h2>'),
                Field('C')
            )
        )

    def clean(self):
        clean_data = super().clean()
        clean_data['probability'] = True  # to be able to use predict_proba in the query strategies
        return clean_data
