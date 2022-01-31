import sklearn.feature_extraction.text
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer

from alambic_app.models.input_models import *
from alambic_app.feature_extraction.text_mining import initialize_client

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
    'client': initialize_client,
    # image
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
        if "client" in operations:
            lst = initialize_client(operations['client'])
        else:
            for op, params in operations.items():
                lst.append(
                    (op, OPERATIONS_MATCH[op](**params))
                )
        return lst

    def create_features(self):
        data = Data.objects.all()
        data_ids = [item.id for item in data]
        data = [item.content for item in data]
        if isinstance(self.pipeline, list):
            pipeline = sklearn.pipeline.Pipeline(self.pipeline)
            features = pipeline.fit_transform(data)
        else:
            features = [self.pipeline.annotate(text) for text in data]
        self.features = {k: v for k, v in zip(data_ids, features)}

    def __getitem__(self, id):
        return self.features[id]

    def __str__(self):
        return f"Handler of Data with {len(self.features)} data points"
