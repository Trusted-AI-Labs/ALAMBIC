import logging

from django.core.cache import cache

from alambic_app.models.input_models import Data

logger = logging.getLogger(__name__)


def get_table_data(data):
    res = []
    if data == 'all':
        if not cache.get('all_data'):
            qs = Data.objects.all()
            i = 1
            for obj in qs.iterator():
                print(i)
                res.append(obj.data)
                i += 1
            cache.set('all_data', res)
        else:
            res = cache.get('all_data')

    return res
