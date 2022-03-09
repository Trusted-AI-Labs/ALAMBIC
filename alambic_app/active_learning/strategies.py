import numpy as np


def random_sampling(model, unlabelled_data, n_instances):
    return np.random.choice(unlabelled_data, n_instances)
