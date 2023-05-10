from django.contrib import admin

from tardis.apps.autoarchive.models import DataFileAutoArchive, ProjectAutoArchive

admin.site.register(DataFileAutoArchive)
admin.site.register(ProjectAutoArchive)
