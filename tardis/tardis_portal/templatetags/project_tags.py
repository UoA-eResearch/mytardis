from django import template
from django.template.defaultfilters import pluralize
from django.contrib.humanize.templatetags.humanize import naturalday

from ..util import get_local_time
from ..util import render_mustache # render_public_access_badge
from ..models.experiment import Experiment
from ..models.dataset import Dataset

register = template.Library()

def get_all_project_experiments(project_id, user):
    """
    Returns all experiment objects in a project.
    """
    return Experiment.safe.all(user).filter(project__id=project_id)

@register.simple_tag
def project_get_recent_experiments(project_id, user):
    """
    Return the 5 most recently updated experiments for this project
    """
    experiments = Experiment.safe.all(user).filter(project__id=project_id).order_by('-update_time')[:4]
    return experiments

@register.simple_tag
def project_experiments_badge(project_id, user):
    """
    Displays a badge with the number of experiments for this project.
    """
    count = Experiment.safe.all(user).filter(project__id=project_id).count()
    return render_mustache('tardis_portal/badges/experiment_count', {
        'title': "%d experiment%s" % (count, pluralize(count)),
        'count': count,
    })

@register.simple_tag
def project_datafiles_badge(project, user):
    """
    Displays a badge with the number of datafiles for this project.
    """
    count = project.get_datafiles(user).count()
    return render_mustache('tardis_portal/badges/datafile_count', {
        'title': "%d file%s" % (count, pluralize(count)),
        'count': count,
    })

@register.simple_tag
def project_datasets_badge(project_id, user):
    """
    Displays a badge with the number of datafiles for this project
    """
    count = 0
    for experiment in get_all_project_experiments(project_id, user):
        count += Dataset.safe.all(user).filter(experiments__id=experiment.id).count()
    return render_mustache('tardis_portal/badges/dataset_count', {
        'title': "%d dataset%s" % (count, pluralize(count)),
        'count': count,
    })


@register.filter
def project_last_updated_badge(project):
    return render_mustache('tardis_portal/badges/last_updated_badge', {
        'actual_time': get_local_time(project.start_date)\
                        .strftime('%a %d %b %Y %H:%M'),
        'iso_time': get_local_time(project.start_date).isoformat(),
        'natural_time': naturalday(project.start_date)
    })

@register.filter
def project_public_access_badge(project):
    """
    Displays a badge the level of public access for this experiment
    """
    # return render_public_access_badge(project)
