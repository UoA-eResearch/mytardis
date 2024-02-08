# Generated by Mike Laverick on 2021-05-21 17:00

from django.db import migrations

# =========#
# WARNING #
# =========#

# This migration will delete your old ACLs, which is irreversible.
# Only perform this migration once you are sure your MyTardis deployment has
# Successfully moved over to the new ACLs without any errors.


class Migration(migrations.Migration):

    dependencies = [
        ("tardis_portal", "0019_create_and_populate_new_acls"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ObjectACL",
        ),
    ]
