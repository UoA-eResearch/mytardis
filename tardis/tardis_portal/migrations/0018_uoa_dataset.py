# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-06 00:15
from __future__ import unicode_literals

from django.db import migrations, models
import tardis.tardis_portal.models.dataset
#import tardis.tardis_portal.models.experiment


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0017_uoa_experiment'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='dataset_id',
            field=models.CharField(default=tardis.tardis_portal.models.dataset.dataset_id_default, max_length=400, unique=True),
        ),
 #       migrations.AlterField(
 #           model_name='experiment',
 #           name='internal_id',
 #           field=models.CharField(default=tardis.tardis_portal.models.experiment.experiment_internal_id_default, max_length=400, unique=True),
 #       ),
    ]
