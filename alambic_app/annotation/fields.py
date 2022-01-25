from crispy_forms.bootstrap import StrictButton
from crispy_forms.layout import HTML, Div, Field, Layout
from django.core.exceptions import ValidationError
from django.forms import ModelChoiceField

from alambic_app.models.labels import ClassificationLabel

from alambic_app.annotation.widgets import ClassificationLabelModelSelect


class ClassificationLabelSelectField(ModelChoiceField):
    """
    Custom select field to choose a variant that will be associated to a new combination.
    Allows creation of a new variant through the VariantModelSelect widget.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         widget=ClassificationLabelModelSelect(
                             attrs={
                                 'data-minimum-input-length': 0,
                                 'data-placeholder': 'Select or create a classification label',
                                 'class': 'label-select'
                             }),
                         queryset=ClassificationLabel.objects.all(),
                         error_messages={
                             'incomplete': 'Select the label to attribute to the data or create a new one'},
                         **kwargs)

    def clean(self, value):
        """
        Override that extracts eventual parsing errors from the widget.
        """
        if self.widget.error is not None:
            raise ValidationError(self.widget.error)
        # print(f'Value to clean: {value}')
        return super().clean(value)
