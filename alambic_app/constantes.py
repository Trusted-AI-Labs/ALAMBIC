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

DATA_PATH = "/app/data_alambic"

ENDPOINT_CORENLP = "http://corenlp:9000"
