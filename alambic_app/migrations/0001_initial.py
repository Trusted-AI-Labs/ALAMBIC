# Generated by Django 4.0 on 2021-12-13 14:36

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.TextField()),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                   to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('C', 'Classification'), ('R', 'Regression')], max_length=3)),
                ('polymorphic_ctype',
                 models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                   related_name='polymorphic_%(app_label)s.%(class)s_set+',
                                   to='contenttypes.contenttype')),
            ],
        ),
        migrations.CreateModel(
            name='ClassificationLabel',
            fields=[
                ('label_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='alambic_app.label')),
                ('class_id', models.IntegerField(unique=True)),
                ('value', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('alambic_app.label',),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('data_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='alambic_app.data')),
                ('content', django.contrib.postgres.fields.ArrayField(
                    base_field=django.contrib.postgres.fields.ArrayField(
                        base_field=django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(), size=None),
                        size=None), size=None)),
            ],
            options={
                'db_table': 'image_data',
            },
            bases=('alambic_app.data',),
        ),
        migrations.CreateModel(
            name='RegressionLabel',
            fields=[
                ('label_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='alambic_app.label')),
                ('value', models.FloatField(unique=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('alambic_app.label',),
        ),
        migrations.CreateModel(
            name='Text',
            fields=[
                ('data_ptr',
                 models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True,
                                      primary_key=True, serialize=False, to='alambic_app.data')),
                ('content', models.TextField()),
            ],
            options={
                'db_table': 'text_data',
            },
            bases=('alambic_app.data',),
        ),
        migrations.CreateModel(
            name='Output',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('annotated_by_human', models.BooleanField(default=False)),
                ('predicted', models.BooleanField(default=False)),
                ('data', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='alambic_app.data')),
                ('label',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='alambic_app.label')),
            ],
            options={
                'db_table': 'output',
                'unique_together': {('data', 'label', 'annotated_by_human', 'predicted')},
            },
        ),
    ]