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
    ('stop_word', 'Ignore stop words'),
    ('lemma', 'Lemmatize'),
]

FEATURES_TEXT_CHOICES = [
    ('tfidf', 'TF-IDF'),
    ('bow', 'Bag Of Words'),
    ('hashing', 'Token occurrences with hashing'),
]

KERNELS_CHOICES = [
    ('linear','Linear'),
    ('poly','Polynomial'),
    ('rbf', 'Radial Basis Function'),
    ('sigmoid','Sigmoid')
]

AL_ALGORITHMS_CHOICES = [
    ('RS', 'Random Sampling'),
    ('US', 'Uncertainty Sampling'),
    ('MS', 'Margin Sampling'),
    ('ES', 'Entropy Sampling'),
    ('CS', 'Core-set')
]

AL_ALGORITHMS_MATCH = {
    'RS': 'Random Sampling',
    'US': 'Uncertainty Sampling',
    'MS': 'Margin Sampling',
    'ES': 'Entropy Sampling',
    'CS':'Core-set'
}

DATA_PATH = "/app/data_alambic"
