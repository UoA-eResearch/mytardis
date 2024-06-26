# Generated by Django 3.2.4 on 2021-10-29 03:38

from django.db import migrations, models


def create_public_user(apps, schema_editor):

    EXPERIMENTACL = apps.get_model("tardis_portal", "ExperimentACL")
    USER = apps.get_model("auth", "User")
    EXPERIMENT = apps.get_model("tardis_portal", "Experiment")

    # Create PUBLIC_USER
    PUBLIC_USER = USER.objects.create(username="PUBLIC_USER")
    print(
        "PUBLIC USER ID is "
        + str(PUBLIC_USER.id)
        + ", please update the settings.py PUBLIC_USER_ID variable accordingly"
    )

    # Iterate over all public (+metadata public) Experiments and create ACL for
    # PUBLIC_USER
    for exp in EXPERIMENT.objects.filter(public_access__gt=25).iterator():
        EXPERIMENTACL.objects.create(
            canRead=True,
            aclOwnershipType=2,  # = .SYSTEM_OWNED,
            experiment=exp,
            user=PUBLIC_USER,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tardis_portal", "0021_groupadmin_changes"),
    ]

    operations = [
        migrations.AddField(
            model_name="datafile",
            name="public_access",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "No public access (hidden)"),
                    (25, "Ready to be released pending embargo expiry"),
                    (50, "Public Metadata only (no data file access)"),
                    (100, "Public"),
                ],
                default=1,
            ),
        ),
        migrations.AddField(
            model_name="dataset",
            name="public_access",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "No public access (hidden)"),
                    (25, "Ready to be released pending embargo expiry"),
                    (50, "Public Metadata only (no data file access)"),
                    (100, "Public"),
                ],
                default=1,
            ),
        ),
        migrations.RunPython(create_public_user),
    ]
