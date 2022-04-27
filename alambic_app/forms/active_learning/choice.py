from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class ActiveLearningTaskChoice(CrispyWizardStep):
    type_learning = forms.ChoiceField(
        choices=[
            ('model', 'Train a model'),
            ('analysis', 'Analyse the active learning process')
        ]
    )

    batch_size = forms.IntegerField(
        min_value=1,
        required=True,
        help_text='Number of queries annotated each step of the active learning process'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Type of active learning process and common parameters</h2>'),
                Field('type_learning'),
                Field('batch_size')
            )
        )
