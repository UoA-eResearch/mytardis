# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-10-01 03:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tardis_portal", "0017_add_cc_licenses"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storagebox",
            name="status",
            field=models.CharField(default="online", max_length=100),
        ),
    ]
