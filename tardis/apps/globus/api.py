'''
RESTful API for MyTardis Globus app.
Implemented with Tastypie.

.. moduleauthor:: Mike Laverick <mikelaverick@btinternet.com>
'''

import json
import logging

from django.conf import settings
from django.db import transaction
from tastypie import fields
from tastypie.resources import Resource, Bundle, ModelResource

from tastypie.serializers import Serializer
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpBadRequest, HttpUnauthorized, HttpForbidden, HttpNotFound
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized

from tardis.tardis_portal.api import default_authentication
from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.models import Project, Experiment, Dataset, DataFile
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


class GlobusAuthorization(Authorization):

    def read_list(self, object_list, bundle):
        obj_ids = [obj.id for obj in object_list]
        if not bundle.request.user.is_authenticated:
            raise Unauthorized("User must be logged in to access remote hosts")
        # This assumes a ``QuerySet`` from ``ModelResource``.
        if isinstance(bundle.obj, RemoteHost):
            query = RemoteHost.objects.filter(users=bundle.request.user)
            for group in bundle.request.user.groups.all():
                query |= RemoteHost.objects.filter(groups=group)
            return query.filter(id__in=obj_ids).distinct()
        return []

    def read_detail(self, object_list, bundle):
        if not bundle.request.user.is_authenticated:
            raise Unauthorized("User must be logged in to access remote hosts")
        # Is the requested object accessible by the user?
        if isinstance(bundle.obj, RemoteHost):
            query = RemoteHost.objects.filter(users=bundle.request.user)
            for group in bundle.request.user.groups.all():
                query |= RemoteHost.objects.filter(groups=group)
            return query.filter(id=bundle.obj.id).exists()
        return False #bundle.obj.user == bundle.request.user

    def create_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def create_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no creates.")

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def update_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no updates.")

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


# API object to check selected objects and return invalid options
class DownloadCartObject(object):
    def __init__(self, projects=None, experiments=None, datasets=None,
                 datafiles=None, id=None):
        self.projects = projects
        self.experiments = experiments
        self.datasets = datasets
        self.datafiles = datafiles
        self.id = id


class RemoteHostAppResource(ModelResource):
    """Tastypie resource for RemoteHosts"""
    #hosts = fields.ApiField(attribute='hosts', null=True)

    class Meta:
        resource_name = 'remotehost'
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']
        serializer = default_serializer
        authentication = default_authentication
        authorization = GlobusAuthorization()
        object_class = RemoteHost
        always_return_data = True
        queryset = RemoteHost.objects.all()
        excludes = ['ip_address', 'managed', 'endpoint', 'users', 'groups', 'projects']
        filtering = {
            'id': ('exact', ),
            'name': ('exact', ),
        }
        ordering = [
            'id',
            'name'
        ]


def validate_objects(user, host, projects, experiments, datasets, datafiles):

    if not RemoteHost.objects.filter(pk=host).exists():
        raise ImmediateHttpResponse(HttpNotFound("Remote host does not exist"))

    host_query = RemoteHost.objects.select_related("users").filter(pk=host, users__id=user.id)
    users_groups = [*user.groups.all().values_list("id",flat=True)]
    host_query |= RemoteHost.objects.select_related("groups").filter(pk=host, groups__id__in=users_groups)

    if not host_query.exists():
        raise ImmediateHttpResponse(HttpForbidden("User does not have access to remote host"))

    # Query for related projects, and unpack into list here for efficiency
    related_projects = [*{*RemoteHost.objects.filter(id=host).prefetch_related('projects'
                            ).values_list("projects__id", flat=True)}]
    if projects:
        if Project.objects.filter(pk__in=projects).count() != len(projects):
            raise ImmediateHttpResponse(HttpNotFound("One or more Projects do not exist"))
        if Project.safe.all(user).filter(pk__in=projects).count() != len(projects):
            raise ImmediateHttpResponse(HttpForbidden("User does not have access to one or more Projects"))
        projects = [id for id in projects if id not in related_projects]
    if experiments:
        if Experiment.objects.filter(pk__in=experiments).count() != len(experiments):
            raise ImmediateHttpResponse(HttpNotFound("One or more Experiments do not exist"))
        if Experiment.safe.all(user).filter(pk__in=experiments).count() != len(experiments):
            raise ImmediateHttpResponse(HttpForbidden("User does not have access to one or more Experiments"))
        exp_projs = [*{*Experiment.objects.filter(pk__in=experiments).select_related(
                                  'project').values_list("id", "project__id")}]
        experiments = [id for (id, proj_id) in exp_projs if proj_id not in related_projects]
    if datasets:
        if Dataset.objects.filter(pk__in=datasets).count() != len(datasets):
            raise ImmediateHttpResponse(HttpNotFound("One or more Datasets do not exist"))
        if Dataset.safe.all(user).filter(pk__in=datasets).count() != len(datasets):
            raise ImmediateHttpResponse(HttpForbidden("User does not have access to one or more Datasets"))
        set_projs = [*{*Dataset.objects.filter(pk__in=datasets).prefetch_related(
                        "experiments", "experiments__project").values_list(
                        "id", "experiments__project__id")}]
        datasets = [id for (id, proj_id) in set_projs if proj_id not in related_projects]
    if datafiles:
        if DataFile.objects.filter(pk__in=datafiles).count() != len(datafiles):
            raise ImmediateHttpResponse(HttpNotFound("One or more Datafiles do not exist"))
        if DataFile.safe.all(user).filter(pk__in=datafiles).count() != len(datafiles):
            raise ImmediateHttpResponse(HttpForbidden("User does not have access to one or more Datafiles"))
        file_projs = [*{*DataFile.objects.filter(pk__in=datafiles).prefetch_related(
                        "dataset", "dataset__experiments", "dataset__experiments__project").values_list(
                        "id", "dataset__experiments__project__id")}]
        datafiles = [id for (id, proj_id) in file_projs if proj_id not in related_projects]
    return projects, experiments, datasets, datafiles


