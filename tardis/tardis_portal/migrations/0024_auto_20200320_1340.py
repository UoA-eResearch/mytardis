# Generated by Django 2.2.10 on 2020-03-20 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0023_objectacl_candownload'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='embargo_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='experiment',
            name='embargo_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='embargo_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
