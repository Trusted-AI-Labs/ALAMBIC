from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class RFClassification(CrispyWizardStep):
    # TODO Inheritance for the different models and then specialize according to task ?

    number_trees = forms.IntegerField(
        max_value=100,
        min_value=1,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Random Forest Classification</h2>'),
                Field('number_trees')
            )
        )
