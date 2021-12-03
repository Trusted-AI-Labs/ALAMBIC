from django import forms
from django.core.exceptions import ValidationError

from django_select2.forms import Select2Widget

from csv import DictReader

from alambic_app.constantes import *


class GeneralInfoInputForm(forms.Form):
    input_file = forms.FilePathField(
        path=DATA_PATH,
        match=r"[a-zA-Z0-9_]*\.tsv"
    )
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

    def clean(self):
        cleaned_data = super().clean()
        try:
            infile = open(cleaned_data.get('input_file'))
        except FileNotFoundError:
            raise ValidationError("File Not found", code='not_found')

        reader = DictReader(infile, delimiter='\t')
        if 'label' not in reader.fieldnames:
            raise ValidationError('Missing a label column in the file', code='invalid')
        if 'file' not in reader.fieldnames and 'content' not in reader.fieldnames:
            raise ValidationError(
                'Missing a column with the content or the path to the file to import ("content" or "file" columns)',
                code='invalid')
