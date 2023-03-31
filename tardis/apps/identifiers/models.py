import logging

from django.db import models

from tardis.apps.projects.models import Institution, Project
from tardis.tardis_portal.models.dataset import Dataset
from tardis.tardis_portal.models.experiment import Experiment
from tardis.tardis_portal.models.facility import Facility
from tardis.tardis_portal.models.instrument import Instrument

logger = logging.getLogger(__name__)


class DatasetID(models.Model):
    """A model that adds a ID field to an dataset model
    :attribute dataset: A ForeignKey pointing to the related Dataset
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    class Meta:
        app_label = "identifiers"

    def __str__(self):
        return self.identifier or "No Identifier"


class ExperimentID(models.Model):
    """A model that adds a ID field to an experiment model
    :attribute experiment: A ForeignKey pointing to the related Experiment
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    class Meta:
        app_label = "identifiers"

    def __str__(self):
        return self.identifier or "No Identifier"


class FacilityID(models.Model):
    """A model that adds a ID field to an facility model
    :attribute facility: A ForeignKey pointing to the related Facility
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    def __str__(self):
        return self.identifier or "No Identifier"

    class Meta:
        app_label = "identifiers"


class InstrumentID(models.Model):
    """A model that adds a ID field to an instrument model
    :attribute instrument: A ForeignKey pointing to the related Instrument
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    class Meta:
        app_label = "identifiers"

    def __str__(self):
        return self.identifier or "No Identifier"


class ProjectID(models.Model):
    """A model that adds a ID field to a Project model
    :attribute project: A ForeignKey pointing to the related Project
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    class Meta:
        app_label = "identifiers"

    def __str__(self):
        return self.identifier or "No Identifier"


class InstitutionID(models.Model):
    """A model that adds a ID field to a Institution model
    :attribute institution: A ForeignKey pointing to the related Institution
    :attribute identifier: A CharField containing the UNIQUE identifier
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=True, blank=True, unique=True)

    class Meta:
        app_label = "identifiers"

    def __str__(self):
        return self.identifier or "No Identifier"
