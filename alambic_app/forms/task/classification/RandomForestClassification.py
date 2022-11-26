from crispy_forms.layout import Layout, Div, HTML, Field
from django import forms

from alambic_app.forms.forms import CrispyWizardStep


class RFClassification(CrispyWizardStep):

    number_trees = forms.IntegerField(
        max_value=100,
        min_value=1,
        required=True
    )

    max_depth = forms.IntegerField(
        max_value=100,
        min_value=1,
        required=False
    ),

    criterion = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=[
            ('gini', 'Gini impurity'),
            ('log_loss', 'Log loss Shannon information gain'),
            ('entropy', 'Entropy Shannon information gain')
        ],
        required=True,
        initial='gini'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout = Layout(
            Div(
                HTML('<h2>Parameters for the Random Forest Classification</h2>'),
                HTML('Check the full documentation <a href="https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html?highlight=random#sklearn.ensemble.RandomForestClassifier">here</a>'),
                Field('number_trees'),
                Field('max_depth'),
                Field('criterion')
            )
        )
    
    def clean(self):
        clean_data = super().clean()
        clean_data['n_estimators'] = clean_data.pop('number_trees')  # to be able to use predict_proba in the query strategies
        return clean_data