# Generated by Django 4.0 on 2022-02-02 13:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('alambic_app', '0003_alter_result_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='cross_val',
            field=models.BooleanField(default=False),
        ),
    ]
