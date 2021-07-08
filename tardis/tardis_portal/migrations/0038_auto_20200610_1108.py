# Generated by Django 2.2.10 on 2020-06-09 23:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tardis_portal', '0037_auto_20200514_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project',
            name='lead_researcher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lead_researcher', to=settings.AUTH_USER_MODEL),
        ),
    ]