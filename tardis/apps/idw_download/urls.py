from django.urls import re_path

from tardis.apps.idw_download.views.idwyaml import IDWYAMLView
from tardis.apps.idw_download.views.idw import IDWIndexView

app_name = "tardis.apps.idw_download"

urlpatterns = [re_path("idw-yaml/", IDWYAMLView.as_view(), name="idw-yaml"),
    re_path("^$", IDWIndexView.as_view(), name="index")
]