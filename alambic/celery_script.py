import os
import torch

from celery import Celery
from accelerate import Accelerator

class OneAccelerator(Accelerator):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(OneAccelerator, cls).__new__(cls)
        return cls.instance

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alambic.settings')

app = Celery('alambic')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

if __name__ == "__main__":
    accelerator = OneAccelerator()
    #CUDA_VISIBLE_DEVICES = int(os.environ["LOCAL_RANK"])
    accelerator.print(accelerator.device, accelerator.num_processes)
    if accelerator.is_main_process:
        worker = app.Worker(pool = "solo", loglevel = "INFO")
        worker.start()
