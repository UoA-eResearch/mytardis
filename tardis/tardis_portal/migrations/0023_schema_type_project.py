# Generated by Django 3.2.4 on 2022-01-07 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tardis_portal", "0022_publicaccess_dataset_datafile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="schema",
            name="type",
            field=models.IntegerField(
                choices=[
                    (1, "Experiment schema"),
                    (2, "Dataset schema"),
                    (3, "Datafile schema"),
                    (4, "None"),
                    (5, "Instrument schema"),
                    (6, "Project schema"),
                ],
                default=1,
            ),
        ),
    ]