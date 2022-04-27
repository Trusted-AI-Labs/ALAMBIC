from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms
from django.core.cache import cache
from django_select2.forms import Select2Widget

from alambic_app.constantes import AL_ALGORITHMS_CHOICES
from alambic_app.forms.forms import CrispyWizardStep


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
        help_text='Percentage of the dataset for the test set',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 0.01
            }
        )
    )

    size_seed = forms.IntegerField(
        min_value=1,
        required=True,
        help_text='Initial size of the training set'
    )

    budget = forms.IntegerField(
        min_value=1,
        required=False,
        help_text='Number of annotations the oracle will do'
    )

    accuracy_goal = forms.FloatField(
        min_value=0.5,
        max_value=1,
        required=False,
        help_text='Minimum accuracy to reach',
        widget=forms.NumberInput(
            attrs={
                'theme': 'material',
                'data-minimum-input-length': 0,
                'step': 0.01
            }
        )
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
            Div(
                HTML('<h3>Stop Criterion</h3>')
            ),
            Accordion(
                AccordionGroup(
                    'Maximum number of labels added',
                    Field('budget')
                ),
                AccordionGroup(
                    'Accuracy to reach',
                    Field('accuracy_goal')
                )
            )

        )

    def clean(self):
        cleaned_data = super().clean()
        size_seed = cleaned_data['size_seed']

        if size_seed > cache.get('data'):
            self.add_error('size_seed', 'You are exceeding the size of the dataset')

        data = {
            'ratio_test': cleaned_data['ratio_test'],
            'query_strategy': cleaned_data['query_strategy'],
            'size_seed': size_seed
        }

        if cleaned_data['accuracy_goal'] is not None and cleaned_data['budget'] is not None:
            self.add_error('accuracy_goal', 'You have to choose only one stop criterion')
            self.add_error('budget', 'You have to choose only one stop criterion')

        else:
            if cleaned_data['accuracy_goal'] is not None:
                data['stop_criterion'] = {'algorithm': 'accuracy', 'param': cleaned_data.get('accuracy_goal')}
            elif cleaned_data['budget'] is not None:
                data['stop_criterion'] = {'algorithm': 'budget', 'param': cleaned_data.get('budget')}
            else:
                self.add_error('accuracy_goal', 'You have to choose one stop criterion')
                self.add_error('budget', 'You have to choose one stop criterion')

        return data
