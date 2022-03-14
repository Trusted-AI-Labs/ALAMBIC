# to add strategies to ALiPy if needed
import numpy as np
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
