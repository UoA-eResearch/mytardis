from django.urls import re_path

from tardis.apps.idw.views.idwyaml import IDWYAMLView
from tardis.apps.idw.views.idw import IDWIndexView

app_name = "tardis.apps.idw"

urlpatterns = [re_path("idw-yaml/", IDWYAMLView.as_view(), name="idw-yaml"),
    re_path("^$", IDWIndexView.as_view(), name="index")
]