import os.path

import torch

from django.conf import settings
from transformers import AutoModelForSequenceClassification

from alambic_app.models.labels import ClassificationLabel

class ModelFactory:

    def __init__(self, origin):
        self.origin = origin
        self.save_dir = f'{settings.MEDIA_ROOT}'
        self.embed_dim = 0
        self.get_labels_config()

    def get_labels_config(self):
        labels = list(ClassificationLabel.objects.all().values('value'))

        if len(labels) == 0:
            labels = ['0','1']

        self.label2id = {v: i for i, v in enumerate(labels)}
        self.id2label = {id: label for label, id in self.label2id.items()}

    def get_num_classes(self):
        return len(self.label2id)

    def get_embed_dim(self):
        return self.embed_dim

    def produce(self, model=None, cv = None):
        self.get_labels_config()

        if model is None:
            model = AutoModelForSequenceClassification.from_pretrained(
                self.origin,
                num_labels=self.get_num_classes(),
                output_hidden_states = True
            )
            self.embed_dim = model.config.hidden_size
            model.gradient_checkpointing_enable()
        else:
            model = model.module

        if not os.path.exists(f"{self.save_dir}/pytorch_model.bin"):
            torch.save(model.state_dict(), f"{self.save_dir}/pytorch_model.bin")

            return model

        if cv is None:
            model.load_state_dict(torch.load(f"{self.save_dir}/pytorch_model.bin", map_location="cpu"))
        else :
            model.load_state_dict(torch.load(f"{self.save_dir}/pytorch_model_{cv}.bin", map_location="cpu"))
        return model

    def save_model(self, model):
        distributed = getattr(model, 'module', None)
        model_to_save = model
        if distributed:
            model_to_save = model.module
        torch.save(model_to_save.state_dict(),f"{self.save_dir}/pytorch_model.bin")