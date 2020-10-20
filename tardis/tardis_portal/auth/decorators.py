# -*- coding: utf-8 -*-
#
# Copyright (c) 2010-2011, Monash e-Research Centre
#   (Monash University, Australia)
# Copyright (c) 2010-2011, VeRSI Consortium
#   (Victorian eResearch Strategic Initiative, Australia)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    *  Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    *  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#    *  Neither the name of the VeRSI, the VeRSI Consortium members, nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# pylint: disable=R1702

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpRequest
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.conf import settings

from ..models import Project, Experiment, Dataset, DataFile, GroupAdmin, \
    ProjectParameter, ExperimentParameter, DatasetParameter, \
    DatafileParameter, ObjectACL
from ..shortcuts import return_response_error
from .localdb_auth import django_user, django_group


def bulk_replace_existing_acls(some_request, admin_flag=False):
    # 1) To work on users(groups), supply users(groups) key in request_dict
    # 2) lead_researchers/created_by users are treated as immutable by this function
    # 3) "admins"(users/groups with isOwner permission), are treated as immutable
    #    unless admin_flag is True
    # 4) Empty lists will delete all old acls (obeying immutability)

    # --- Issues ---
    # 1) this should probably go elsewhere
    # 2) this is pretty inefficient with its database queries
    # 3) should probably be refactored to separate users/groups out a bit more
    #    efficiently than the current "if" statements
    """ assume some default structure
        [
            {
            "content_type": "project",  "data file"
            "id": 1,
            "users": [
                        {"id": str(1),
                         "canRead":False,
                         "canWrite":False,
                         "canDownload":False,
                         "canSensitive":False,
                         "canDelete":False,
                         "isOwner":False}
                     ],
            "groups": [
                        {"id": str(1),
                         "canRead":False,
                         "canWrite":False,
                         "canDownload":False,
                         "canSensitive":False,
                         "canDelete":False,
                         "isOwner":False}
                     ]
            }
        ]
    """

    # used for heirarchical look up of lead_researcher/creator, in order to
    # preserve their ACLs from being edited
    createdby_lead_dict = {"project": ["created_by__id","lead_researcher__id"],
                           "experiment": ["created_by__id", "project__created_by__id",
                                          "project__lead_researcher__id"],
                           "dataset": ["experiments__created_by__id",
                                       "experiments__project__created_by__id",
                                       "experiments__project__lead_researcher__id"],
                           "data file": ["dataset__experiments__created_by__id",
                                         "dataset__experiments__project__created_by__id",
                                         "dataset__experiments__project__lead_researcher__id"]}

    for new_acls in some_request:
        # Collect either admin(isOwner) or non-admin users/groups
        if not admin_flag:
            old_acls = ObjectACL.objects.filter(
                object_id=new_acls["id"],
                content_type=new_acls["content_type"],
                aclOwnershipType=ObjectACL.OWNER_OWNED,
                isOwner=False)
        else:
            old_acls = ObjectACL.objects.filter(
                object_id=new_acls["id"],
                content_type=new_acls["content_type"],
                aclOwnershipType=ObjectACL.OWNER_OWNED,
                isOwner=True)
        #Used to filter out any duplicate ACLs
        modified_user_acls = []
        modified_group_acls = []

        for old_acl in old_acls:

            if old_acl.pluginId == "django_user":
                if "users" in new_acls.keys():
                    # If old ACL user_entity is a project_lead or creator (created_by)
                    # for any (parent) projects or experiments, then we do not wish to
                    # change their permissions in any way, so we skip this old ACL
                    if new_acls["content_type"] == 'project':
                        protected_users = list(Project.objects.get(id=new_acls["id"]
                                               ).values(*createdby_lead_dict[new_acls["content_type"]]).distinct())
                    if new_acls["content_type"] == 'experiment':
                        protected_users = list(Experiment.objects.get(id=new_acls["id"]
                                               ).values(*createdby_lead_dict[new_acls["content_type"]]).distinct())
                    if new_acls["content_type"] == 'dataset':
                        protected_users = list(Dataset.objects.get(id=new_acls["id"]
                                               ).values(*createdby_lead_dict[new_acls["content_type"]]).distinct())
                    if new_acls["content_type"] == 'data file':
                        protected_users = list(DataFile.objects.get(id=new_acls["id"]
                                               ).values(*createdby_lead_dict[new_acls["content_type"]]).distinct())
                    protected_users = [str(id) for id in user_id_dict.values() for user_id_dict in protected_users]
                    if old_acl.entityId in protected_users:
                        continue
                    # If requested list is empty: delete old ACLs
                    if not new_acls["users"]:
                        old_acl.delete()
                        continue
                    # If old ACL user is not in new list of users, delete ACL
                    if old_acl.entityId not in [d['id'] for d in new_acls["users"]]:
                        old_acl.delete()
                    else:
                        # If this ACL is a duplicate, delete it
                        if old_acl.entityId in [d.entityId for d in modified_user_acls]:
                            old_acl.delete()
                        else:
                            # If user already has permissions, update old ACL
                            # according to new permissions
                            matched_idx = [d['id'] for d in new_acls["users"]].index(
                                old_acl.entityId)
                            old_acl.canRead = new_acls["users"][matched_idx]["canRead"]
                            old_acl.canDownload = new_acls["users"][matched_idx]["canDownload"]
                            old_acl.canWrite = new_acls["users"][matched_idx]["canWrite"]
                            old_acl.canSensitive = new_acls["users"][matched_idx]["canSensitive"]
                            old_acl.canDelete = new_acls["users"][matched_idx]["canDelete"]
                            old_acl.isOwner = new_acls["users"][matched_idx]["isOwner"]
                            old_acl.save()
                            # Add old ACL to "processed" list, in order to delete
                            # any further duplicate entries of it in the database
                            modified_user_acls.append(old_acl)

            if old_acl.pluginId == "django_group":
                if "groups" in new_acls.keys():
                    # If requested list is empty: delete old ACLs
                    if not new_acls["groups"]:
                        old_acl.delete()
                        continue
                    # If old ACL group is not in new list of groups, delete ACL
                    if old_acl.entityId not in [d['id'] for d in new_acls["groups"]]:
                        old_acl.delete()
                    else:
                        # If this ACL is a duplicate, delete it
                        if old_acl.entityId in [d.entityId for d in modified_group_acls]:
                            old_acl.delete()
                        else:
                            # If group already has permissions, update old ACL
                            # according to new permissions
                            matched_idx = [d['id'] for d in new_acls["groups"]].index(
                                old_acl.entityId)
                            old_acl.canRead = new_acls["groups"][matched_idx]["canRead"]
                            old_acl.canDownload = new_acls["groups"][matched_idx]["canDownload"]
                            old_acl.canWrite = new_acls["groups"][matched_idx]["canWrite"]
                            old_acl.canSensitive = new_acls["groups"][matched_idx]["canSensitive"]
                            old_acl.canDelete = new_acls["groups"][matched_idx]["canDelete"]
                            old_acl.isOwner = new_acls["groups"][matched_idx]["isOwner"]
                            old_acl.save()
                            # Add old ACL to "processed" list, in order to delete
                            # any further duplicate entries of it in the database
                            modified_group_acls.append(old_acl)

        if "users" in new_acls.keys():
            # likely inefficient to partially "duplicate" the first query,
            # but convenient flat list of IDs
            old_acls_user_ids = ObjectACL.objects.filter(
                pluginId=django_user,
                object_id=new_acls["id"],
                content_type=new_acls["content_type"],
                aclOwnershipType=ObjectACL.OWNER_OWNED).values_list('entityId', flat=True)

            if new_acls["users"]:
                for new_acl in new_acls["users"]:
                    # if user doesn't already have an ACL for this object, create one
                    if new_acl["id"] not in old_acls_user_ids:
                        acl = ObjectACL(content_type=new_acls["content_type"],
                                        object_id=new_acls["id"],
                                        pluginId=django_user,
                                        entityId=str(new_acl["id"]),
                                        canRead=new_acl["canRead"],
                                        canDownload=new_acl["canDownload"],
                                        canWrite=new_acl["canWrite"],
                                        canDelete=new_acl["canDelete"],
                                        canSensitive=new_acl["canSensitive"],
                                        isOwner=new_acl["isOwner"],
                                        aclOwnershipType=ObjectACL.OWNER_OWNED)
                        acl.save()

        if "groups" in new_acls.keys():
            # likely inefficient to partially "duplicate" the first query,
            # but convenient flat list of IDs
            old_acls_group_ids = ObjectACL.objects.filter(
                pluginId=django_group,
                object_id=new_acls["id"],
                content_type=new_acls["content_type"],
                aclOwnershipType=ObjectACL.OWNER_OWNED).values_list('entityId', flat=True)

            if new_acls["groups"]:
                for new_acl in new_acls["groups"]:
                    # if group doesn't already have an ACL for this object, create one
                    if new_acl["id"] not in old_acls_group_ids:
                        acl = ObjectACL(content_type=new_acls["content_type"],
                                        object_id=new_acls["id"],
                                        pluginId=django_group,
                                        entityId=str(new_acl["id"]),
                                        canRead=new_acl["canRead"],
                                        canDownload=new_acl["canDownload"],
                                        canWrite=new_acl["canWrite"],
                                        canDelete=new_acl["canDelete"],
                                        canSensitive=new_acl["canSensitive"],
                                        isOwner=new_acl["isOwner"],
                                        aclOwnershipType=ObjectACL.OWNER_OWNED)
                        acl.save()


