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
    """

    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("identifier",), name="unique_dataset_id"),
        ]


class ExperimentID(models.Model):
    """A model that adds a ID field to an experiment model
    :attribute experiment: A ForeignKey pointing to the related Experiment
    """

    experiment = models.ForeignKey(
        Experiment,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("identifier",), name="unique_experiment_id"
            ),
        ]


class FacilityID(models.Model):
    """A model that adds a ID field to an facility model
    :attribute facility: A ForeignKey pointing to the related Facility
    """

    facility = models.ForeignKey(
        Facility,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("identifier",), name="unique_facility_id"),
        ]


class InstrumentID(models.Model):
    """A model that adds a ID field to an instrument model
    :attribute instrument: A ForeignKey pointing to the related Instrument
    """

    instrument = models.ForeignKey(
        Instrument,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("identifier",), name="unique_instrument_id"
            ),
        ]


class ProjectID(models.Model):
    """A model that adds a ID field to a Project model
    :attribute project: A ForeignKey pointing to the related Project
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("identifier",), name="unique_project_id"),
        ]


class InstitutionID(models.Model):
    """A model that adds a ID field to a Institution model
    :attribute institution: A ForeignKey pointing to the related Institution
    """

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        related_name="identifiers",
    )
    identifier = models.CharField(max_length=400, null=False, blank=False)

    def __str__(self):
        if self.identifier:
            return self.identifier
        return "No Identifier"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("identifier",), name="unique_institution_id"
            ),
        ]
