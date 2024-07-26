from django.urls import re_path
from django.contrib.auth.decorators import login_required

from tardis.apps.idw_download.views.idwyaml import IDWYAMLView
from tardis.apps.idw_download.views.idw import IDWIndexView


app_name = "tardis.apps.idw_download"

urlpatterns = [
    re_path("idw-yaml/", login_required(IDWYAMLView.as_view()), name="idw-yaml"),
    re_path("^$", login_required(IDWIndexView.as_view()), name="index")
]
