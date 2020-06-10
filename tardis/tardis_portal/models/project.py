import logging
from os import path
from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.db import models
from django.utils.safestring import SafeText
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now as django_time_now
from .institution import Institution
# from ..models import DataManagementPlan # Hook in place for future proofing
from ..managers import OracleSafeManager, SafeManager

from .access_control import ObjectACL

from .license import License

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Project(models.Model):
    """A project is a collection of :class: '~tardis.tardis_portal.experiment.Experiment'
    records. A project can have multiple Experiments but an experiment has only one
    Project.
    Inputs:
    =================================
    """

    PUBLIC_ACCESS_NONE = 1
    PUBLIC_ACCESS_EMBARGO = 25
    PUBLIC_ACCESS_METADATA = 50
    PUBLIC_ACCESS_FULL = 100

    PUBLIC_ACCESS_CHOICES = (
        (PUBLIC_ACCESS_NONE, 'No public access (hidden)'),
        (PUBLIC_ACCESS_EMBARGO, 'Ready to be released pending embargo expiry'),
        (PUBLIC_ACCESS_METADATA, 'Public Metadata only (no data file access)'),
        (PUBLIC_ACCESS_FULL, 'Public'),
    )
    name = models.CharField(max_length=255, null=False, blank=False)
    raid = models.CharField(max_length=255, null=False,
                            blank=False, unique=True)
    description = models.TextField()
    locked = models.BooleanField(default=False)
    public_access = \
        models.PositiveSmallIntegerField(choices=PUBLIC_ACCESS_CHOICES,
                                         null=False,
                                         default=PUBLIC_ACCESS_NONE)
    # TODO No project should have the ingestion service account as the lead_researcher
    lead_researcher = models.ForeignKey(User,
                                        related_name='lead_researcher',
                                        on_delete=models.CASCADE)
    objectacls = GenericRelation(ObjectACL)
    objects = OracleSafeManager()
    embargo_until = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(default=django_time_now)
    end_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User,
                                   on_delete=models.CASCADE)
    url = models.URLField(max_length=255,
                          null=True, blank=True)
    institution = models.ManyToManyField(Institution,
                                         related_name='institutions')
    safe = SafeManager()

    # TODO Integrate DMPs into the project.
    # data_management_plan = models.ManyToManyField(DataManagementPlan,
    #                                              null=True, blank=True)

    class Meta:
        app_label = 'tardis_portal'

    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)

    def getParameterSets(self):
        """Return the project parametersets associated with this
        project.

        """
        from .parameters import Schema
        return self.projectparameterset_set.filter(
            schema__schema_type=Schema.PROJECT)

    def getParametersforIndexing(self):
        """Returns the project parameters associated with this
        project, formatted for elasticsearch.

        """
        from .parameters import ProjectParameter, ParameterName
        paramset = self.getParameterSets()
        param_type_options = {1: 'datetime_value', 2: 'string_value',
                              3: 'numerical_value'}
        param_glob = ProjectParameter.objects.filter(
            parameterset__in=paramset).all().values_list('name', 'datetime_value', 'string_value', 'numerical_value')
        param_list = []
        for sublist in param_glob:
            full_name = ParameterName.objects.get(id=sublist[0]).full_name
            #string2append = (full_name+'=')
            param_dict = {}
            for idx, value in enumerate(sublist[1:]):
                if value is not None:
                    param_dict['full_name'] = str(full_name)
                    param_dict['value'] = str(value)
                    param_dict['type'] = param_type_options[idx+1]
            param_list.append(param_dict)
        return param_list

    def is_embargoed(self):
        if self.embargo_until:
            if datetime.now() < self.embargo_until:
                return True
        return False

    def get_ct(self):
        return ContentType.objects.get_for_model(self)

    def get_owners(self):
        acls = ObjectACL.objects.filter(pluginId='django_user',
                                        content_type=self.get_ct(),
                                        object_id=self.id,
                                        isOwner=True)
        return [acl.get_related_object() for acl in acls]

    def get_users(self):
        acls = ObjectACL.objects.filter(pluginId='django_user',
                                        content_type=self.get_ct(),
                                        object_id=self.id,
                                        canRead=True)
        return [acl.get_related_object() for acl in acls]

    def get_admins(self):
        acls = ObjectACL.objects.filter(pluginId='django_group',
                                        content_type=self.get_ct(),
                                        object_id=self.id,
                                        isOwner=True)
        return [acl.get_related_object() for acl in acls]

    def get_groups(self):
        acls = ObjectACL.objects.filter(pluginId='django_group',
                                        content_type=self.get_ct(),
                                        object_id=self.id,
                                        canRead=True)
        return [acl.get_related_object() for acl in acls]

    def get_groups_and_perms(self):
        acls = ObjectACL.objects.filter(pluginId='django_group',
                                        content_type=self.get_ct(),
                                        object_id=self.id,
                                        canRead=True)
        ret_list = []
        for acl in acls:
            if not acl.isOwner:
                group = acl.get_related_object()
                sensitive_flg = acl.canSensitive
                download_flg = acl.canDownload
                ret_list.append([group,
                                 sensitive_flg,
                                 download_flg])
        return ret_list

    def _has_view_perm(self, user_obj):
        '''
        Called from the ACLAwareBackend class's has_perm method
        in tardis/tardis_portal/auth/authorisation.py

        Returning None means we won't override permissions here,
        i.e. we'll leave it to ACLAwareBackend's has_perm method
        to determine permissions from ObjectACLs
        '''
        if not hasattr(self, 'id'):
            return False
        # May be redundant - left in for the short term
        if self.public_access >= self.PUBLIC_ACCESS_METADATA:
            return True
        return None

    def _has_change_perm(self, user_obj):
        '''
        Called from the ACLAwareBackend class's has_perm method
        in tardis/tardis_portal/auth/authorisation.py

        Returning None means we won't override permissions here,
        i.e. we'll leave it to ACLAwareBackend's has_perm method
        to determine permissions from ObjectACLs
        '''
        if not hasattr(self, 'id'):
            return False
        if self.locked:
            return False
        return None

    def _has_delete_perm(self, user_obj):
        '''
        Called from the ACLAwareBackend class's has_perm method
        in tardis/tardis_portal/auth/authorisation.py

        Returning None means we won't override permissions here,
        i.e. we'll leave it to ACLAwareBackend's has_perm method
        to determine permissions from ObjectACLs
        '''
        if not hasattr(self, 'id'):
            return False
        return None

    def get_datafiles(self, user):
        from .datafile import DataFile
        return DataFile.safe.all(user).filter(dataset__experiments__project=self)

    def get_size(self, user):
        from .datafile import DataFile
        return DataFile.sum_sizes(self.get_datafiles(user))
