from alambic_app.models.input_models import Data


def get_table_data(data):
    res = None
    if data == 'all':
        qs = Data.objects.all()
        res = [obj.data
               for obj in qs]
        print(res)

    return res
