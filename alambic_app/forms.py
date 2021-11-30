from django import forms
from django_select2.forms import Select2Widget


class GeneralInfoInputForm(forms.Form):
    DATA_CHOICES = [
        ('Text', 'Text'),
        ('Image', 'Image')
    ]
    TASK_CHOICES = [
        ('C', 'Classification'),
        ('R', 'Regression')
    ]

    input_file = forms.FileField(widget=forms.FileInput(attrs={'accept': '.tsv'}))
    model = forms.ChoiceField(
        choices=DATA_CHOICES,
        widget=Select2Widget(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0
            }
        ),
        required=True
    )
    task = forms.ChoiceField(
        choices=TASK_CHOICES,
        widget=Select2Widget(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0
            }
        ),
        required=True
    )
