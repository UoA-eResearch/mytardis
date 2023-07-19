# Generated by Mike Laverick on 2021-10-29 13:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tardis_portal', '0020_delete_old_acls'),
    ]

    operations = [


        migrations.AlterField(
            model_name='groupadmin',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),

        migrations.AddField(
            model_name='groupadmin',
            name='admin_group',
            field=models.ForeignKey(related_name='admin_group', blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auth.Group'),
        ),

        migrations.RenameField(
            model_name='groupadmin',
            old_name='user',
            new_name='admin_user',
        ),

    ]
