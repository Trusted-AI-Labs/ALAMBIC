import logging

from time import sleep
from PIL import Image
from numpy import asarray

from django.db.utils import OperationalError

from polymorphic.models import PolymorphicManager

from alambic_app.models.text_mining import Entity, EntityType, Relation, RelationType, EntitytoRelation

logger = logging.getLogger(__name__)


class TextManager(PolymorphicManager):

    def create_instance(self, **kwargs):
        with open(kwargs['filename']) as infile:
            kwargs['content'] = ' '.join(infile.readlines())  # just a big long string

        done = False
        while not done:
            try:
                obj = self.create(**kwargs)
                done = True
            except OperationalError as e:
                logger.info(e)
                logger.info("Sleeping for a bit before trying again")
                sleep(10)
        return obj


class ImageManager(PolymorphicManager):

    def create_instance(self, **kwargs):
        kwargs['content'] = asarray(Image.open(kwargs['filename'])).tolist()  # convert in numpy array

        done = False
        while not done:
            try:
                obj = self.create(**kwargs)
                done = True
            except OperationalError as e:
                logger.info(e)
                logger.info("Sleeping for a bit before trying again")
                sleep(10)
        return obj


### LABELS

class LabelManager(PolymorphicManager):
    model = None

    def find_instance(self, **kwargs):
        return self.filter(**kwargs)

    def create_instance(self, **kwargs):
        instance = self.find_instance(**kwargs)

        if len(instance) > 0:
            return instance[0]
        else:
            done = False
            while not done:
                try:
                    obj = self.create(**kwargs)
                    done = True
                except OperationalError as e:
                    logger.info(e)
                    logger.info("Sleeping for a bit before trying again")
                    sleep(10)
            return obj


class LabelClassificationManager(LabelManager):
    model = 'ClassificationLabel'

    def get_id(self, value):
        """
        :return: The ID that will be assigned to the new class label
        :rtype: int
        """
        instance = self.filter(value=value)
        if len(instance) > 0:
            return instance[0].class_id

        last_id = self.get_queryset().order_by('class_id').last().class_id if len(self.get_queryset()) > 0 else -1
        return last_id + 1

    def create_instance(self, **kwargs):
        kwargs['class_id'] = self.get_id(kwargs['value'])

        return super().create_instance(**kwargs)


class LabelRegressionManager(LabelManager):
    model = 'RegressionLabel'

    def create_instance(self, **kwargs):
        kwargs['value'] = float(kwargs['value'])

        return super().create_instance(**kwargs)


class LabelRelationManager(LabelManager):
    model = 'RelationLabel'

    def create_instance(self, **kwargs):
        json = kwargs.get('data')
        entities = json.get('entities')
        relations = json.get('relations')
        id_entitites = []

        label_relation = self.create()

        for entity in entities:
            entity_type = EntityType.objects.get(name=entity['EntityType'])
            id_entitites.append(Entity.objects.get_or_create(
                entity_type=entity_type,
                start=entity['start_token'],
                end=entity['end_token'],
                content=entity['content']
            )[0])

        for relation in relations:
            relation_type = RelationType.objects.get(name=relation['RelationType'])
            relation_obj = Relation.objects.create(relation_type=relation_type)

            for component in relation:
                EntitytoRelation.objects.create(entity=id_entitites[component], relation=relation_obj)

            relation_obj.save()
            label_relation.relation.add(relation_obj)

        label_relation.save()

        return label_relation
