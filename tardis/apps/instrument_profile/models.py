import logging

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from tardis.tardis_portal.models.instrument import Instrument

logger = logging.getLogger(__name__)


class InstrumentProfile(models.Model):
    """A model to implement the minimum metadata schema for an instrument

    :attribute instrument: A OneToOneField pointing to a related Instrument
    :attribute landing_page: A URLField that holds the instrument landing page (defaults to MyTardis)
    :attribute owner: A CharField containing the owner
    :attribute owner_contact: A CharField containing the owner email address
    :attribute manufacturer: A CharField containing the manufacturer's name
    :attribute instrument_model: A CharField containing the model of the instrument in question
    :attribute description: A TextField containing technical description of the device and its capabilities
    :attribute instrument_type: A CharField containing the classification of the type of the instrument
    :attribute measured_variable: A CharField containing the variable(s) that this instrument measures
    :attribute pid: A CharField holding the chosen PID
    """

    instrument = models.OneToOneField(
        Instrument, on_delete=models.CASCADE, related_name="profile"
    )
    landing_page = models.URLField(null=True, blank=True)
    owner = models.CharField(
        max_length=400, null=False, blank=False, default="No Owner - Please Udate"
    )
    owner_contact = models.CharField(max_length=400, null=True, blank=True)
    manufacturer = models.CharField(
        max_length=400,
        null=False,
        blank=False,
        default="No Manufacturer - Please Update",
    )
    instrument_model = models.CharField(max_length=400, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    instrument_type = models.CharField(max_length=400, null=True, blank=True)
    measured_variable = models.CharField(max_length=400, null=True, blank=True)
    pid = models.CharField(max_length=400, null=True, blank=True, unique=True)

    def __str__(self):
        return self.instrument.name

    def get_absolute_url(self):
        """Return the absolute URL to the current ``Instrument``"""
        return reverse(
            "view_instrument_profile", kwargs={"instrument_profile_id": self.id}
        )


@receiver(post_save, sender=Instrument, dispatch_uid="create_instrument_profile")
def create_instrument_profile(sender, instance, created, **kwargs):
    if created:
        InstrumentProfile(instrument=instance).save()
