from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.models.text_mining import RelationType, EntityType


class NewRelationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML('<h3>Create a new Relation</h3>')
            ),
            Div(
                Field('name'),
                Field('color')
            )
        )

    class Meta:
        model = RelationType
        fields = '__all__'


class NewEntityForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                HTML('<h3>Create a new Entity</h3>')
            ),
            Div(
                Field('name'),
                Field('color'),
            )
        )

    class Meta:
        model = EntityType
        fields = '__all__'
