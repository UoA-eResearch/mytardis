# Generated by Django 2.2.10 on 2020-03-20 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0024_auto_20200320_1340'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='experiment',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),
    ]
