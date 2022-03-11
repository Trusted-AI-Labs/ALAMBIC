import numpy as np


def random_sampling(model, unlabelled_data, n_instances):
    random_idx = np.random.choice(unlabelled_data.shape[0], size=n_instances, replace=False)
    return random_idx
