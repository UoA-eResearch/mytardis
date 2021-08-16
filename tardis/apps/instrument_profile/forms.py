import logging

from django import forms

from tardis.apps.instrument_profile.models import InstrumentProfile
from tardis.tardis_portal.models import Facility

logger = logging.getLogger(__name__)


class InstrumentProfileForm(forms.Form):
    name = forms.CharField(max_length=400, required=True)
    facility = forms.ModelChoiceField(queryset=Facility.objects.all())
    landing_page = forms.URLField()
    owner = forms.CharField(max_length=400, required=True)
    owner_contact = forms.CharField(
        max_length=400, required=False
    )  # TODO add validation for email?
    manufacturer = forms.CharField(max_length=400, required=True)
    instrument_model = forms.CharField(max_length=400, required=False)
    description = forms.CharField(widget=forms.Textarea, required=False)
    instrument_type = forms.CharField(max_length=400, required=False)
    measured_variable = forms.CharField(max_length=400, required=False)
    pid = forms.CharField(max_length=400, required=False)
    asset_tag = forms.CharField(max_length=200, required=False)
