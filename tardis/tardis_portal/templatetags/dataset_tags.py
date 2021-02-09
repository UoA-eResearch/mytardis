from datetime import datetime

from django import template
from django.template.defaultfilters import pluralize, filesizeformat

from ..util import render_mustache
from ..views import get_dataset_info
from ..models.dataset import Dataset
from ..models.experiment import Experiment
from ..models.datafile import DataFile

register = template.Library()


@register.simple_tag
def dataset_tiles(experiment_id, request, include_thumbnails):
    # only show 8 datasets for initial load
    datasets = Dataset.safe.all(request.user).filter(experiments__id=experiment_id
                                             ).order_by('description')[:8]

    # Get data to template (used by JSON service too)
    # ?? doesn't seem to be used by JSON service at all
    data = (get_dataset_info(ds, request, bool(include_thumbnails),
                             exclude=['datasettype', 'size'])
            for ds in datasets)

    class DatasetInfo(object):

        def __init__(self, **data):
            self.__dict__.update(data)

        def experiment_badge(self):
            count = len(self.experiments)
            return render_mustache('tardis_portal/badges/experiment_count', {
                'title': "In %d experiment%s" % (count, pluralize(count)),
                'count': count,
            })

        def dataset_size_badge(self):
            if hasattr(self, 'size'):
                return dataset_size_badge(request, size=self.size)
            ds = Dataset.objects.get(id=self.id)
            return dataset_size_badge(request, dataset=ds)

        def dataset_datafiles_badge(self):
            if hasattr(self, 'datafiles'):
                return dataset_datafiles_badge(count=len(self.datafiles))
            ds = Dataset.objects.get(id=self.id)
            return dataset_datafiles_badge(ds)

    class DatasetsInfo(object):
        # Generator which renders a dataset at a time
        def datasets(self):
            for ds in data:
                yield render_mustache('tardis_portal/dataset_tile',
                                      DatasetInfo(**ds))

    # Render template
    return render_mustache('tardis_portal/dataset_tiles', DatasetsInfo())


@register.simple_tag
def dataset_count(experiment_id, user):
    """
    Count the number of Datasets in Experiment, obeying ACLs for user
    """
    #count = Dataset.safe.all(user).filter(experiments__id=experiment_id).count()
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
    return count


@register.simple_tag
def datafile_count(dataset_id, user):
    """
    Count the number of Datafiles in Dataset, obeying ACLs for user
    """
    #count = DataFile.safe.all(user).filter(dataset__id=dataset_id).count()

    query = user.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                             ).filter(datafile__dataset__id=dataset_id
                             ).exclude(effectiveDate__gte=datetime.today(),
                                       expiryDate__lte=datetime.today()).values_list("datafile__id")
    for group in user.groups.all():
        query |= group.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                                 ).filter(datafile__dataset__id=dataset_id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("datafile__id")

    count = query.distinct().count()

    return count


@register.simple_tag
def dataset_experiments_badge(dataset, user):
    """
    Displays a badge with the number of experiments for this dataset
    """

    query = user.experimentacls.select_related("experiment").prefetch_related("experiment__datasets"
                             ).filter(experiment__datasets__id=dataset.id
                             ).exclude(effectiveDate__gte=datetime.today(),
                                       expiryDate__lte=datetime.today()).values_list("experiment__id")
    for group in user.groups.all():
        query |= group.experimentacls.select_related("experiment").prefetch_related("experiment__datasets"
                                 ).filter(experiment__datasets__id=dataset.id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("experiment__id")
    count = query.distinct().count()

    return render_mustache('tardis_portal/badges/experiment_count', {
        'title': "In %d experiment%s" % (count, pluralize(count)),
        'count': count,
    })


@register.filter
def dataset_datafiles_badge(dataset=None, count=None):
    """
    Displays an badge with the number of datafiles for this dataset
    """
    if count is None:

        query = user.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                                 ).filter(datafile__dataset__id=dataset.id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("datafile__id")
        for group in user.groups.all():
            query |= group.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                                     ).filter(datafile__dataset__id=dataset.id
                                     ).exclude(effectiveDate__gte=datetime.today(),
                                               expiryDate__lte=datetime.today()).values_list("datafile__id")

        count = query.distinct().count()
        #count = dataset.datafile_set.count()
    return render_mustache('tardis_portal/badges/datafile_count', {
        'title': "%d file%s" % (count, pluralize(count)),
        'count': count,
    })


@register.simple_tag
def dataset_datafiles_badge_notile(dataset, user):
    """
    Displays an badge with the number of datafiles for this dataset
    None tile mode
    """
    #count = DataFile.safe.all(user).filter(dataset__id=dataset.id).count()
    query = user.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                             ).filter(datafile__dataset__id=dataset.id
                             ).exclude(effectiveDate__gte=datetime.today(),
                                       expiryDate__lte=datetime.today()).values_list("datafile__id")
    for group in user.groups.all():
        query |= group.datafileacls.select_related("datafile").prefetch_related("datafile__dataset"
                                 ).filter(datafile__dataset__id=dataset.id
                                 ).exclude(effectiveDate__gte=datetime.today(),
                                           expiryDate__lte=datetime.today()).values_list("datafile__id")

    count = query.distinct().count()
    return render_mustache('tardis_portal/badges/datafile_count', {
        'title': "%d file%s" % (count, pluralize(count)),
        'count': count,
    })


@register.simple_tag
def dataset_size_badge_notile(dataset, user):
    """
    Displays a badge with the total size of the files in this dataset
    """
    size = filesizeformat(dataset.get_size(user))
    return render_mustache('tardis_portal/badges/size', {
        'title': "Dataset size is ~%s" % size,
        'label': size,
    })


@register.filter
def dataset_size_badge(request, dataset=None, size=None):
    """
    Displays an badge with the total size of the files in this experiment
    """
    if size is None:
        size = filesizeformat(dataset.get_size(request.user))
    else:
        size = filesizeformat(size)
    return render_mustache('tardis_portal/badges/size', {
        'title': "Dataset size is ~%s" % size,
        'label': size,
    })
