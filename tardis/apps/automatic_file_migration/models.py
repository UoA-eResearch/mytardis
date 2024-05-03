"""An extension to the project model, the automatic file mover app adds a source and destination 
target and a delete_on_move flag to determine if the file should be copied or moved to the 
destination.
Finally we add an expiry date field to the project model that will be used to determine when 
the data will be automatically deleted.
"""
from datetime import datetime, timedelta

from django.conf import settings
from django.db import models

from tardis.apps.automatic_file_migration.enumerators import StorageClassification
from tardis.apps.projects.models import Project
from tardis.tardis_portal.models.storage import StorageBox


class ProjectStorage(models.Model):
    """A model to add additional fields to the Project model to store the necessary information
    that will allow for the automatic movement of data and it's deletion.
    """

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="storage",
    )
    source = models.ForeignKey(
        StorageBox,
        on_delete=models.CASCADE,
        related_name="source",
    )
    target = models.ManyToManyField(
        StorageBox,
        related_name="target",
    )
    move_file_not_copy = models.BooleanField(default=False)
    must_delete_after = models.DateField(
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "storage"

    @property
    def expiry_date(
        self,
        classification: StorageClassification = StorageClassification.DEFAULT,
    ):
        if self.project.end_time:
            return self.project.end_time + classification.value["retention_period"]
        project_end = datetime.now() + timedelta(days=settings.DEFAULT_PROJECT_LENGTH)
        return project_end + classification.value["retention_period"]

    def __str__(self):
        return self.project.name

    def move_files():
        pass

    def copy_files():
        pass

    def delete_files():
        pass

    def _get_verified_dfos_from_target():
        pass

    def _get_verified_dfos_from_source():
        pass

    # Need a way of triggering this on data which is added to a project Many-To-Many type relationships
