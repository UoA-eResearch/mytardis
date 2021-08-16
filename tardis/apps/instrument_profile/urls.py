"""
URLs for instruments
"""
from django.conf.urls import url

from tardis.apps.instrument_profile.views import InstrumentProfileView

from tardis.apps.instrument_profile.views import (
    create_instrument_profile,
    edit_instrument_profile,
)

urlpatterns = [
    url(
        r"^view/(?P<instrument_profile_id>\d+)/$",
        InstrumentProfileView.as_view(),
        name="view_instrument_profile",
    ),
    url(
        r"^edit/(?P<instrument_profile_id>\d+)/$",
        edit_instrument_profile,
        name="edit_instrument_profile",
    ),
    url(
        r"^create/$",
        create_instrument_profile,
        name="create_instrument_profile",
    ),
]
