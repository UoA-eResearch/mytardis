# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-08-02 01:03
from __future__ import unicode_literals

from django.db import migrations, models
import tardis.tardis_portal.models.experiment

class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0016_add_timestamps'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='internal_id',
            field=models.CharField(default=tardis.tardis_portal.models.experiment.experiment_internal_id_default, max_length=400, unique=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='project_id',
            field=models.CharField(default=b'No Project ID', max_length=400),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='institution_name',
            field=models.CharField(default=b'University of Auckland', max_length=400),
        ),
        migrations.AlterField(
            model_name='storagebox',
            name='django_storage_class',
            field=models.TextField(default=b'storages.backends.s3boto3.S3Boto3Storage'),
        ),
    ]
