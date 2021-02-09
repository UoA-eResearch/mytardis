from datetime import datetime

from django import template
from django.template.defaultfilters import pluralize, filesizeformat
from django.contrib.humanize.templatetags.humanize import naturalday

from ..util import get_local_time
from ..util import render_mustache, render_public_access_badge
from ..models.dataset import Dataset

register = template.Library()


@register.inclusion_tag('tardis_portal/experiment_tags/experiment_browse_item.html')
def experiment_browse_item(experiment, **kwargs):
    """
    Displays an experiment for a browsing view.
    """
    show_images = kwargs.get('can_download') or \
        experiment.public_access == experiment.PUBLIC_ACCESS_FULL
    return {
        'experiment': experiment,
        'show_images': show_images
    }


@register.simple_tag
def experiment_datasets_badge(experiment_id, user):
    """
    Displays an badge with the number of datasets for this experiment
    """

    query = user.datasetacls.select_related("dataset").prefetch_related("dataset__experiments"
                             ).filter(dataset__experiments__id=experiment_id
                             ).exclude(effectiveDate__gte=datetime.today(),
                                       expiryDate__lte=datetime.today()).values_list("dataset__id")
    for group in user.groups.all():
        query |= group.datasetacls.select_related("dataset").prefetch_related("dataset__experiments"
                                 ).filter(dataset__experiments__id=experiment_id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("dataset__id")

    count = query.distinct().count()
    return render_mustache('tardis_portal/badges/dataset_count', {
        'title': "%d dataset%s" % (count, pluralize(count)),
        'count': count,
    })


@register.simple_tag
def experiment_datafiles_badge(experiment, user):
    """
    Displays an badge with the number of datafiles for this experiment
    """

    query = user.datafileacls.select_related("datafile").prefetch_related("datafile__dataset__experiments"
                             ).filter(datafile__dataset__experiments__id=experiment.id
                             ).exclude(effectiveDate__gte=datetime.today(),
                                       expiryDate__lte=datetime.today()).values_list("datafile__id")
    for group in user.groups.all():
        query |= group.datafileacls.select_related("datafile").prefetch_related("datafile__dataset__experiments"
                                 ).filter(datafile__dataset__experiments__id=experiment.id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("datafile__id")

    count = query.distinct().count()

    return render_mustache('tardis_portal/badges/datafile_count', {
        'title': "%d file%s" % (count, pluralize(count)),
        'count': count,
    })


@register.filter
def experiment_last_updated_badge(experiment):
    return render_mustache('tardis_portal/badges/last_updated_badge', {
        'actual_time': get_local_time(experiment.update_time)\
                        .strftime('%a %d %b %Y %H:%M'),
        'iso_time': get_local_time(experiment.update_time).isoformat(),
        'natural_time': naturalday(experiment.update_time),
    })


@register.filter
def experiment_public_access_badge(experiment):
    """
    Displays an badge the level of public access for this experiment
    """
    return render_public_access_badge(experiment)


@register.simple_tag
def experiment_size_badge(experiment, user):
    """
    Displays an badge with the total size of the files in this experiment
    """
    size = filesizeformat(experiment.get_size(user))
    return render_mustache('tardis_portal/badges/size', {
        'title': "Experiment size is ~%s" % size,
        'label': size,
    })


@register.inclusion_tag('tardis_portal/experiment_tags/experiment_badges.html')
def experiment_badges(experiment, user, **kwargs):
    """
    Displays badges for an experiment for displaying in an experiment list view
    """
    return {
        'experiment': experiment,
        'user': user
    }


@register.inclusion_tag('tardis_portal/experiment_tags/experiment_authors.html')
def experiment_authors(experiment, **kwargs):
    """
    Displays an experiment's authors in an experiment list view
    """
    return {
        'experiment': experiment
    }


@register.inclusion_tag('tardis_portal/experiment_tags/experiment_download_link.html')
def experiment_download_link(experiment, **kwargs):
    """
    Displays a download link for an experiment in a list view
    """
    return {
        'experiment': experiment
    }
