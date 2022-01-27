from django import forms
from django.core.exceptions import ValidationError

from django_select2.forms import Select2Widget

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML, Field
from crispy_forms.bootstrap import InlineCheckboxes, InlineRadios, Accordion, AccordionGroup

from csv import DictReader

from alambic_app.constantes import *
from alambic_app.annotation.fields import ClassificationLabelSelectField


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
    vectorizer = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=FEATURES_TEXT_CHOICES,
        required=False
    )

    ngram_min = forms.IntegerField(
        label='Min n-gram',
        help_text='Minimum size for the n-gram analysis',
        required=False,
        initial=1
    )
    ngram_max = forms.IntegerField(
        label='Max n-gram',
        help_text='Maximal size for the n-gram analysis',
        required=False,
        initial=1
    )
    max_features = forms.IntegerField(
        label='Maximum number of features',
        help_text='Build a vocabulary that only consider the top max_features ordered by term frequency across the corpus',
        required=False
    )

    preprocessing_steps = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=PREPROCESSING_TEXT_CHOICES,
        required=False,
        help_text="Available preprocessing that can be done on the text before feature extraction"
    )

    annotators = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=ANNOTATORS_CHOICES,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Optional preprocessing steps</h2><br><br>'),
                css_class='form-row'
            ),
            Div(
                InlineCheckboxes('preprocessing_steps'),
                css_class='form-row'
            ),
            Div(
                HTML('<h2>Features for your model</h2>'),
                css_class='form-row'
            ),
            Accordion(
                AccordionGroup(
                    'Vectorizers',
                    InlineRadios('vectorizer'),
                    Div(
                        Div(
                            HTML(
                                '<span class="align-bottom"> With the range value for the analyzed n-grams from </span>'),
                            css_class='col-3'
                        ),
                        Div('ngram_min', css_class='col-3'),
                        Div(
                            HTML('<span class="align-bottom"> to </span>'),
                            css_class='col-3'
                        ),
                        Div('ngram_max', css_class='col-3'),
                        css_class='form-row'
                    ),
                    Field('max_features')
                ),
                AccordionGroup(
                    'Convert in a tree',
                    InlineRadios('annotators'),
                )
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        operations = dict()
        tree = cleaned_data.get('annotators')
        vector = cleaned_data.get('vectorizer')
        preprocess = cleaned_data.get('preprocessing_steps')
        if tree != '' and vector != '':
            self.add_error('annotators', 'Only one type of features can be selected')
            self.add_error('vectorizer', 'Only one type of features can be selected')

        if 'lemma' in preprocess:
            operations['client'] = 'tokenize,mwt,pos,lemma'

        if vector:
            operations[vector] = {'ngram_range': (cleaned_data['ngram_min'], cleaned_data['ngram_max'])}
            if 'stop_words' in preprocess:
                operations[vector]['stop_words'] = 'english'
            if cleaned_data.get('max_features') is not None:
                operations[vector]['max_features'] = cleaned_data.get('max_features')

        if tree:
            operations['client'] = f'tokenize,mwt,pos,lemma,{tree}'

        return operations

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
        required=True,

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

    ratio_test = forms.FloatField(
        min_value=0,
        max_value=1,
        required=True,
        help_text='Percentage of the dataset for the test set'
    )

    size_seed = forms.IntegerField(
        min_value=1,
        required=True,
        help_text='Initial size of the training set'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters of the Active learning</h2>'),
                Field('query_strategy'),
                Field('ratio_test'),
                Field('size_seed')
            ),
            Accordion(
                AccordionGroup(
                    'Number of labels added'
                ),
                AccordionGroup(
                    'Accuracy to reach'
                )
            )

        )


### ANNOTATION
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
                css_class='col-md-10 d-flex justify-content-center'
            )
        )
