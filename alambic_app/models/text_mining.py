from django.db import models
from colorfield.fields import ColorField


class Entity(models.Model):
    entity_type = models.ForeignKey('EntityType', null=False, blank=False, on_delete=models.CASCADE)
    start = models.BigIntegerField(null=False, blank=False)
    end = models.BigIntegerField(null=False, blank=False)
    content = models.TextField(null=False, blank=False)

    class Meta:
        app_label = 'alambic_app'
        unique_together = ['start', 'end', 'entity_type', 'content']


class EntityType(models.Model):
    name = models.TextField(null=False, blank=False)
    color = ColorField(default='#FF0000', format='hex')

    class Meta:
        app_label = 'alambic_app'


class EntitytoRelation(models.Model):
    entity = models.ForeignKey('Entity', null=False, blank=False, on_delete=models.CASCADE)
    relation = models.ForeignKey('Relation', null=False, blank=False, on_delete=models.CASCADE)

    class Meta:
        app_label = 'alambic_app'
        unique_together = ['entity', 'relation']


class Relation(models.Model):
    relation_type = models.ForeignKey('RelationType', null=False, blank=False, on_delete=models.CASCADE)
    components = models.ManyToManyField('Entity', through='EntitytoRelation')

    class Meta:
        app_label = 'alambic_app'


class RelationType(models.Model):
    name = models.TextField(null=False, blank=False)
    color = ColorField(default='#FF0000', format='hex')

    class Meta:
        app_label = 'alambic_app'
