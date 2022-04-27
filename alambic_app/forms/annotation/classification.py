from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field, Submit
from django import forms

from alambic_app.annotation.fields import ClassificationLabelSelectField


class ClassificationAnnotationForm(forms.Form):
    label = ClassificationLabelSelectField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'bold'
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Label of the data</h2>'),
                Field('label'),
                css_class='justify-content-center'
            ),
            Submit('submit', 'Submit')
        )

    def clean(self):
        return super().clean()
