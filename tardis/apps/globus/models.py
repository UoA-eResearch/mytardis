from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from .apps import GlobusConfig



@python_2_unicode_compatible
class RemoteHost(models.Model):
    """``
    A remote host/VM that contains a Globus endpoint
    """
    name = models.CharField('Name', max_length=50, blank=False, null=False)
    ip_address = models.CharField('IP Address', max_length=50, blank=True)
    endpoint = models.CharField('Globus Endpoint', max_length=50, blank=False, null=False)
    managed = models.BooleanField('Managed', default=True) # managed by MyTardis service account
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.name + ' | ' + self.ip_address


class RemoteHostAdmin(admin.ModelAdmin):
    fields = ['name', 'ip_adress', 'endpoint', 'managed', 'users', 'groups']


# Register the models with the admin
if apps.is_installed(GlobusConfig.name):
    admin.site.register(RemoteHost, RemoteHostAdmin)
