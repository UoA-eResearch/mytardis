import logging

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


from tardis.tardis_portal.models.facility import Facility

logger = logging.getLogger(__name__)


class FacilityProfile(models.Model):
    """An extension to the Facility Model in MyTardis

    :attribute facility: A OneToOneKey relationship to a Facility
    :attribute url: A URL pointing to the facilities home page
    :attribute institution: A Institution model, either Institution from the app or DefaultInstitution
    defined below"""

    facility = models.OneToOneField(
        Facility, on_delete=models.CASCADE, related_name="profile"
    )
    url = models.URLField(max_length=255, null=True, blank=True)
    institution = models.ForeignKey(
        settings.FACILITY_PROFILE_INSTITUTION,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # class Meta:
    #    app_label = "tardis_apps"


@receiver(post_save, sender=Facility, dispatch_uid="create_facility_profile")
def create_facility_profile(sender, instance, created, **kwargs):
    if created:
        FacilityProfile(facility=instance).save()


class DefaultInstitution(models.Model):
    """Placeholder Institution model in case we aren't using a more complete
    Institution model.

    :attribute name: CharField detailing the name of the institution.
    """

    name = models.CharField(max_length=400, null=True, blank=True, unique=True)
