from django import forms
from django.conf import settings
from django.contrib.auth.models import User

from tardis.tardis_portal.models import Experiment

from .models import Project

# from django.forms.models import ModelChoiceField


class ProjectForm(forms.ModelForm):
    name = forms.CharField()

    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "principal_investigator",
            # "url",
            "institution",
            "experiments"
            # "embargo_until",
            # "start_time",
            # "end_time",
        ]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["principal_investigator"].queryset = User.objects.exclude(
            pk=settings.PUBLIC_USER_ID
        )
        self.fields["experiments"].queryset = Experiment.safe.all(
            user=self.user, canWrite=True
        )
