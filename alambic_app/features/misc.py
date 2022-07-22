# Adapted from https://ryan-cranfill.github.io/sentiment-pipeline-sklearn-3/
# Found on https://towardsdatascience.com/setting-up-text-preprocessing-pipeline-using-scikit-learn-and-spacy-e09b9b76758f

from sklearn.preprocessing import FunctionTransformer


def pipelinize(function, kwargs):
    return FunctionTransformer(function, validate=False, kw_args=kwargs)
