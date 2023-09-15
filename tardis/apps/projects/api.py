"""
RESTful API for MyTardis models and data.
Implemented with Tastypie.

.. moduleauthor:: Mike Laverick <mike.laverick@auckland.ac.nz>
.. moduleauthor:: Chris Seal <c.seal@auckland.ac.nz>
"""

from itertools import chain

from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import re_path

import ldap3
from ldap3.utils.conv import escape_filter_chars
from ldap3.utils.dn import escape_rdn
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.constants import ALL_WITH_RELATIONS
from tastypie.exceptions import NotFound, Unauthorized
from tastypie.resources import ModelResource
from tastypie.serializers import Serializer
from tastypie.utils import trailing_slash

from tardis.apps.dataclassification.models import (
    DATA_CLASSIFICATION_INTERNAL,
    DATA_CLASSIFICATION_PUBLIC,
    DATA_CLASSIFICATION_SENSITIVE,
    ProjectDataClassification,
)
from tardis.apps.identifiers.models import InstitutionID, ProjectID
from tardis.tardis_portal.api import (
    ExperimentResource,
    MyTardisAuthentication,
    ParameterResource,
    ParameterSetResource,
    PrettyJSONSerializer,
    UserResource,
)
from tardis.tardis_portal.auth.decorators import (
    has_access,
    has_sensitive_access,
    has_write,
)
from tardis.tardis_portal.models.access_control import UserAuthentication

from .models import (
    Institution,
    Project,
    ProjectACL,
    ProjectParameter,
    ProjectParameterSet,
)

default_serializer = PrettyJSONSerializer() if settings.DEBUG else Serializer()
PROJECT_INSTITUTION_RESOURCE = "tardis.apps.projects.api.Institution"


def classification_to_string(classification: int) -> str:
    """Helper function to turn the classification into a String

    Note: Relies on the order of operations in order to distinguish between
    PUBLIC and INTERNAL. Any PUBLIC data should have been filtered out prior to
    testing the INTERNAL classification, which simplifies the function."""
    if classification < DATA_CLASSIFICATION_SENSITIVE:
        return "Restricted"
    if classification >= DATA_CLASSIFICATION_PUBLIC:
        return "Public"
    if classification >= DATA_CLASSIFICATION_INTERNAL:
        return "Internal"
    return "Sensitive"


