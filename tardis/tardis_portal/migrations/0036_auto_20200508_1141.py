# Generated by Django 2.2.10 on 2020-05-07 23:41

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0035_merge_20200507_1612'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='public_access',
            field=models.PositiveSmallIntegerField(choices=[(1, 'No public access (hidden)'), (25, 'Ready to be released pending embargo expiry'), (50, 'Public Metadata only (no data file access)'), (100, 'Public')], default=1),
        ),
        migrations.AlterField(
            model_name='facility',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tardis_portal.Institution'),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]