def get_accessible_experiments(request):
    return Experiment.safe.all(request.user)


def get_accessible_experiments_for_dataset(request, dataset_id):
    experiments = Experiment.safe.all(request.user)
    return experiments.filter(datasets__id=dataset_id)


def get_shared_experiments(request):
    experiments = Experiment.safe.owned_and_shared(request.user)
    # exclude owned experiments
    owned = get_owned_experiments(request)
    experiments = experiments.exclude(id__in=[o.id for o in owned])
    return experiments


def get_owned_experiments(request):
    return Experiment.safe.owned(request.user)


def get_accessible_datafiles_for_user(request):
    experiments = get_accessible_experiments(request)
    if experiments.count() == 0:
        return DataFile.objects.none()
    queries = [Q(dataset__experiments__id=e.id) for e in experiments]
    query = queries.pop()
    for item in queries:
        query |= item
    return DataFile.safe.all(request.user).filter(query)


def get_obj_parameter(pn_id, obj_id, ct_type):
    if ct_type == "project":
        return ProjectParameter.objects.get(name__id=pn_id,
                                            parameterset__project__id=obj_id)
    if ct_type == "experiment":
        return ExperimentParameter.objects.get(name__id=pn_id,
                                               parameterset__experiment__id=obj_id)
    if ct_type == "dataset":
        return DatasetParameter.objects.get(name__id=pn_id,
                                            parameterset__dataset__id=obj_id)
    if ct_type == "datafile":
        return DatafileParameter.objects.get(name__id=pn_id,
                                             parameterset__datafile__id=obj_id)
    return None


