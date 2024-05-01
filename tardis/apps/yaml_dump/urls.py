from django.urls import re_path

from tardis.apps.yaml_dump.views.idwyaml import IDWYAMLView

urlpatterns = [re_path("idw-yaml/", IDWYAMLView.as_view(), name="idw-yaml")]
