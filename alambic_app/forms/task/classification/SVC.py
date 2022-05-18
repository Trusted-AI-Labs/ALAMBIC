from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep
from alambic_app.constantes import KERNELS_CHOICES


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

    kernel = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=KERNELS_CHOICES,
        required=False,
        initial='rbf'
    )

    gamma = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ('auto', 'auto'),
            ('scale', 'scale')
        ],
        required=False,
        initial='scale'
    )

    degree = forms.IntegerField(
        min_value=1,
        max_value=10,
        required=False,
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 1
            }
        ),
        initial = 3
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Support Vector Classification</h2>'),
                HTML('Check the full documentation <a href="https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html">here</a>'),
                Field('kernel'),
                Field('C'),
                Field('gamma'),
                Field('degree')
            )
        )

    def clean(self):
        clean_data = super().clean()
        clean_data['probability'] = True  # to be able to use predict_proba in the query strategies
        return clean_data
