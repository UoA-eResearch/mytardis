from django.apps import apps
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from tardis.tardis_portal.models.datafile import DataFile
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
    users = models.ManyToManyField(User, related_name='remotehosts', blank=True)
    groups = models.ManyToManyField(Group, related_name='remotehosts', blank=True)
    projects = models.ManyToManyField(Project, related_name='remotehosts', blank=True)

    def __str__(self):
        return self.name + ' | ' + self.ip_address


@python_2_unicode_compatible
class TransferLog(models.Model):
    """``
    A MyTardis log of a Globus transfer request.
    """
    STATUS_NEW = 1
    STATUS_SUBMITTED = 2
    STATUS_SUCCEEDED = 3
    STATUS_FAILED = 4

    STATUS_CHOICES = (
        (STATUS_NEW, 'Transfer pending'),
        (STATUS_SUBMITTED, 'Transfer submitted to Globus'),
        (STATUS_SUCCEEDED, 'Transfer succeeded'),
        (STATUS_FAILED, 'Transfer failed'),
    )

    transfer_id = models.CharField('Name', max_length=50, blank=True)
    initiated_by = models.ForeignKey(User, related_name='initiated_by',
                                     on_delete=models.CASCADE)
    remote_host = models.ForeignKey(RemoteHost)
    datafiles = models.ManyToManyField(DataFile, related_name='transferlogs')
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,
                                              null=False, default=STATUS_NEW)

    def __str__(self):
        if self.transfer_id:
            return self.transfer_id
        else:
            return "Pending: "+ str(self.id)


class RemoteHostAdmin(admin.ModelAdmin):
    fields = ['name', 'ip_adress', 'endpoint', 'managed', 'users', 'groups', 'projects']


class TransferLogAdmin(admin.ModelAdmin):
    fields = ['transfer_id', 'initiated_by', 'remote_host', 'datafiles', 'status']


# Register the models with the admin
if apps.is_installed(GlobusConfig.name):
    admin.site.register(RemoteHost, RemoteHostAdmin)
    admin.site.register(TransferLog, TransferLogAdmin)
