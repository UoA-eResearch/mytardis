# Generated by Django 2.2.10 on 2020-03-17 22:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tardis_portal', '0021_auto_20200317_1525'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project',
            old_name='project_description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='project_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='project',
            old_name='project_id',
            new_name='raid',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='handle',
        ),
        migrations.AddField(
            model_name='instrument',
            name='description',
            field=models.TextField(blank=True, default='No description'),
        ),
        migrations.AddField(
            model_name='project',
            name='contact',
            field=models.ManyToManyField(blank=True, null=True, related_name='contacts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='member',
            field=models.ManyToManyField(blank=True, null=True, related_name='members', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='owner',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
