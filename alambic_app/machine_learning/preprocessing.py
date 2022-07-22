from scipy.sparse import vstack
import scipy.sparse.csr

import sklearn.feature_extraction.text
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer

from alambic_app.models.input_models import *

# Custom functions
from alambic_app.features.images import *
from alambic_app.features.text_mining import *

OPERATIONS_MATCH = {
    # global
    ## scaler
    'standard': StandardScaler,
    'minmax': MinMaxScaler,
    'normalize': Normalizer,
    ## imputation,
    'simple_imp': SimpleImputer,
    'knn_imp': KNNImputer,
    # text
    'tfidf': TfidfVectorizer,
    'bow': CountVectorizer,
    'hashing': HashingVectorizer,
    'lemma': tokenizer_lemmatizer,
    'tree': dependency_tree
    # image
}

CUSTOM_FUNCTIONS = {
    'lemma',
    'tree'
}


class PreprocessingHandler:
    """
    Class to do the processing and store them
    """

    def __init__(self, operations):
        self.pipeline = self.get_pipeline(operations)
        self.features = dict()

    def get_pipeline(self, operations):
        lst = []
        for op, params in operations.items():
            if op in CUSTOM_FUNCTIONS:
                lst.append(
                    (op, pipelinize(OPERATIONS_MATCH[op], kwargs=params))
                )
            else:
                lst.append(
                    (op, OPERATIONS_MATCH[op](**params))
                )
        return lst

    def create_features(self):
        data = Data.objects.all()
        data_ids = [item.id for item in data]
        data = [item.content for item in data]
        if isinstance(self.pipeline, list):
            pipeline = Pipeline(self.pipeline)
            features = pipeline.fit_transform(data)
        self.features = {k: v for k, v in zip(data_ids, features)}

    def __getitem__(self, id):
        return self.features[id]

    def __str__(self):
        return f"Handler of Data with {len(self.features)} data points"

    def __repr__(self):
        return str(self)

    def get_x(self, lst):
        x = []
        for data_id in lst:
            x.append(self.features[data_id])
        if isinstance(x[0], scipy.sparse.csr.csr_matrix):
            x = vstack(x)
        else:
            x = np.concatenate(x)
        return x