def get_user_from_upi(upi):
    upi = escape_rdn(upi)
    server = ldap3.Server(settings.LDAP_URL)
    search_filter = f"({settings.LDAP_USER_LOGIN_ATTR}={upi})"
    with ldap3.Connection(
        server,
        user=settings.LDAP_ADMIN_USER,
        password=settings.LDAP_ADMIN_PASSWORD,
    ) as connection:
        connection.bind()
        connection.search(
            settings.LDAP_USER_BASE,
            escape_filter_chars(search_filter),
            attributes=["*"],
        )
        if len(connection.entries) > 1:
            error_message = (
                "More than one person with {}: {} has been found in the LDAP".format(
                    settings.LDAP_USER_LOGIN_ATTR, upi
                )
            )
            # if logger:
            #    logger.error(error_message)
            raise ValueError(error_message)
        if len(connection.entries) == 0:
            error_message = "No one with {}: {} has been found in the LDAP".format(
                settings.LDAP_USER_LOGIN_ATTR, upi
            )
            # if logger:
            #    logger.warning(error_message)
            return None
        person = connection.entries[0]
        first_name_key = "givenName"
        last_name_key = "sn"
        email_key = "mail"
        username = person[settings.LDAP_USER_LOGIN_ATTR].value
        first_name = person[first_name_key].value
        last_name = person[last_name_key].value
        try:
            email = person[email_key].value
        except KeyError:
            email = ""
        details = {
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
        return details


def gen_random_password():
    import random

    random.seed()
    characters = "abcdefghijklmnopqrstuvwxyzABCDFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
    passlen = 16
    password = "".join(random.sample(characters, passlen))
    return password


def get_or_create_user(username):
    if not User.objects.filter(username=username).exists():
        new_user = get_user_from_upi(username)
        user = User.objects.create(
            username=new_user["username"],
            first_name=new_user["first_name"],
            last_name=new_user["last_name"],
            email=new_user["email"],
        )
        user.set_password(gen_random_password())
        user.save()
        authentication = UserAuthentication(
            userProfile=user.userprofile,
            username=new_user["username"],
            authenticationMethod=settings.LDAP_METHOD,
        )
        authentication.save()
        for permission in settings.DEFAULT_PERMISSIONS:
            user.permissions.add(Permission.objects.get(codename=permission))
    else:
        user = User.objects.get(username=username)
    return user


class ProjectACLAuthorization(Authorization):
    """A Project-specific Authorisation class for Tastypie, rather than bloating
    the existing generic MyTardis-API ACLAuthorization class further. It would be
    good to refactor the generic API ACLAuthorization class to be even more generic:
    reducing verboseness of the class and removing this specific project ACLAuth class.
    """

    def read_list(self, object_list, bundle):  # noqa # too complex
        if bundle.request.user.is_authenticated and bundle.request.user.is_superuser:
            return object_list
        if isinstance(bundle.obj, Project):
            project_ids = [
                proj.id
                for proj in object_list
                if has_access(bundle.request, proj.id, "project")
            ]
            return Project.objects.filter(id__in=project_ids)
        if isinstance(bundle.obj, ProjectParameterSet):
            return [
                pps
                for pps in object_list
                if has_access(bundle.request, pps.project.id, "project")
            ]
        if isinstance(bundle.obj, ProjectParameter):
            pp_list = [
                pp
                for pp in object_list
                if has_access(bundle.request, pp.parameterset.project.id, "project")
            ]

            # Generator to filter sensitive exp_parameters when given an exp id
            def get_set_param(set_par):
                if not set_par.name.sensitive:
                    yield set_par
                elif has_sensitive_access(
                    bundle.request, set_par.parameterset.project.id, "project"
                ):
                    yield set_par

            # Take chained generators and turn them into a set of parameters
            return list(chain(chain.from_iterable(map(get_set_param, pp_list))))

        if isinstance(bundle.obj, ProjectACL):
            query = ProjectACL.objects.none()
            if bundle.request.user.is_authenticated:
                query |= bundle.request.user.projectacls.all()
                for group in bundle.request.user.groups.all():
                    query |= group.projectacls.all()
            return query
        return []

    def read_detail(self, object_list, bundle):  # noqa # too complex
        if bundle.request.user.is_authenticated and bundle.request.user.is_superuser:
            return True
        if isinstance(bundle.obj, Project):
            return has_access(bundle.request, bundle.obj.id, "project")
        if isinstance(bundle.obj, ProjectParameterSet):
            return has_access(bundle.request, bundle.obj.project.id, "project")
        if isinstance(bundle.obj, ProjectParameter):
            if bundle.obj.name.sensitive:
                return has_sensitive_access(
                    bundle.request, bundle.obj.parameterset.project.id, "project"
                )
            return has_access(
                bundle.request, bundle.obj.parameterset.project.id, "project"
            )
        raise NotImplementedError(type(bundle.obj))

    def create_list(self, object_list, bundle):
        raise NotImplementedError(type(bundle.obj))

    def create_detail(self, object_list, bundle):  # noqa # too complex
        if not bundle.request.user.is_authenticated:
            return False
        if bundle.request.user.is_superuser:
            return True

        if isinstance(bundle.obj, Project):
            if not bundle.request.user.has_perm("projects.change_project"):
                return False
            perm = False
            if settings.ONLY_EXPERIMENT_ACLS:
                for exp_uri in bundle.data.get("experiments", []):
                    try:
                        this_exp = ExperimentResource.get_via_uri(
                            ExperimentResource(), exp_uri, bundle.request
                        )
                    except Exception:
                        return False
                    if has_write(bundle.request, this_exp.id, "experiment"):
                        perm = True
                    else:
                        return False
            else:
                perm = True
            return perm
        if isinstance(bundle.obj, ProjectParameterSet):
            if not bundle.request.user.has_perm("projects.change_project"):
                return False
            project_uri = bundle.data.get("project", None)
            if project_uri is not None:
                project = ProjectResource.get_via_uri(
                    ProjectResource(), project_uri, bundle.request
                )
                return has_write(bundle.request, project.id, "project")
            if getattr(bundle.obj.project, "id", False):
                return has_write(bundle.request, bundle.obj.project.id, "project")
            return False
        if isinstance(bundle.obj, ProjectParameter):
            return bundle.request.user.has_perm(
                "projects.change_project"
            ) and has_write(
                bundle.request, bundle.obj.parameterset.project.id, "project"
            )
        if isinstance(bundle.obj, ProjectACL):
            return bundle.request.user.has_perm("projects.add_projectacl")
        raise NotImplementedError(type(bundle.obj))

    def update_list(self, object_list, bundle):
        raise NotImplementedError(type(bundle.obj))

    def update_detail(self, object_list, bundle):  # noqa # too complex
        """
        Latest TastyPie requires update_detail permissions to be able to create
        objects.  Rather than duplicating code here, we'll just use the same
        authorization rules we use for create_detail.
        """
        return self.create_detail(object_list, bundle)

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")


class InstitutionResource(ModelResource):
    """Tastypie class for accessing Instituions"""

    instituitionid = None
    identifiers = fields.ListField(null=True, blank=True)

    # Custom filter for identifiers module based on code example from
    # https://stackoverflow.com/questions/10021749/ \
    # django-tastypie-advanced-filtering-how-to-do-complex-lookups-with-q-objects

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}
        orm_filters = super().build_filters(filters)

        if "tardis.apps.identifiers" in settings.INSTALLED_APPS and (
            "institution" in settings.OBJECTS_WITH_IDENTIFIERS
            and "identifier" in filters
        ):
            query = filters["identifier"]
            qset = Q(identifiers__identifier__iexact=query)
            orm_filters.update({"identifier": qset})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        if "tardis.apps.identifiers" in settings.INSTALLED_APPS:
            if (
                "institution" in settings.OBJECTS_WITH_IDENTIFIERS
                and "identifier" in applicable_filters
            ):
                custom = applicable_filters.pop("identifier")
            else:
                custom = None
        else:
            custom = None

        semi_filtered = super().apply_filters(request, applicable_filters)

        return semi_filtered.filter(custom) if custom else semi_filtered

    # End of custom filter code

    class Meta:
        authentication = MyTardisAuthentication()
        authorization = ProjectACLAuthorization()
        allowed_methods = ["get"]
        serializer = default_serializer
        object_class = Institution
        queryset = Institution.objects.all()
        filtering = {
            "id": ("exact",),
            "name": ("exact",),
        }
        ordering = ["id", "name"]
        always_return_data = True

    def dehydrate(self, bundle):
        if (
            "tardis.apps.identifiers" in settings.INSTALLED_APPS
            and "institution" in settings.OBJECTS_WITH_IDENTIFIERS
        ):
            bundle.data["identifiers"] = list(
                map(str, InstitutionID.objects.filter(institution=bundle.obj))
            )
            if bundle.data["identifiers"] == []:
                bundle.data.pop("identifiers")
        return bundle


