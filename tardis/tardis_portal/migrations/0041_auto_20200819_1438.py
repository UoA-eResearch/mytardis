# Generated by Django 2.2.10 on 2020-08-19 02:38

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0040_auto_20200805_1108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupadmin',
            name='admin_groups',
            field=models.ManyToManyField(blank=True, related_name='admin_groups', to='auth.Group'),
        ),
        migrations.AlterField(
            model_name='groupadmin',
            name='admin_users',
            field=models.ManyToManyField(blank=True, related_name='admin_users', to=settings.AUTH_USER_MODEL),
        ),
    ]
