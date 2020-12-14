# Generated by Django 2.2.10 on 2020-08-04 23:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tardis_portal', '0039_groupadmin_admin_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupadmin',
            name='admin_users',
            field=models.ManyToManyField(related_name='admin_users', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='groupadmin',
            name='admin_groups',
            field=models.ManyToManyField(related_name='admin_groups', to='auth.Group'),
        ),
    ]