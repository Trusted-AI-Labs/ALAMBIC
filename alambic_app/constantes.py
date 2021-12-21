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
    ('SVM', 'SVM'),
    ('RF', 'Random Forest'),
]

REGRESSION_MODELS_CHOICES = [

]

NER_MODELS_CHOICES = [

]

RE_MODELS_CHOICES = [

]

AL_ALGORITHMS_CHOICES = [
    ('RS', 'Random Sampling'),
    ('UC', 'Uncertainty measure'),
]

DATA_PATH = "/app/data_alambic"

ENDPOINT_CORENLP = "http://corenlp:9000"
