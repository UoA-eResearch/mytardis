# Generated by Django 4.2.7 on 2024-02-22 22:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tardis_portal", "0026_alter_experiment_institution_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("identifiers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserPID",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identifier",
                    models.CharField(
                        blank=True, max_length=400, null=True, unique=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="identifiers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DatafileID",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "identifier",
                    models.CharField(
                        blank=True, max_length=400, null=True, unique=True
                    ),
                ),
                (
                    "datafile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="identifiers",
                        to="tardis_portal.datafile",
                    ),
                ),
            ],
        ),
    ]
