'''
RESTful API for MyTardis Globus app.
Implemented with Tastypie.

.. moduleauthor:: Mike Laverick <mikelaverick@btinternet.com>
'''

import json
import logging
#from datetime import datetime

from django.conf import settings
#from django.template.defaultfilters import filesizeformat

from tastypie import fields
from tastypie.resources import Resource, Bundle
from tastypie.serializers import Serializer
#from tastypie.exceptions import ImmediateHttpResponse
#from tastypie.http import HttpUnauthorized

from tardis.tardis_portal.models import Experiment, Dataset, DataFile
from tardis.tardis_portal.api import default_authentication
#from tardis.tardis_portal.auth import decorators as authz
from .models import RemoteHost, TransferLog


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        logging.info("The data is " + str(data))
        options = options or {}
        data = self.to_simple(data, options)
        return json.dumps(data, cls=json.JSONEncoder,
                          sort_keys=True, ensure_ascii=False,
                          indent=self.json_indent) + "\n"


if settings.DEBUG:
    default_serializer = PrettyJSONSerializer()
else:
    default_serializer = Serializer()

# API object to return accessible hosts
class RemoteHostsObject(object):
    def __init__(self, hosts=None):
        self.hosts = hosts

# API object to check selected objects and return invalid options
class DownloadCartObject(object):
    def __init__(self, projects=None, experiments=None, datasets=None,
                 datafiles=None):
        self.projects = projects
        self.experiments = experiments
        self.datasets = datasets
        self.datafiles = datafiles

# API object to submit objects for globus transfer
# Could just re-use the cart object? and for the size API?

#class GlobusSubmissionObject(object):
#    def __init__(self, objects=None, id=None):
#        self.objects = objects
#        self.id = id


class RemoteHostAppResource(Resource):
    """Tastypie resource for RemoteHosts"""
    hosts = fields.ApiField(attribute='hosts', null=True)

    class Meta:
        resource_name = 'remotehost'
        list_allowed_methods = ['get']
        serializer = default_serializer
        authentication = default_authentication
        object_class = RemoteHostsObject
        always_return_data = True

    def get_object_list(self, request):
        if not request.user.is_authenticated:
            raise Exception(message="User must be logged in to retrieve remote hosts")
        hosts = RemoteHost.objects.filter(users=request.user)
        for group in request.user.groups.all():
            hosts |= RemoteHost.objects.filter(groups=group)
        response = []
        for host in hosts.distinct():
            response.append({"id":host.id, "name":host.name})
        return [RemoteHostsObject(hosts=response)]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)


class ValidateAppResource(Resource):
    """Tastypie resource to validate Download Cart contents"""
    projects = fields.ApiField(attribute='projects', null=True)
    experiments = fields.ApiField(attribute='experiments', null=True)
    datasets = fields.ApiField(attribute='datasets', null=True)
    datafiles = fields.ApiField(attribute='datafiles', null=True)

    class Meta:
        resource_name = 'transfer_validation'
        list_allowed_methods = ['post']
        serializer = default_serializer
        authentication = default_authentication
        object_class = DownloadCartObject
        always_return_data = True


    def get_object_list(self, request):
        return request

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        bundle = self.create_return_invalid(bundle)
        return bundle


    def create_return_invalid(self, bundle):
        user = bundle.request.user
        if not user.is_authenticated:
            raise Exception(message="User must be logged in to validate download cart")
        groups = user.groups.all()

        host_id = bundle.data.get('remote_host', None)
        proj_ids = bundle.data.get('projects', [])
        exp_ids = bundle.data.get('experiments', [])
        set_ids = bundle.data.get('datasets', [])
        file_ids = bundle.data.get('datafiles', [])
        if not host_id:
            raise Exception(message="Please specify a remote host")
        if not any([proj_ids, exp_ids, set_ids, file_ids]):
            raise Exception(message="Please provide Projects/Experiments/Datasets/Datafiles for validation")
        # Query for related projects, and unpack into list here for efficiency
        related_projects = [*{*RemoteHost.objects.filter(id=host_id).prefetch_related('projects'
                                ).values_list("projects__id", flat=True)}]

        #proj_list, exp_list, set_list, file_list = [], [], [], []
        #proj_list = [id for id in proj_ids if id not in related_projects]

        exp_projs = [*{*Experiment.objects.filter(pk__in=[exp_ids]).select_related(
                                      'project').values_list("id", "project__id")}]

        set_projs = [*{*Dataset.objects.filter(pk__in=[set_ids]).prefetch_related(
                        "experiments", "experiments__project").values_list(
                        "id", "experiments__project__id")}]

        file_projs = [*{*DataFile.objects.filter(pk__in=[file_ids]).prefetch_related(
                        "dataset", "dataset__experiments", "dataset__experiments__project").values_list(
                        "id", "dataset__experiments__project__id")}]

        proj_list = [id for id in proj_ids if id not in related_projects]
        exp_list = [id for (id, proj_id) in exp_projs if proj_id not in related_projects]
        set_list = [id for (id, proj_id) in set_projs if proj_id not in related_projects]
        file_list = [id for (id, proj_id) in file_projs if proj_id not in related_projects]

        bundle.obj = DownloadCartObject(projects=proj_list, experiments=exp_list,
                                        datasets=set_list, datafiles=file_list)
        return bundle