def has_ownership(request, obj_id, ct_type):
    if ct_type == 'project':
        return Project.safe.owned(request.user).filter(pk=obj_id).exists()
    if ct_type == 'experiment':
        return Experiment.safe.owned(request.user).filter(pk=obj_id).exists()
    if ct_type == 'dataset':
        return Dataset.safe.owned(request.user).filter(pk=obj_id).exists()
    if ct_type == 'datafile':
        return DataFile.safe.owned(request.user).filter(pk=obj_id).exists()
    return None


def has_access(request, obj_id, ct_type):
    try:
        if ct_type == 'project':
            obj = Project.objects.get(id=obj_id)
        if ct_type == 'experiment':
            obj = Experiment.objects.get(id=obj_id)
        if ct_type == 'dataset':
            obj = Dataset.objects.get(id=obj_id)
        if ct_type == 'datafile':
            obj = DataFile.objects.get(id=obj_id)
    except (Project.DoesNotExist, Experiment.DoesNotExist,
            Dataset.DoesNotExist, DataFile.DoesNotExist):
        return False
    return request.user.has_perm('tardis_acls.view_'+ct_type, obj)


def has_write(request, obj_id, ct_type):
    if ct_type == 'project':
        obj = Project.objects.get(id=obj_id)
        if obj.locked:
            return False
    if ct_type == 'experiment':
        obj = Experiment.objects.get(id=obj_id)
        if obj.locked:
            return False
    if ct_type == 'dataset':
        obj = Dataset.objects.get(id=obj_id)
        if obj.immutable:
            return False
    if ct_type == 'datafile':
        obj = DataFile.objects.get(id=obj_id)
    return request.user.has_perm('tardis_acls.change_'+ct_type, obj)


