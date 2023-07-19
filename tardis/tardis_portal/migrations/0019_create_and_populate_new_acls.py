# Generated by Mike Laverick on 2021-05-21 16:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def create_new_acl_objects(apps, schema_editor):

    OBJECTACL = apps.get_model("tardis_portal", "ObjectACL")
    EXPERIMENTACL = apps.get_model("tardis_portal", "ExperimentACL")
    USER = apps.get_model("auth", "User")
    GROUP = apps.get_model("auth", "Group")
    EXPERIMENT = apps.get_model("tardis_portal", "Experiment")

    for acl in OBJECTACL.objects.all().iterator():
        # Check that old ACL belongs to an experiment
        if acl.content_type.model == 'experiment':
            try:
                linked_object = EXPERIMENT.objects.get(pk=acl.object_id)
            except:
                print("ERROR finding experiment for new_ACL copy: old_acl_id="+str(acl.id)+', exp_id='+str(acl.object_id))
        # something went horribly wrong with Generic foreign keys if not an experiment
        else:
            print("bad ACL content type: id="+str(acl.id)+",!"+str(acl.content_type.model)+"!")

        # pull out user corresponding to old ACL, ready for new foreignkey relation
        if acl.pluginId == 'django_user':
            try:
                linked_user = USER.objects.get(pk=acl.entityId)
            except:
                print("ERROR finding user for new_ACL copy: old_acl_id="+str(acl.id)+', userid='+str(acl.entityId))

            EXPERIMENTACL.objects.create(canRead = acl.canRead,
                                         canDownload = acl.canDownload,
                                         canWrite = acl.canWrite,
                                         canDelete = acl.canDelete,
                                         canSensitive = acl.isOwner,
                                         isOwner = acl.isOwner,
                                         effectiveDate = acl.effectiveDate,
                                         expiryDate = acl.expiryDate,
                                         aclOwnershipType = acl.aclOwnershipType,
                                         experiment = linked_object,
                                         user = linked_user)

        # pull out group corresponding to old ACL, ready for new foreignkey relation
        if acl.pluginId == 'django_group':
            try:
                linked_group = GROUP.objects.get(pk=acl.entityId)
            except:
                print("ERROR finding group for new_ACL copy: old_acl_id="+str(acl.id)+', groupid='+str(acl.entityId))

            EXPERIMENTACL.objects.create(canRead = acl.canRead,
                                         canDownload = acl.canDownload,
                                         canWrite = acl.canWrite,
                                         canDelete = acl.canDelete,
                                         canSensitive = acl.isOwner,
                                         isOwner = acl.isOwner,
                                         effectiveDate = acl.effectiveDate,
                                         expiryDate = acl.expiryDate,
                                         aclOwnershipType = acl.aclOwnershipType,
                                         experiment = linked_object,
                                         group = linked_group)

        if acl.pluginId == 'token_group':
            # We do not have enough information to correctly create new ACLs for Tokens using only the old ACL data
            # so we unfortunately need to skip token ACLs!
            print("WARNING  old_acl_id="+str(acl.id)+" belongs to a token, and thus cannot be converted to the new ACL model")
            continue



class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tardis_portal', '0018_make_default_storage_box_status_online'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='token',
            name='experiment',
        ),
        migrations.CreateModel(
            name='ExperimentACL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canRead', models.BooleanField(default=False)),
                ('canDownload', models.BooleanField(default=False)),
                ('canWrite', models.BooleanField(default=False)),
                ('canDelete', models.BooleanField(default=False)),
                ('canSensitive', models.BooleanField(default=False)),
                ('isOwner', models.BooleanField(default=False)),
                ('effectiveDate', models.DateField(blank=True, null=True)),
                ('expiryDate', models.DateField(blank=True, null=True)),
                ('aclOwnershipType', models.IntegerField(choices=[(1, 'Owner-owned'), (2, 'System-owned')], default=1)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tardis_portal.Experiment')),
                ('group', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='experimentacls', to='auth.Group')),
                ('user', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='experimentacls', to=settings.AUTH_USER_MODEL)),
                ('token', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='experimentacls', to='tardis_portal.Token')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DatasetACL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canRead', models.BooleanField(default=False)),
                ('canDownload', models.BooleanField(default=False)),
                ('canWrite', models.BooleanField(default=False)),
                ('canDelete', models.BooleanField(default=False)),
                ('canSensitive', models.BooleanField(default=False)),
                ('isOwner', models.BooleanField(default=False)),
                ('effectiveDate', models.DateField(blank=True, null=True)),
                ('expiryDate', models.DateField(blank=True, null=True)),
                ('aclOwnershipType', models.IntegerField(choices=[(1, 'Owner-owned'), (2, 'System-owned')], default=1)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tardis_portal.Dataset')),
                ('group', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasetacls', to='auth.Group')),
                ('user', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasetacls', to=settings.AUTH_USER_MODEL)),
                ('token', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datasetacls', to='tardis_portal.Token')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DatafileACL',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('canRead', models.BooleanField(default=False)),
                ('canDownload', models.BooleanField(default=False)),
                ('canWrite', models.BooleanField(default=False)),
                ('canDelete', models.BooleanField(default=False)),
                ('canSensitive', models.BooleanField(default=False)),
                ('isOwner', models.BooleanField(default=False)),
                ('effectiveDate', models.DateField(blank=True, null=True)),
                ('expiryDate', models.DateField(blank=True, null=True)),
                ('aclOwnershipType', models.IntegerField(choices=[(1, 'Owner-owned'), (2, 'System-owned')], default=1)),
                ('datafile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tardis_portal.DataFile')),
                ('group', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datafileacls', to='auth.Group')),
                ('user', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datafileacls', to=settings.AUTH_USER_MODEL)),
                ('token', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='datafileacls', to='tardis_portal.Token')),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
        ),

        migrations.AddField(
            model_name='ParameterName',
            name='sensitive',
            field=models.BooleanField(default=False),
        ),

        migrations.RunPython(create_new_acl_objects
        ),
    ]
