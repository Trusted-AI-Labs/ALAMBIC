import numpy as np


def random_sampling(model, unlabelled_data):
    return np.random.choice(unlabelled_data, 1)
