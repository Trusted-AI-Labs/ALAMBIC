from scipy.sparse import vstack
import scipy.sparse.csr

import sklearn.feature_extraction.text
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, MinMaxScaler, Normalizer
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, HashingVectorizer

# DL
from transformers import AutoTokenizer, DefaultDataCollator
from datasets import Dataset
from torch.utils.data import DataLoader

from alambic_app.models.input_models import *

# Custom functions
from alambic_app.features import *

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
    'tree': dependency_tree,
    'masking': masking
    # image
}

CUSTOM_FUNCTIONS = {
    'lemma',
    'tree',
    'masking'
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
    

class DeepLearningTextHandler(PreprocessingHandler):
    def __init__(self, origin, max_seq_length):
        self.tokenizer = self.get_tokenizer(origin)
        self.max_seq_length = max_seq_length
        self.features = self.import_data()

    def create_features(self):
        self.features = self.features.map(
            self.process_data,
            batched=True,
            remove_columns=['sentence']
        )


    def get_x(self, indices = None):
        if indices is None:
            return self.data.set_format('torch')
        return self.data.filter(lambda x : x['id'] in indices).sort('id').remove_columns('id').set_format('torch')

    def get_dataloader(self, data, labels, batch_size, shuffle=False):
        #collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        if labels is not None:
            data = data.add_column(name = 'label', column=labels)
        collator = DefaultDataCollator()
        return DataLoader(
            data,
            batch_size = batch_size,
            shuffle = shuffle,
            collate_fn=collator,
            pin_memory=True
        )

    def get_tokenizer(self, origin):
        return AutoTokenizer.from_pretrained(origin)


    def process_data(self, example):
        # we have to do it padding full here and not dynamic because the predict function in
        # strategy does not do the collate_fn
        tokenized = self.tokenizer(
            example["sentence"],
            truncation = True,
            max_length = self.max_seq_length,
            padding="max_length"
        )
        return tokenized

    @staticmethod
    def import_data():
        data = Data.objects.all()
        data_ids = [item.id for item in data]
        data = [item.content for item in data]

        data = Dataset.from_dict({
            "sentence" : data,
            'id' : data_ids
        })

        return data