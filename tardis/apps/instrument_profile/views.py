import logging

from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required, permission_required
from tardis.apps.instrument_profile.models import InstrumentProfile
from tardis.apps.instrument_profile.forms import InstrumentProfileForm
from tardis.tardis_portal.views.utils import _redirect_303
from tardis.tardis_portal.shortcuts import (
    render_response_index,
    return_response_error,
    return_response_not_found,
)
from tardis.tardis_portal.models.instrument import Instrument

logger = logging.getLogger(__name__)


class InstrumentProfileView(TemplateView):
    template_name = "view_instrument.html"

    def get_context_data(self, request, instrument_profile, **kwargs):
        """
        Prepares the values to be passed to the default instrument_profile view,
        respecting authorization rules. Returns a dict of values (the context).
        :param request: a HTTP request object
        :type request: :class:`django.http.HttpRequest`
        :param instrument_profile: the Instrument model instance
        :type instrument_profile: tardis.apps.instrument_profile.models.InstrumentProfile
        :param dict kwargs:
        :return: A dictionary of values for the view/template.
        :rtype: dict
        """
        c = super().get_context_data(**kwargs)

        instrument = instrument_profile.instrument
        if instrument:
            instrument_name = instrument.name
            instrument_facility = instrument.facility
            facility_name = instrument_facility.name if instrument_facility else None
        else:
            instrument_name = None
            facility_name = None
        c.update(
            {
                "instrument_name": instrument_name,
                "instrument_profile": instrument_profile,
                "parametersets": instrument.getParameterSets().exclude(
                    schema__hidden=True
                ),
                "from_facility": facility_name,
            }
        )
        # _add_protocols_and_organizations(request, instrument_profile, c)
        return c

    def get(self, request, *args, **kwargs):
        """
        View an existing dataset.
        This default view can be overriden by defining a dictionary
        DATASET_VIEWS in settings.
        :param request: a HTTP request object
        :type request: :class:`django.http.HttpRequest`
        :param list args:
        :param dict kwargs:
        :return: The Django response object
        :rtype: :class:`django.http.HttpResponse`
        """
        instrument_profile_id = kwargs.get("instrument_profile_id", None)
        if instrument_profile_id is None:
            return return_response_error(request)
        try:
            instrument_profile = InstrumentProfile.objects.get(pk=instrument_profile_id)
        except PermissionDenied:
            return return_response_error(request)
        except InstrumentProfile.DoesNotExist:
            return return_response_not_found(request)

        # view_override = self.find_custom_view_override(request, instrument_profile)
        # if view_override is not None:
        #    return view_override
        c = self.get_context_data(request, instrument_profile, **kwargs)

        template_name = kwargs.get("template_name", None)
        if template_name is None:
            template_name = self.template_name
        return render_response_index(request, template_name, c)


@permission_required("tardis_portal.add_experiment")  # TODO Set appropriate permission
@login_required
def create_instrument_profile(request):

    c = {
        "subtitle": "Create Instrument Profile",
        "user_id": request.user.id,
    }

    # Process form or prepopulate it
    if request.method == "POST":
        form = InstrumentProfileForm(request.POST)
        if form.is_valid():
            instrument = Instrument()
            instrument.name = form.cleaned_data["name"]
            instrument.facility = form.cleaned_data["facility"]
            instrument.save()
            instrument_profile = instrument.profile
            instrument_profile.landing_page = form.cleaned_data["landing_page"]
            instrument_profile.owner = form.cleaned_data["owner"]
            instrument_profile.owner_contact = form.cleaned_data["owner_contact"]
            instrument_profile.manufacturer = form.cleaned_data["manufacturer"]
            instrument_profile.instrument_model = form.cleaned_data["instrument_model"]
            instrument_profile.description = form.cleaned_data["description"]
            instrument_profile.instrument_type = form.cleaned_data["instrument_type"]
            instrument_profile.measured_variable = form.cleaned_data[
                "measured_variable"
            ]
            instrument_profile.pid = form.cleaned_data["pid"]
            instrument_profile.asset_tag = form.cleaned_data["asset_tag"]
            instrument_profile.save()
            return _redirect_303("view_instrument_profile", instrument_profile.id)
    else:
        form = InstrumentProfileForm()

    c = {
        "form": form,
        "subtitle": "Create Instrument Profile",
        "user_id": request.user.id,
    }
    return render_response_index(request, "create_instrument.html", c)


@login_required
def edit_instrument_profile(request, instrument_profile_id):
    # if not has_dataset_write(request, dataset_id): # need appropriate permissions here
    #    return HttpResponseForbidden()
    instrument_profile = InstrumentProfile.objects.get(id=instrument_profile_id)

    # Process form or prepopulate it
    if request.method == "POST":
        form = InstrumentProfileForm(request.POST)
        instrument = instrument_profile.instrument
        if form.is_valid():
            instrument.name = form.cleaned_data["name"]
            instrument.facility = form.cleaned_data["facility"]
            instrument_profile.landing_page = form.cleaned_data["landing_page"]
            instrument_profile.owner = form.cleaned_data["owner"]
            instrument_profile.owner_contact = form.cleaned_data["owner_contact"]
            instrument_profile.manufacturer = form.cleaned_data["manufacturer"]
            instrument_profile.instrument_model = form.cleaned_data["instrument_model"]
            instrument_profile.description = form.cleaned_data["description"]
            instrument_profile.instrument_type = form.cleaned_data["instrument_type"]
            instrument_profile.measured_variable = form.cleaned_data[
                "measured_variable"
            ]
            instrument_profile.pid = form.cleaned_data["pid"]
            instrument_profile.asset_tag = form.cleaned_data["asset_tag"]
            instrument.save()
            instrument_profile.save()
            return _redirect_303("view_instrument_profile", instrument_profile.id)
    else:
        instrument = instrument_profile.instrument
        initialisation_dict = {
            "name": instrument.name,
            "facility": instrument.facility,
            "landing_page": instrument_profile.landing_page,
            "owner": instrument_profile.owner,
            "owner_contact": instrument_profile.owner_contact,
            "manufacturer": instrument_profile.manufacturer,
            "instrument_model": instrument_profile.instrument_model,
            "description": instrument_profile.description,
            "instrument_type": instrument_profile.instrument_type,
            "measured_variable": instrument_profile.measured_variable,
            "pid": instrument_profile.pid,
            "asset_tag": instrument_profile.asset_tag,
        }
        form = InstrumentProfileForm(initial=initialisation_dict)

    c = {
        "form": form,
        "instrument_profile": instrument_profile,
        "subtitle": "Edit Instrument Profile",
    }
    return render_response_index(request, "create_instrument.html", c)
