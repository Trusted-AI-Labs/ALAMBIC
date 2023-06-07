# to add strategies to ALiPy if needed
import numpy as np
from sklearn.metrics import pairwise_distances
from alipy.query_strategy.query_labels import BaseIndexQuery, randperm


class QueryInstanceRandom(BaseIndexQuery):
    """Randomly sample a batch of indexes from the unlabel indexes.
    Correction by C. Nachtegael
    """

    def select(self, label_index, unlabel_index, batch_size=1, **kwargs):
        """Select indexes randomly.

        Parameters
        ----------
        label_index: object
            Add this parameter to ensure the consistency of api of strategies.
            Please ignore it.

        unlabel_index: list
            The indexes of unlabeled set.

        batch_size: int, optional (default=1)
            Selection batch size.

        Returns
        -------
        selected_idx: list
            The selected indexes which is a subset of unlabel_index.
        """
        if len(unlabel_index) <= batch_size:
            return np.array([i for i in unlabel_index])
        perm = randperm(len(unlabel_index) - 1, batch_size)
        tpl = unlabel_index.copy()
        return [tpl[i] for i in perm]


class QueryInstanceCoresetGreedy(BaseIndexQuery):
    """ICLR 2018 Paper: Active Learning for Convolutional Neural Networks: A Core-Set Approach.
    The implementation is referred to
    https://github.com/google/active-learning/blob/master/sampling_methods/kcenter_greedy.py

    Parameters
    ----------
    X: 2D array
        Feature matrix of the whole dataset. It is a reference which will not use additional memory.

    y: array-like
        Label matrix of the whole dataset. It is a reference which will not use additional memory.

    train_idx: array-like
        the index of training data.

    distance: str, optional (default='euclidean')
        Distance metric. Should be one of ['cityblock', 'cosine', 'euclidean', 'l1', 'l2', 'manhattan'].
    """

    def __init__(self, X, y, train_idx, distance='euclidean'):
        self.X = X[train_idx,:]
        self.y = y[train_idx]
        self.name = 'kcenter'
        self.features = self.X
        self.metric = distance
        self.min_distances = None
        self.n_obs = self.X.shape[0]
        self.already_selected = []
        self.train_idx = train_idx
    
    def set_features(self, embeddings):
        self.X = embeddings[:,0]

    def update_distances(self, cluster_centers, only_new=True, reset_dist=False):
        """Update min distances given cluster centers.

        Args:
          cluster_centers: indices of cluster centers
          only_new: only calculate distance for newly selected points and update
            min_distances.
          rest_dist: whether to reset min_distances.
        """
        if reset_dist:
            self.min_distances = None
        if only_new:
            cluster_centers = [d for d in cluster_centers
                               if d not in self.already_selected]
        if cluster_centers:
            # Update min_distances for all examples given new cluster center.
            x = self.features[cluster_centers,:]
            dist = pairwise_distances(self.features, x, metric=self.metric)

            if self.min_distances is None:
                self.min_distances = np.min(dist, axis=1).reshape(-1, 1)
            else:
                if dist.shape[1] != 1:
                    dist = np.min(dist, axis=1).reshape(-1, 1)
                self.min_distances = np.minimum(self.min_distances, dist)

    def select(self, label_index, unlabel_index, batch_size=1, **kwargs):
        """
        Diversity promoting active learning method that greedily forms a batch
        to minimize the maximum distance to a cluster center among all unlabeled
        datapoints.

        Parameters
        ----------
        label_index: {list, np.ndarray, IndexCollection}
            The indexes of labeled samples.

        unlabel_index: {list, np.ndarray, IndexCollection}
            The indexes of unlabeled samples.

        model: object, optional (default=None)
            Current classification model, should have the 'predict_proba' method for probabilistic output.
            If not provided, LogisticRegression with default parameters implemented by sklearn will be used.

        batch_size: int, optional (default=1)
            Selection batch size.

        Returns
        -------
          indices of points selected to minimize distance to cluster centers
        """
        already_selected = [np.where(self.train_idx == id)[0].item() for id in label_index]
        self.update_distances(already_selected, only_new=True, reset_dist=False)

        new_batch = []
        self.min_distances[already_selected] = -100.0
        self.already_selected = already_selected

        for _ in range(batch_size):
            ind = np.argmax(self.min_distances)
            # New examples should not be in already selected since those points
            # should have min_distance of zero to a cluster center.
            assert ind not in self.already_selected
            assert self.train_idx[ind] in unlabel_index

            self.update_distances([ind], only_new=True, reset_dist=False)
            self.min_distances[ind] = -100.0
            new_batch.append(self.train_idx[ind])
        return new_batch