def has_download_access(request, obj_id, ct_type):
    if ct_type == 'project':
        obj = Project.objects.get(id=obj_id)
    if ct_type == 'experiment':
        obj = Experiment.objects.get(id=obj_id)
    if ct_type == 'dataset':
        obj = Dataset.objects.get(id=obj_id)
    if ct_type == 'datafile':
        obj = DataFile.objects.get(id=obj_id)
    return request.user.has_perm('tardis_acls.download_'+ct_type, obj)


def has_sensitive_access(request, obj_id, ct_type):
    if ct_type == 'project':
        obj = Project.objects.get(id=obj_id)
    if ct_type == 'experiment':
        obj = Experiment.objects.get(id=obj_id)
    if ct_type == 'dataset':
        obj = Dataset.objects.get(id=obj_id)
    if ct_type == 'datafile':
        obj = DataFile.objects.get(id=obj_id)
    return request.user.has_perm('tardis_acls.sensitive_'+ct_type, obj)


def has_read_or_owner_ACL(request, obj_id, ct_type):
    """
    Check whether the user has read access to the proj/exp/set/file -
    this means either
    they have been granted read access, or that they are the owner.

    NOTE:
    This does not check whether the proj/exp/set/file is public or not, which means
    even when the proj/exp/set/file is public, this method does not automatically
    returns true.

    As such, this method should NOT be used to check whether the user has
    general read permission.
    """
    from datetime import datetime
    from .localdb_auth import django_user

    if ct_type == 'project':
        obj = Project.safe.get(request.user, obj_id)
    if ct_type == 'experiment':
        obj = Experiment.safe.get(request.user, obj_id)
    if ct_type == 'dataset':
        obj = Dataset.safe.get(request.user, obj_id)
    if ct_type == 'datafile':
        obj = DataFile.safe.get(request.user, obj_id)

    # does the user own this experiment
    query = Q(content_type=obj.get_ct(),
              object_id=obj.id,
              pluginId=django_user,
              entityId=str(request.user.id),
              isOwner=True)

    # check if there is a user based authorisation role
    query |= Q(content_type=obj.get_ct(),
               object_id=obj.id,
               pluginId=django_user,
               entityId=str(request.user.id),
               canRead=True)\
        & (Q(effectiveDate__lte=datetime.today())
           | Q(effectiveDate__isnull=True))\
        & (Q(expiryDate__gte=datetime.today())
           | Q(expiryDate__isnull=True))

    # and finally check all the group based authorisation roles
    for name, group in request.user.userprofile.ext_groups:
        query |= Q(pluginId=name,
                   entityId=str(group),
                   content_type=obj.get_ct(),
                   object_id=obj.id,
                   canRead=True)\
            & (Q(effectiveDate__lte=datetime.today())
               | Q(effectiveDate__isnull=True))\
            & (Q(expiryDate__gte=datetime.today())
               | Q(expiryDate__isnull=True))

    # is there at least one ACL rule which satisfies the rules?
    from ..models.access_control import ObjectACL
    acl = ObjectACL.objects.filter(query)
    return bool(acl)


# MIKEACL: REFACTOR for future proj/set/file delete options?
def has_delete_permissions(request, experiment_id):
    experiment = Experiment.safe.get(request.user, experiment_id)
    return request.user.has_perm('tardis_acls.delete_experiment', experiment)


