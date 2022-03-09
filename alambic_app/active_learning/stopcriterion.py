import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

def budget_reached(budget, learner):
    return (budget - learner.get_annotated_by_human()) <= 0


def accuracy_reached(accuracy, learner):
    return (accuracy - learner.accuracy) <= 0

def final_reached(param, learner):
    return learner.unlabelled_dataset == 0
