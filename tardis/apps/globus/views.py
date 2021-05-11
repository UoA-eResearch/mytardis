# pylint: disable=http-response-with-json-dumps,http-response-with-content-type-json
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.db import transaction

#from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.models import Project, Experiment, Dataset, DataFile
from .models import RemoteHost, TransferLog
from tardis.tardis_portal.shortcuts import return_response_error

@login_required
def get_accessible_hosts(request):
    """
    Retrieves all accessible hosts
    :param Request request: request object
    :return: json object with accessible hosts
    :rtype: HttpResponse
    """
    hosts = RemoteHost.objects.filter(users=request.user)
    for group in request.user.groups.all():
        hosts |= RemoteHost.objects.filter(groups=group)
    response = []
    for host in hosts.distinct():
        response.append(host)
        #TODO provide the necessary mcgubbins here, so that the response is clean
    return HttpResponse(json.dumps(response), content_type='application/json')


@login_required
def globus_initiate(request):

    object_type = request.GET.get('object_type')
    object_id = request.GET.get('object_id')

    if not has_download_access(request, object_id, object_type):
        return return_response_error(request)

    remote_vm = RemoteHost.objects.get(pk=2)
    # GET REMOTE HOST #2
    # need some nice checks for object validity + permissions

    if object_type == 'project':
        project = Project.objects.get(id=object_id)
        datafiles = project.get_datafiles(request.user)

    elif object_type == 'experiment':
        exp = Experiment.objects.get(id=object_id)
        datafiles = exp.get_datafiles(request.user)

    elif object_type == 'dataset':
        dataset = Dataset.objects.get(id=object_id)
        datafiles = dataset.get_datafiles(request.user)

    elif object_type == 'datafile':
        datafiles = DataFile.safe.get(id=object_id)
    else:
        raise NotImplementedError(object_type)

    with transaction.atomic():
        newtransferlog = TransferLog.objects.create(
            initiated_by = request.user,
            remote_host = remote_vm,
            status = TransferLog.STATUS_NEW)
        newtransferlog.save()
        newtransferlog.datafiles.add(*datafiles)
        newtransferlog.save()

    c = {
        'site_name': getattr(settings, 'SITE_TITLE', 'MyTardis'),
    }
    return render(request, template_name='globus/index.html', context=c)
    # atomic create transferLog
    # for this, hardcode which remotehosts to use i.e. 1 and 2
    # Get the remote hosts that are manually created already
    # CAVEAT probably change the model association with TransferLog in the future, for proof of concept just leave it at DataFile level
