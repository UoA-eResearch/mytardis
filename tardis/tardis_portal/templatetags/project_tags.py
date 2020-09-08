from django import template
from django.template.defaultfilters import pluralize, filesizeformat
from django.contrib.humanize.templatetags.humanize import naturalday

from ..util import get_local_time
from ..util import render_mustache, render_public_access_badge
from ..models.experiment import Experiment

register = template.Library()

@register.simple_tag
def project_get_experiments(project_id, user):
    """
    Return the 5 most recently updated experiments for this project
    """
    experiments = Experiment.safe.all(user).filter(project__id=project_id).order_by('-update_time')[:4]
    return experiments
