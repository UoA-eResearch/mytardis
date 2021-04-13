# pylint: disable=http-response-with-json-dumps,http-response-with-content-type-json
import json
import requests

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound
from django.shortcuts import redirect, render

from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.models import Experiment, Dataset
from . import tasks
from .models import RemoteHost

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

    return HttpResponse(json.dumps(response), content_type='application/json')
