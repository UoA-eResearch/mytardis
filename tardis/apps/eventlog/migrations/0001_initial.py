# Generated by Django 2.2.14 on 2020-07-18 06:27

import django.utils.timezone
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import migrations, models

# pylint: disable=C0412
if "sqlite" in settings.DATABASES["default"]["ENGINE"]:
    from ..fields import JSONField
elif "mysql" in settings.DATABASES["default"]["ENGINE"]:
    # pylint: disable=E0401
    from django_mysql.models import JSONField
else:
    from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eventlog.Action')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType')),
                ('object_id', models.PositiveIntegerField(null=True)),
                ('extra', JSONField(verbose_name=DjangoJSONEncoder)),
            ],
        ),
    ]
