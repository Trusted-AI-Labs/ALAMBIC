from crispy_forms.bootstrap import InlineCheckboxes, Accordion, AccordionGroup
from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.constantes import FEATURES_TEXT_CHOICES, PREPROCESSING_TEXT_CHOICES
from alambic_app.forms.forms import CrispyWizardStep


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

    tokenizer = forms.BooleanField(
        help_text="Settings for using a tokenizer in case of deep learning",
        widget = forms.CheckboxInput,
        required = False
    )

    max_length = forms.IntegerField(
        label='Maximum length',
        help_text="Maximum number of tokens for input",
        initial= 512
    )

    # annotators = forms.ChoiceField(
    #    widget=forms.RadioSelect,
    #    choices=ANNOTATORS_CHOICES,
    #    required=False
    # )

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
                    InlineCheckboxes('vectorizer'),
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
                    'Tokenizer for Deep Learning',
                    Field('tokenizer'),
                    Div('max_length')
                )
                # AccordionGroup(
                #    'Convert in a tree',
                #    InlineCheckboxes('annotators'),
                # )
            ),
        )

    def clean(self):
        cleaned_data = super().clean()
        operations = dict()
        # tree = cleaned_data.get('annotators')
        vector = cleaned_data.get('vectorizer')
        preprocess = cleaned_data.get('preprocessing_steps')
        tokenizer = cleaned_data.get('tokenizer')
        

        if 'lemma' in preprocess:
            operations['lemma'] = {'stop': 'stop_words' in preprocess}

        if vector == '' and tokenizer == '':
            # self.add_error('annotators', 'Only one type of features can be selected')
            self.add_error('vectorizer', 'You have to select a feature')
        
        if vector:
            operations[vector] = {'ngram_range': (cleaned_data['ngram_min'], cleaned_data['ngram_max'])}
            if 'stop_words' in preprocess:
                operations[vector]['stop_words'] = 'english'
            if cleaned_data.get('max_features') is not None:
                operations[vector]['max_features'] = cleaned_data.get('max_features')
        
        if tokenizer:
            operations['tokenizer'] = {'max_seq_length': cleaned_data.get('max_length')}

        # if tree:
        #    operations['client'] = f'tokenize,mwt,pos,lemma,{tree}'

        return operations
