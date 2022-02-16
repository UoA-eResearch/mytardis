# Generated by Django 2.2.10 on 2021-02-15 01:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0045_auto_20210128_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='experiment',
        ),
        migrations.AddField(
            model_name='datafileacl',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datafileacls', to='tardis_portal.Token'),
        ),
        migrations.AddField(
            model_name='datasetacl',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasetacls', to='tardis_portal.Token'),
        ),
        migrations.AddField(
            model_name='experimentacl',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='experimentacls', to='tardis_portal.Token'),
        ),
        migrations.AddField(
            model_name='projectacl',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projectacls', to='tardis_portal.Token'),
        ),
    ]