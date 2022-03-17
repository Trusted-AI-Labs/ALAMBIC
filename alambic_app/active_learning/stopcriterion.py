import logging

from alambic_app.models.results import Result

from django.core.cache import cache

logger = logging.getLogger(__name__)


def budget_reached(budget, learner):
    return ((budget - learner.step) <= 0) and (learner.step - Result.objects.latest('step').step) <= 0


def accuracy_reached(accuracy, learner):
    return (accuracy - learner.accuracy) <= 0


def final_reached(param, learner):
    return len(learner.unlabelled_indices) == 0
