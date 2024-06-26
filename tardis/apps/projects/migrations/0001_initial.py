# Generated by Django 3.2.4 on 2022-01-07 01:57

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import tardis.tardis_portal.models.parameters


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("tardis_portal", "0022_publicaccess_dataset_datafile"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Institution",
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
                    "name",
                    models.CharField(default="University of Auckland", max_length=255),
                ),
                ("url", models.URLField(blank=True, null=True)),
                (
                    "institution_type",
                    models.CharField(max_length=100, blank=True, null=True),
                ),
                ("date_established", models.DateTimeField(blank=True, null=True)),
                ("address", models.TextField(blank=True, null=True)),
                ("aliases", models.CharField(max_length=255, blank=True, null=True)),
                ("status", models.CharField(max_length=255, blank=True, null=True)),
                ("country", models.CharField(max_length=255, blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Project",
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
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField()),
                ("locked", models.BooleanField(default=False)),
                (
                    "public_access",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "No public access (hidden)"),
                            (25, "Ready to be released pending embargo expiry"),
                            (50, "Public Metadata only (no data file access)"),
                            (100, "Public"),
                        ],
                        default=1,
                    ),
                ),
                ("embargo_until", models.DateTimeField(blank=True, null=True)),
                ("start_time", models.DateTimeField(default=django.utils.timezone.now)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("url", models.URLField(blank=True, max_length=255, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "experiments",
                    models.ManyToManyField(
                        blank=True,
                        related_name="projects",
                        to="tardis_portal.Experiment",
                    ),
                ),
                (
                    "institution",
                    models.ManyToManyField(
                        related_name="projects",
                        to="projects.Institution",
                    ),
                ),
                (
                    "principal_investigator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="principal_investigator",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProjectParameterSet",
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
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                    ),
                ),
                (
                    "schema",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tardis_portal.schema",
                    ),
                ),
                (
                    "storage_box",
                    models.ManyToManyField(
                        related_name="projectparametersets",
                        to="tardis_portal.StorageBox",
                    ),
                ),
            ],
            bases=(
                models.Model,
                tardis.tardis_portal.models.parameters.ParameterSetManagerMixin,
            ),
        ),
        migrations.CreateModel(
            name="ProjectParameter",
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
                ("string_value", models.TextField(blank=True, null=True)),
                (
                    "numerical_value",
                    models.FloatField(blank=True, db_index=True, null=True),
                ),
                (
                    "datetime_value",
                    models.DateTimeField(blank=True, db_index=True, null=True),
                ),
                ("link_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "link_ct",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tardis_portal.parametername",
                    ),
                ),
                (
                    "parameterset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.projectparameterset",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProjectACL",
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
                ("canRead", models.BooleanField(default=False)),
                ("canDownload", models.BooleanField(default=False)),
                ("canWrite", models.BooleanField(default=False)),
                ("canDelete", models.BooleanField(default=False)),
                ("canSensitive", models.BooleanField(default=False)),
                ("isOwner", models.BooleanField(default=False)),
                ("effectiveDate", models.DateField(blank=True, null=True)),
                ("expiryDate", models.DateField(blank=True, null=True)),
                (
                    "aclOwnershipType",
                    models.IntegerField(
                        choices=[(1, "Owner-owned"), (2, "System-owned")], default=1
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projectacls",
                        to="auth.group",
                    ),
                ),
                (
                    "project",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="projects.project",
                    ),
                ),
                (
                    "token",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projectacls",
                        to="tardis_portal.token",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="projectacls",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
