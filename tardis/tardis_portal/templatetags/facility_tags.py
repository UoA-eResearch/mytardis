from django import template
from django.conf import settings
from ..models.facility import is_facility_manager

register = template.Library()


@register.filter
def check_if_facility_manager(request):
    """
    Custom template filter to identify whether a user is a
    facility manager.
    """
    if request.user.is_authenticated:
        return is_facility_manager(request.user)
    return False


@register.filter
def check_if_instrument_profile_active(request):
    """
    Custom template filter to check if the instrument_profile app
    is active.
    """
    return "tardis.apps.instrument_profile" in settings.INSTALLED_APPS
