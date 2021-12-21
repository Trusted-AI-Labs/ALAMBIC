from django import forms
from django.core.exceptions import ValidationError

from django_select2.forms import Select2Widget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from crispy_forms.bootstrap import InlineCheckboxes

from csv import DictReader

from alambic_app.constantes import *


class CrispyWizardStep(forms.Form):
    """
    Base class for forms that use django-crispy-forms and are used in a form wizard
    Applies common initialization steps
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'bold'


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


### DATA SPECIFIC PROCESSING

class PreprocessingText(CrispyWizardStep):
    ANNOTATORS_CHOICES = [
        ('tokenize', 'Tokenization'),
        ('ssplit', 'Sentence Splitting'),
        ('pos', 'POS Tagger'),
        ('lemma', 'Lemma'),
        ('ner', 'Named Entity Tag (non biomedical)'),
        ('ddparse', 'Dependency Parse Tree'),
        ('parse', 'Constituency and Dependency Parse Tree'),
        ('coref', "Coreference Resolution"),
    ]

    annotators = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=ANNOTATORS_CHOICES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Processing linked to the data</h2>'),
                InlineCheckboxes('annotators')
            )
        )


### CHOICE MODEL

class ClassificationModel(CrispyWizardStep):
    model_choice = forms.ChoiceField(
        choices=CLASSIFICATION_MODELS_CHOICES,
        required=True,
        widget=Select2Widget(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Choose a model</h2>'),
                Field('model_choice')
            )
        )


### MODEL-SPECIFIC PARAMETERS

class SVCClassification(CrispyWizardStep):
    C = forms.FloatField(
        min_value=0,
        max_value=10,
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Support Vector Classification</h2>'),
                Field('C')
            )
        )


class RFClassification(CrispyWizardStep):
    # TODO Inheritance for the different models and then specifialize according to task ?

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


### ACTIVE LEARNING

class ActiveLearningParameters(CrispyWizardStep):
    query_strategy = forms.ChoiceField(
        choices=AL_ALGORITHMS_CHOICES,
        required=True,
        widget=Select2Widget(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0
            }
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters of the Active learning</h2>'),
                Field('query_strategy')
            )
        )