class ValidateAppResource(Resource):
    """Tastypie resource to validate Download Cart contents"""
    projects = fields.ApiField(attribute='projects', null=True)
    experiments = fields.ApiField(attribute='experiments', null=True)
    datasets = fields.ApiField(attribute='datasets', null=True)
    datafiles = fields.ApiField(attribute='datafiles', null=True)

    class Meta:
        resource_name = 'transfer_validate'
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        serializer = default_serializer
        authentication = default_authentication
        object_class = DownloadCartObject
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']
        return kwargs

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
            raise ImmediateHttpResponse(HttpUnauthorized("User must be logged in to validate download cart"))

        host_id = bundle.data.get('remote_host', None)
        proj_ids = bundle.data.get('projects', [])
        exp_ids = bundle.data.get('experiments', [])
        set_ids = bundle.data.get('datasets', [])
        file_ids = bundle.data.get('datafiles', [])
        if not host_id:
            raise ImmediateHttpResponse(HttpBadRequest("Please specify a remote host"))
        if not any([proj_ids, exp_ids, set_ids, file_ids]):
            raise ImmediateHttpResponse(HttpBadRequest("Please provide Projects/Experiments/Datasets/Datafiles for validation"))
        # Query for related projects, and unpack into list here for efficiency
        proj_bad, exp_bad, set_bad, file_bad = validate_objects(user, host_id, proj_ids, exp_ids, set_ids, file_ids)

        bundle.obj = DownloadCartObject(projects=proj_bad, experiments=exp_bad,
                                        datasets=set_bad, datafiles=file_bad, id=1)
        return bundle


class TransferAppResource(Resource):
    """Tastypie resource to submit transfer ready for Globus"""
    projects = fields.ApiField(attribute='projects', null=True)
    experiments = fields.ApiField(attribute='experiments', null=True)
    datasets = fields.ApiField(attribute='datasets', null=True)
    datafiles = fields.ApiField(attribute='datafiles', null=True)

    class Meta:
        resource_name = 'transfer'
        list_allowed_methods = ['post']
        detail_allowed_methods = ['post']
        serializer = default_serializer
        authentication = default_authentication
        object_class = DownloadCartObject
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']
        return kwargs

    def get_object_list(self, request):
        return request

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        bundle = self.create_transfer(bundle)
        return bundle


    def create_transfer(self, bundle):
        user = bundle.request.user
        if not user.is_authenticated:
            raise ImmediateHttpResponse(HttpUnauthorized("User must be logged in to submit Globus transfer"))

        host_id = bundle.data.get('remote_host', None)
        proj_ids = bundle.data.get('projects', [])
        exp_ids = bundle.data.get('experiments', [])
        set_ids = bundle.data.get('datasets', [])
        file_ids = bundle.data.get('datafiles', [])
        if not host_id:
            raise ImmediateHttpResponse(HttpBadRequest("Please specify a remote host"))
        if not any([proj_ids, exp_ids, set_ids, file_ids]):
            raise ImmediateHttpResponse(HttpBadRequest("Please provide Projects/Experiments/Datasets/Datafiles for validation"))

        proj_bad, exp_bad, set_bad, file_bad = validate_objects(user, host_id, proj_ids, exp_ids, set_ids, file_ids)

        if any([proj_bad, exp_bad, set_bad, file_bad]):
            raise ImmediateHttpResponse(HttpForbidden("One or more objects could not be transferred to specified remote host"))

        query = DataFile.objects.none()

        for proj in proj_ids:
            if not authz.has_download_access(bundle.request, proj, "project"):
                raise ImmediateHttpResponse(HttpForbidden("You do not have download access for one or more projects"))
            query |= Project.objects.get(pk=proj).get_datafiles(user, downloadable=True)
        for exp in exp_ids:
            if not authz.has_download_access(bundle.request, exp, "experiment"):
                raise ImmediateHttpResponse(HttpForbidden("You do not have download access for one or more experiments"))
            query |= Experiment.objects.get(pk=exp).get_datafiles(user, downloadable=True)
        for set in set_ids:
            if not authz.has_download_access(bundle.request, set, "dataset"):
                raise ImmediateHttpResponse(HttpForbidden("You do not have download access for one or more datasets"))
            query |= Dataset.objects.get(pk=set).get_datafiles(user)
        for file in file_ids:
            if not authz.has_download_access(bundle.request, file, "datafile"):
                raise ImmediateHttpResponse(HttpForbidden("You do not have download access for one or more datafiles"))
        query |= DataFile.safe.all(user).filter(pk__in=file_ids)

        downloadable_dfs = query.distinct().values_list("id", flat=True)

        remote_vm = RemoteHost.objects.get(pk=host_id)

        with transaction.atomic():
            newtransferlog = TransferLog.objects.create(
                initiated_by = user,
                remote_host = remote_vm,
                status = TransferLog.STATUS_NEW)
            newtransferlog.save()
            newtransferlog.datafiles.add(*downloadable_dfs)
            newtransferlog.save()

        bundle.obj = DownloadCartObject(projects=proj_bad, experiments=exp_bad,
                                        datasets=set_bad, datafiles=file_bad, id=1)
        return bundle
