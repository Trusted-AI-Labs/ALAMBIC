import sklearn

from alambic_app.models.input_models import *
from alambic_app.feature_extraction import *

OPERATIONS_MATCH = {
    # global
    ## scaler
    'standard': sklearn.preprocessing.StandardScaler,
    'minmax': sklearn.preprocessing.MinMaxScaler,
    'normalize': sklearn.preprocessing.Normalizer,
    ## imputation,
    'simple_imp': sklearn.impute.SimpleImputer,
    'knn_imp': sklearn.impute.KNNImputer,
    'iterative_imp': sklearn.impute.IterativeImputer,
    # text
    'tfidf': sklearn.feature_extraction.text.TfidfTransformer,
    'bow': sklearn.feature_extraction.text.CountVectorizer,
    'hashing': sklearn.feature_extraction.text.HashingVectorizer,
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
        for op, params in operations.items():
            lst.append(
                (op, OPERATIONS_MATCH[op](**params))
            )
        return lst

    def create_features(self):
        data = list(Data.objects.values_list("id", "content"))
        data_ids = [item['id'] for item in data]
        data = [item['content'] for item in data]
        pipeline = sklearn.pipeline.Pipeline(self.pipeline)
        features = pipeline.fit_transform(data)
        self.features = {k: v for k, v in zip(data_ids, features)}

    def __getitem__(self, id):
        return self.features[id]