@login_required
def is_group_admin(request, group_id):
    user_check = GroupAdmin.objects.filter(user=request.user,
                                           group__id=group_id).exists()
    admin_user_check = GroupAdmin.objects.filter(admin_users__id=request.user.id,
                                                group__id=group_id).exists()
    admin_group_check = any([GroupAdmin.objects.filter(admin_groups__id=group.id,
            group__id=group_id).exists() for group in request.user.groups.all()])
    return any([user_check, admin_user_check, admin_group_check])

def group_ownership_required(f):
    """
    A decorator for Django views that validates if a user is a group admin
    or 'superuser' prior to further processing the request.
    Unauthenticated requests are redirected to the login page. If the
    user making the request satisfies none of these criteria, an error response
    is returned.

    :param f: A Django view function
    :type f: types.FunctionType
    :return: A Django view function
    :rtype: types.FunctionType
    """
    def wrap(request, *args, **kwargs):
        user = request.user
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login?next=%s' % request.path)
        if not (is_group_admin(request, kwargs['group_id']) or
                user.is_superuser):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def experiment_ownership_required(f):
    """
    A decorator for Django views that validates if a user is an owner of an
    experiment or 'superuser' prior to further processing the request.
    Unauthenticated requests are redirected to the login page. If the
    user making the request satisfies none of these criteria, an error response
    is returned.

    :param f: A Django view function
    :type f: types.FunctionType
    :return: A Django view function
    :rtype: types.FunctionType
    """
    def wrap(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect('/login?next=%s' % request.path)
        if not (has_ownership(request, kwargs['experiment_id'], 'experiment')
                or user.is_superuser):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def experiment_access_required(f):

    def wrap(*args, **kwargs):
        # We find the request as either the first or second argument.
        # This is so it can be used for the 'get' method on class-based
        # views (where the first argument is 'self') and also with traditional
        # view functions (where the first argument is the request).
        # TODO: An alternative would be to create a mixin for the ExperimentView
        #       and similar classes, like AccessRequiredMixin
        request = args[0]
        if not isinstance(request, HttpRequest):
            request = args[1]

        if not has_access(request, kwargs['experiment_id'], "experiment"):
            return return_response_error(request)
        return f(*args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def experiment_download_required(f):

    def wrap(request, *args, **kwargs):
        if not has_download_access(
                request, kwargs['experiment_id'], "experiment"):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def dataset_download_required(f):

    def wrap(request, *args, **kwargs):
        if not has_download_access(request, kwargs['dataset_id'], "dataset"):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def dataset_access_required(f):

    def wrap(*args, **kwargs):
        # We find the request as either the first or second argument.
        # This is so it can be used for the 'get' method on class-based
        # views (where the first argument is 'self') and also with traditional
        # view functions (where the first argument is the request).
        # TODO: An alternative would be to create a mixin for the DatasetView
        #       and similar classes, like AccessRequiredMixin
        request = args[0]
        if not isinstance(request, HttpRequest):
            request = args[1]

        if not has_access(request, kwargs['dataset_id'], "dataset"):
            return return_response_error(request)
        return f(*args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def datafile_access_required(f):

    def wrap(request, *args, **kwargs):

        if not has_access(request, kwargs['datafile_id'], "datafile"):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def write_permissions_required(f):

    def wrap(request, *args, **kwargs):

        if not has_write(request, kwargs['experiment_id'], "experiment"):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def dataset_write_permissions_required(f):
    def wrap(request, *args, **kwargs):
        dataset_id = kwargs['dataset_id']
        if not has_write(request, dataset_id, "dataset"):
            if request.is_ajax():
                return HttpResponse("")
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def delete_permissions_required(f):

    def wrap(request, *args, **kwargs):

        if not has_delete_permissions(request, kwargs['experiment_id']):
            return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def upload_auth(f):
    def wrap(request, *args, **kwargs):
        from django.utils import timezone
        session_id = request.POST.get('session_id',
                                      request.COOKIES.get(
                                          settings.SESSION_COOKIE_NAME,
                                          None))
        sessions = Session.objects.filter(pk=session_id)
        if sessions and sessions[0].expire_date > timezone.now():
            try:
                request.user = User.objects.get(
                    pk=sessions[0].get_decoded()['_auth_user_id'])
            except:
                if request.is_ajax():
                    return HttpResponse("")
                return return_response_error(request)
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap
