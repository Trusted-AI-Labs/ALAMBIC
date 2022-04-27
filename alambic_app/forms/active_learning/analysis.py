from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.constantes import AL_ALGORITHMS_CHOICES
from alambic_app.forms.forms import CrispyWizardStep


class ActiveLearningAnalysisParameters(CrispyWizardStep):
    query_strategies = forms.MultipleChoiceField(
        choices=AL_ALGORITHMS_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )

    cross_validation = forms.IntegerField(
        min_value=5,
        help_text="Number of folds for the cross-validation"
    )

    repeat_operations = forms.IntegerField(
        min_value=1,
        help_text="Number of times the learning process is repeated with the same test set"
    )

    ratio_seed = forms.FloatField(
        min_value=0.1,
        max_value=1,
        required=True,
        help_text='Ratio of the dataset which will be considered as the starting labelled dataset',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 0.01
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Active learning analysis</h2>')
            ),
            Div(
                InlineCheckboxes('query_strategies'),
                css_class='form-row'
            ),
            Div(
                Field('cross_validation'),
                Field('repeat_operations'),
                Field('ratio_seed')
            ),
        )
