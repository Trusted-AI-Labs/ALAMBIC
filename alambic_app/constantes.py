DATA_CHOICES = [
    ('Text', 'Text'),
    ('Image', 'Image')
]
TASK_CHOICES = [
    ('C', 'Classification'),
    ('R', 'Regression')
]

LABEL_MATCH = {
    'C': 'ClassificationLabel',
    'R': 'RegressionLabel'
}

CLASSIFICATION_MODELS_CHOICES = [
    ('SVC', 'SVM'),
    ('RF', 'Random Forest'),
]

REGRESSION_MODELS_CHOICES = [

]

NER_MODELS_CHOICES = [

]

RE_MODELS_CHOICES = [

]

ANNOTATORS_CHOICES = [
    ('ddparse', 'Dependency Parse Tree'),
    ('parse', 'Constituency and Dependency Parse Tree'),
]

PREPROCESSING_TEXT_CHOICES = [
    # ('lemma', 'Lemma'),
    ('stop_word', 'Ignore stop words'),
]

FEATURES_TEXT_CHOICES = [
    ('tfidf', 'TF-IDF'),
    ('bow', 'Bag Of Words'),
    ('hashing', 'Token occurrences with hashing'),
]

AL_ALGORITHMS_CHOICES = [
    ('RS', 'Random Sampling'),
    ('US', 'Uncertainty Sampling'),
    ('MS', 'Margin Sampling'),
    ('ES', 'Entropy Sampling')
]

DATA_PATH = "/app/data_alambic"