class ProjectResource(ModelResource):
    """API for Projects
    also creates a default ACL and allows ProjectParameterSets to be read
    and written.
    TODO: catch duplicate schema submissions for parameter sets
    """

    identifiers = fields.ListField(null=True, blank=True)
    created_by = fields.ForeignKey(UserResource, "created_by")
    parameter_sets = fields.ToManyField(
        "tardis.apps.projects.api.ProjectParameterSetResource",
        "projectparameterset_set",
        related_name="project",
        full=True,
        null=True,
    )
    institution = fields.ToManyField(
        InstitutionResource, "institution", related_name="projects"
    )
    principal_investigator = fields.ForeignKey(UserResource, "principal_investigator")
    tags = fields.ListField()

    # Custom filter for identifiers module based on code example from
    # https://stackoverflow.com/questions/10021749/ \
    # django-tastypie-advanced-filtering-how-to-do-complex-lookups-with-q-objects

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}
        orm_filters = super().build_filters(filters)

        if "tardis.apps.identifiers" in settings.INSTALLED_APPS and (
            "project" in settings.OBJECTS_WITH_IDENTIFIERS and "identifier" in filters
        ):
            query = filters["identifier"]
            qset = Q(identifiers__identifier__iexact=query)
            orm_filters.update({"identifier": qset})
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        custom = None
        if "tardis.apps.identifiers" in settings.INSTALLED_APPS and (
            "project" in settings.OBJECTS_WITH_IDENTIFIERS
            and "identifier" in applicable_filters
        ):
            custom = applicable_filters.pop("identifier")
        semi_filtered = super().apply_filters(request, applicable_filters)
        return semi_filtered.filter(custom) if custom else semi_filtered

    # End of custom filter code

    def dehydrate_tags(self, bundle):
        return list(map(str, bundle.obj.tags.all()))

    def save_m2m(self, bundle):
        tags = bundle.data.get("tags", [])
        bundle.obj.tags.set(*tags)
        return super().save_m2m(bundle)

    class Meta:
        authentication = MyTardisAuthentication()
        authorization = ProjectACLAuthorization()
        serializer = default_serializer
        object_class = Project
        queryset = Project.objects.all()
        filtering = {
            "id": ("exact",),
            "name": ("exact",),
            "url": ("exact",),
            "institution": ALL_WITH_RELATIONS,
        }
        if (
            "tardis.apps.identifiers" in settings.INSTALLED_APPS
            and "project" in settings.OBJECTS_WITH_IDENTIFIERS
        ):
            filtering.update({"pids": ["pids"]})
        ordering = ["id", "name", "url", "start_time", "end_time"]
        always_return_data = True

    def dehydrate(self, bundle):
        from tardis.tardis_portal.models import Experiment

        project = bundle.obj
        size = project.get_size(bundle.request.user)
        bundle.data["size"] = size
        # Both Macro and Micro ACLs route through ExperimentACLs for this
        project_experiment_count = (
            Experiment.safe.all(user=bundle.request.user)
            .filter(projects=project)
            .count()
        )
        bundle.data["experiment_count"] = project_experiment_count
        project_dataset_count = project.get_datasets(bundle.request.user).count()
        bundle.data["dataset_count"] = project_dataset_count
        project_datafile_count = project.get_datafiles(bundle.request.user).count()
        bundle.data["datafile_count"] = project_datafile_count
        if (
            "tardis.apps.identifiers" in settings.INSTALLED_APPS
            and "project" in settings.OBJECTS_WITH_IDENTIFIERS
        ):
            bundle.data["identifiers"] = list(
                map(str, ProjectID.objects.filter(project=bundle.obj))
            )
            if bundle.data["identifiers"] == []:
                bundle.data.pop("identifiers")
        if "tardis.apps.dataclassification" in settings.INSTALLED_APPS:
            bundle.data["classification"] = classification_to_string(
                bundle.obj.dataclassification.classification
            )
        # admins = project.get_admins()
        # bundle.data["admin_groups"] = [acl.id for acl in admins]
        # members = project.get_groups()
        # bundle.data["member_groups"] = [acl.id for acl in members]
        return bundle

    def prepend_urls(self):
        return [
            re_path(
                r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/project-experiments%s$"
                % (self._meta.resource_name, trailing_slash()),
                self.wrap_view("get_project_experiments"),
                name="api_get_project_experiments",
            ),
        ]

    def hydrate_m2m(self, bundle):
        """
        Create project-experiment associations first, in case they affect
        authorization for adding other related resources, e.g. metadata
        """
        if getattr(bundle.obj, "id", False):
            project = bundle.obj
            for exp_uri in bundle.data.get("experiments", []):
                try:
                    exp = ExperimentResource.get_via_uri(
                        ExperimentResource(), exp_uri, bundle.request
                    )
                    bundle.obj.experiments.add(exp)
                except NotFound:
                    pass
            if not settings.ONLY_EXPERIMENT_ACLS:
                # ACL for ingestor
                acl = ProjectACL(
                    project=project,
                    user=bundle.request.user,
                    canRead=True,
                    canDownload=True,
                    canWrite=True,
                    canDelete=True,
                    canSensitive=True,
                    isOwner=True,
                    aclOwnershipType=ProjectACL.OWNER_OWNED,
                )
                acl.save()
                if bundle.request.user.id != project.principal_investigator.id:
                    # and for PI
                    acl = ProjectACL(
                        project=project,
                        user=project.principal_investigator,
                        canRead=True,
                        canDownload=True,
                        canWrite=True,
                        canDelete=True,
                        canSensitive=True,
                        isOwner=True,
                        aclOwnershipType=ProjectACL.OWNER_OWNED,
                    )
                    acl.save()
        return super().hydrate_m2m(bundle)

    def obj_create(self, bundle, **kwargs):
        """Currently not tested for failed db transactions as sqlite does not
        enforce limits.
        """
        user = bundle.request.user
        bundle.data["created_by"] = user
        with transaction.atomic():
            project_lead = get_or_create_user(bundle.data["principal_investigator"])
            bundle.data["principal_investigator"] = project_lead
            # Clean up bundle to remove PIDS if the identifiers app is being used.
            if (
                "tardis.apps.identifiers" in settings.INSTALLED_APPS
                and "project" in settings.OBJECTS_WITH_IDENTIFIERS
            ):
                identifiers = None
                if "identifiers" in bundle.data.keys():
                    identifiers = bundle.data.pop("identifiers")
            # Clean up bundle to remove Data classifications if the app is being used
            if "tardis.apps.dataclassification" in settings.INSTALLED_APPS:
                project = bundle.obj
                classification = DATA_CLASSIFICATION_SENSITIVE
                if "classification" in bundle.data.keys():
                    classification = bundle.data.pop("classification")

            bundle = super().obj_create(bundle, **kwargs)
            # After the obj has been created
            if (
                "tardis.apps.identifiers" in settings.INSTALLED_APPS
                and "project" in settings.OBJECTS_WITH_IDENTIFIERS
            ):
                project = bundle.obj
                if identifiers:
                    for identifier in identifiers:
                        ProjectID.objects.create(
                            project=project,
                            identifier=str(identifier),
                        )

            if "tardis.apps.dataclassification" in settings.INSTALLED_APPS:
                ProjectDataClassification.objects.create(
                    project=project, classification=classification
                )
            if bundle.data.get("users", False):
                for entry in bundle.data["users"]:
                    username, isOwner, canDownload, canSensitive = entry
                    acl_user = get_or_create_user(username)
                    ProjectACL.objects.create(
                        project=project,
                        user=acl_user,
                        canRead=True,
                        canDownload=canDownload,
                        canSensitive=canSensitive,
                        isOwner=isOwner,
                    )
            if bundle.data.get("groups", False):
                for entry in bundle.data["groups"]:
                    groupname, isOwner, canDownload, canSensitive = entry
                    acl_group, _ = Group.objects.get_or_create(name=groupname)
                    ProjectACL.objects.create(
                        project=project,
                        group=acl_group,
                        canRead=True,
                        canDownload=canDownload,
                        canSensitive=canSensitive,
                        isOwner=isOwner,
                    )

            return bundle

    def get_project_experiments(self, request, **kwargs):
        """
        Return a list of experiments related to the project
        :param request: a HTTP Request instance
        :type request: :class:`django.http.HttpRequest`
        :param kwargs:
        :return: a list of experiments
        :rtype: JsonResponse: :class: `django.http.JsonResponse`
        """
        from tardis.tardis_portal.models import Experiment

        self.method_check(request, allowed=["get"])
        self.is_authenticated(request)
        project_id = kwargs["pk"]
        if not has_access(request, project_id, "project"):
            return HttpResponseForbidden()

        # Both Macro and Micro ACLs route through ExperimentACLs for this
        exp_list = Experiment.safe.all(user=request.user).filter(projects=project_id)

        exp_list = {"objects": [*exp_list.values("id", "title")]}
        return JsonResponse(exp_list, status=200, safe=False)


class ProjectACLResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, "project")

    class Meta:
        authentication = MyTardisAuthentication()
        authorization = ProjectACLAuthorization()
        object_class = ProjectACL
        queryset = ProjectACL.objects.select_related("user").exclude(
            user__id=settings.PUBLIC_USER_ID
        )
        filtering = {
            "pluginId": ("exact",),
            "entityId": ("exact",),
        }
        ordering = ["id"]

    def hydrate(self, bundle):
        try:
            project = ProjectResource.get_via_uri(
                ProjectResource(), bundle.data["project"], bundle.request
            )
        except NotFound:
            project = Project.objects.get(namespace=bundle.data["project"])
        bundle.obj.project = project
        del bundle.data["project"]
        return bundle


class ProjectParameterSetResource(ParameterSetResource):
    project = fields.ForeignKey(ProjectResource, "project")
    parameters = fields.ToManyField(
        "tardis.apps.projects.api.ProjectParameterResource",
        "projectparameter_set",
        related_name="parameterset",
        full=True,
        null=True,
    )

    class Meta:
        authentication = MyTardisAuthentication()
        authorization = ProjectACLAuthorization()
        serializer = default_serializer
        object_class = ProjectParameterSet
        queryset = ProjectParameterSet.objects.all()

    def dehydrate_parameters(self, bundle):
        if has_sensitive_access(bundle.request, bundle.obj.project.id, "project"):
            return bundle.data["parameters"]
        return [
            x for x in bundle.data["parameters"] if x.obj.name.sensitive is not True
        ]


class ProjectParameterResource(ParameterResource):
    parameterset = fields.ForeignKey(ProjectParameterSetResource, "parameterset")

    class Meta:
        authentication = MyTardisAuthentication()
        authorization = ProjectACLAuthorization()
        serializer = default_serializer
        object_class = ProjectParameter
        queryset = ProjectParameter.objects.all()
