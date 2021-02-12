"""
managers.py
.. moduleauthor::  Ulrich Felzmann <ulrich.felzmann@versi.edu.au>
"""

from datetime import datetime

from django.db import models
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.db.models import Prefetch

#from .auth.localdb_auth import django_user, django_group
from .models.access_control import (ProjectACL, ExperimentACL,
                                    DatasetACL, DatafileACL)


class OracleSafeManager(models.Manager):
    """
    Implements a custom manager which automatically defers the
    retreival of any TextField fields on calls to get_queryset. This
    is to avoid the known issue that 'distinct' calls on query_sets
    containing TextFields fail when Oracle is being used as the
    backend.
    """

    def get_queryset(self):
        from django.db import connection
        if connection.settings_dict['ENGINE'] == 'django.db.backends.oracle':
            fields = [a.attname for a in self.model._meta.fields
                      if a.db_type(connection=connection) == 'NCLOB']
            return super().get_queryset().defer(*fields)
        return super().get_queryset()


class ParameterNameManager(models.Manager):
    def get_by_natural_key(self, namespace, name):
        return self.get(schema__namespace=namespace, name=name)


class SchemaManager(models.Manager):
    def get_by_natural_key(self, namespace):
        return self.get(namespace=namespace)


class SafeManager(models.Manager):

    """
    Implements a custom manager for the Project/Experiment/Dataset/DataFile
    models which checks the authorisation rules for the requesting user first
    To make this work, the request must be passed to all class
    functions. The username and the group memberships are then
    resolved via the user.userprofile.ext_groups and user objects.
    The :py:mod:`tardis.tardis_portal.auth.AuthService` is responsible for
    filling the request.groups object.
    """

    def all(self, user, downloadable=False, viewsensitive=False):  # @ReservedAssignment
        """
        Returns all proj/exp/set/files a user - either authenticated or
        anonymous - is allowed to see and search
        :param User user: a User instance
        :param bool downloadable: Boolean flag to return downloadable objects
        :param bool viewsensitive: Boolean flag to return viewsensitive objects
        :returns: QuerySet of objects
        :rtype: QuerySet
        """

        query = self._query_owned_and_shared(
            user, downloadable, viewsensitive)  # self._query_all_public() |\

        return query.distinct()

    def _query_owned(self, user, user_id=None):

        if user is None:
            user = User.objects.get(pk=user_id)

        if self.model.get_ct(self.model).model == "project":
            from .models import Project
            query = Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("user"))
                                                ).filter(projectacl__user=user,
                                                         projectacl__isOwner=True,
                                                         ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                   projectacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model == "experiment":
            from .models import Experiment
            query = Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("user"))
                                                ).filter(experimentacl__user=user,
                                                         experimentacl__isOwner=True,
                                                         ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                   experimentacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model == "dataset":
            from .models import Dataset
            query = Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("user"))
                                                ).filter(datasetacl__user=user,
                                                         datasetacl__isOwner=True,
                                                         ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                   datasetacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
            from .models import DataFile
            query = DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("user"))
                                                ).filter(datafileacl__user=user,
                                                         datafileacl__isOwner=True,
                                                         ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                   datafileacl__expiryDate__lte=datetime.today()
                                                                   )

        return query


    def _query_owned_by_group(self, group, group_id=None):

        if group is None:
            group = Group.objects.get(pk=group_id)

        if self.model.get_ct(self.model).model == "project":
            from .models import Project
            query = Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("group"))
                                                ).filter(projectacl__group=group,
                                                         projectacl__isOwner=True,
                                                         ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                   projectacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model == "experiment":
            from .models import Experiment
            query = Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("group"))
                                                ).filter(experimentacl__group=group,
                                                         experimentacl__isOwner=True,
                                                         ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                   experimentacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model == "dataset":
            from .models import Dataset
            query = Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("group"))
                                                ).filter(datasetacl__group=group,
                                                         datasetacl__isOwner=True,
                                                         ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                   datasetacl__expiryDate__lte=datetime.today()
                                                                   )

        if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
            from .models import DataFile
            query = DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("group"))
                                                ).filter(datafileacl__group=group,
                                                         datafileacl__isOwner=True,
                                                         ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                   datafileacl__expiryDate__lte=datetime.today()
                                                                   )

        return query


    def _query_shared(self, user, downloadable=False, viewsensitive=False):
        '''
        get all shared proj/exp/set/files, not owned ones
        '''
        # if the user is not authenticated, only tokens apply
        # this is almost duplicate code of end of has_perm in authorisation.py
        # should be refactored, but cannot think of good way atm
        if not user.is_authenticated:
            # Token - refactor when tokens ready
            from .auth.token_auth import TokenGroupProvider
            query = Q(id=None)
            tgp = TokenGroupProvider()
            for group in tgp.getGroups(user):

                if any([downloadable, viewsensitive]):
                    query_inputs={}
                    if downloadable:
                        query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canDownload"] = True
                    if viewsensitive:
                        query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canSensitive"] = True

                    if self.model.get_ct(self.model).model == "project":
                        from .models import Project
                        query |= Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("group"))
                                                            ).filter(projectacl__group=group,
                                                                     projectacl__isOwner=False,
                                                                     **query_inputs,
                                                                     ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                               projectacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model == "experiment":
                        from .models import Experiment
                        query |= Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("group"))
                                                            ).filter(experimentacl__group=group,
                                                                     experimentacl__isOwner=False,
                                                                     **query_inputs,
                                                                     ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                               experimentacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model == "dataset":
                        from .models import Dataset
                        query |= Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("group"))
                                                            ).filter(datasetacl__group=group,
                                                                     datasetacl__isOwner=False,
                                                                     **query_inputs,
                                                                     ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                               datasetacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                        from .models import DataFile
                        query |= DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("group"))
                                                            ).filter(datafileacl__group=group,
                                                                     datafileacl__isOwner=False,
                                                                     **query_inputs,
                                                                     ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                               datafileacl__expiryDate__lte=datetime.today()
                                                                               )

                else:
                    if self.model.get_ct(self.model).model == "project":
                        from .models import Project
                        query |= Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("group"))
                                                            ).filter(projectacl__group=group,
                                                                     projectacl__isOwner=False,
                                                                     ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                               projectacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model == "experiment":
                        from .models import Experiment
                        query |= Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("group"))
                                                            ).filter(experimentacl__group=group,
                                                                     experimentacl__isOwner=False,
                                                                     ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                               experimentacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model == "dataset":
                        from .models import Dataset
                        query |= Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("group"))
                                                            ).filter(datasetacl__group=group,
                                                                     datasetacl__isOwner=False,
                                                                 ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                               datasetacl__expiryDate__lte=datetime.today()
                                                                               )

                    if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                        from .models import DataFile
                        query |= DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("group"))
                                                            ).filter(datafileacl__group=group,
                                                                     datafileacl__isOwner=False,
                                                                     ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                               datafileacl__expiryDate__lte=datetime.today()
                                                                               )
            return query

        # for which proj/exp/set/files does the user have read access
        # based on USER permissions?
        if any([downloadable, viewsensitive]):
            query_inputs={}
            if downloadable:
                query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canDownload"] = True
            if viewsensitive:
                query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canSensitive"] = True

            if self.model.get_ct(self.model).model == "project":
                from .models import Project
                query = Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("user"))
                                                    ).filter(projectacl__user=user,
                                                             projectacl__isOwner=False,
                                                             **query_inputs,
                                                             ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                       projectacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model == "experiment":
                from .models import Experiment
                query = Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("user"))
                                                    ).filter(experimentacl__user=user,
                                                             experimentacl__isOwner=False,
                                                             **query_inputs,
                                                             ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                       experimentacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model == "dataset":
                from .models import Dataset
                query = Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("user"))
                                                    ).filter(datasetacl__user=user,
                                                             datasetacl__isOwner=False,
                                                             **query_inputs,
                                                             ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                       datasetacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                from .models import DataFile
                query = DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("user"))
                                                    ).filter(datafileacl__user=user,
                                                             datafileacl__isOwner=False,
                                                             **query_inputs,
                                                             ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                       datafileacl__expiryDate__lte=datetime.today()
                                                                       )

        else:
            if self.model.get_ct(self.model).model == "project":
                from .models import Project
                query = Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("user"))
                                                    ).filter(projectacl__user=user,
                                                             projectacl__isOwner=False,
                                                             ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                       projectacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model == "experiment":
                from .models import Experiment
                query = Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("user"))
                                                    ).filter(experimentacl__user=user,
                                                             experimentacl__isOwner=False,
                                                             ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                       experimentacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model == "dataset":
                from .models import Dataset
                query = Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("user"))
                                                    ).filter(datasetacl__user=user,
                                                             datasetacl__isOwner=False,
                                                             ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                       datasetacl__expiryDate__lte=datetime.today()
                                                                       )

            if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                from .models import DataFile
                query = DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("user"))
                                                    ).filter(datafileacl__user=user,
                                                             datafileacl__isOwner=False,
                                                             ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                       datafileacl__expiryDate__lte=datetime.today()
                                                                       )
        # for which does proj/exp/set/files does the user have read access
        # based on GROUP permissions
        for name, group in user.userprofile.ext_groups:
            if any([downloadable, viewsensitive]):
                query_inputs={}
                if downloadable:
                    query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canDownload"] = True
                if viewsensitive:
                    query_inputs[self.model.get_ct(self.model).model.replace(' ','')+"acl__canSensitive"] = True

                if self.model.get_ct(self.model).model == "project":
                    from .models import Project
                    query |= Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("group"))
                                                        ).filter(projectacl__group=group,
                                                                 projectacl__isOwner=False,
                                                                 **query_inputs,
                                                                 ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                           projectacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model == "experiment":
                    from .models import Experiment
                    query |= Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("group"))
                                                        ).filter(experimentacl__group=group,
                                                                 experimentacl__isOwner=False,
                                                                 **query_inputs,
                                                                 ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                           experimentacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model == "dataset":
                    from .models import Dataset
                    query |= Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("group"))
                                                        ).filter(datasetacl__group=group,
                                                                 datasetacl__isOwner=False,
                                                                 **query_inputs,
                                                                 ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                           datasetacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                    from .models import DataFile
                    query |= DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("group"))
                                                        ).filter(datafileacl__group=group,
                                                                 datafileacl__isOwner=False,
                                                                 **query_inputs,
                                                                 ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                           datafileacl__expiryDate__lte=datetime.today()
                                                                           )

            else:
                if self.model.get_ct(self.model).model == "project":
                    from .models import Project
                    query |= Project.objects.prefetch_related(Prefetch("projectacl_set", queryset=ProjectACL.objects.select_related("group"))
                                                        ).filter(projectacl__group=group,
                                                                 projectacl__isOwner=False,
                                                                 ).exclude(projectacl__effectiveDate__gte=datetime.today(),
                                                                           projectacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model == "experiment":
                    from .models import Experiment
                    query |= Experiment.objects.prefetch_related(Prefetch("experimentacl_set", queryset=ExperimentACL.objects.select_related("group"))
                                                        ).filter(experimentacl__group=group,
                                                                 experimentacl__isOwner=False,
                                                                 ).exclude(experimentacl__effectiveDate__gte=datetime.today(),
                                                                           experimentacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model == "dataset":
                    from .models import Dataset
                    query |= Dataset.objects.prefetch_related(Prefetch("datasetacl_set", queryset=DatasetACL.objects.select_related("group"))
                                                        ).filter(datasetacl__group=group,
                                                                 datasetacl__isOwner=False,
                                                                 ).exclude(datasetacl__effectiveDate__gte=datetime.today(),
                                                                           datasetacl__expiryDate__lte=datetime.today()
                                                                           )

                if self.model.get_ct(self.model).model.replace(' ','') == "datafile":
                    from .models import DataFile
                    query |= DataFile.objects.prefetch_related(Prefetch("datafileacl_set", queryset=DatafileACL.objects.select_related("group"))
                                                        ).filter(datafileacl__group=group,
                                                                 datafileacl__isOwner=False,
                                                                 ).exclude(datafileacl__effectiveDate__gte=datetime.today(),
                                                                           datafileacl__expiryDate__lte=datetime.today()
                                                                           )
        return query


    def _query_owned_and_shared(self, user, downloadable=False, viewsensitive=False):
        return self._query_shared(user, downloadable, viewsensitive) | self._query_owned(user)


    def owned_and_shared(self, user, downloadable=False, viewsensitive=False):
        return self._query_owned_and_shared(user, downloadable, viewsensitive).distinct()


    def owned(self, user):
        """
        Return all proj/exp/set/files which are owned by a particular user, including
        those shared with a group of which the user is a member.
        :param User user: a User instance
        :returns: QuerySet of proj/exp/set/files owned by user
        :rtype: QuerySet
        """

        # the user must be authenticated
        if not user.is_authenticated:
            return super().get_queryset().none()

        query = self._query_owned(user)
        for group in user.groups.all():
            query |= self._query_owned_by_group(group)
        return query.distinct()


    def shared(self, user):
        return self._query_shared(user).distinct()


    def get(self, user, obj_id):
        """
        Returns a proj/exp/set/file under the consideration of the ACL rules
        Raises PermissionDenied if the user does not have access.
        :param User user: a User instance
        :param int obj_id: the ID of the proj/exp/set/file to be edited
        :returns: proj/exp/set/file
        :rtype: proj/exp/set/file
        :raises PermissionDenied:
        """
        obj = super().get(pk=obj_id)

        if user.has_perm('tardis_acls.view_'+self.model.get_ct(self.model).model.replace(' ',''), obj):
            return obj
        raise PermissionDenied


    def owned_by_user(self, user):
        """
        Return all proj/exp/set/files which are owned by a particular user id
        :param User user: a User Object
        :return: QuerySet of proj/exp/set/files owned by user
        :rtype: QuerySet
        """
        query = self._query_owned(user)
        return query


    def owned_by_group(self, group):
        """
        Return all proj/exp/set/files that are owned by a particular group
        """
        query = self._query_owned_by_group(group)
        return query


    def owned_by_user_id(self, userId):
        """
        Return all proj/exp/set/files which are owned by a particular user id
        :param int userId: a User ID
        :returns: QuerySet of proj/exp/set/files owned by user id
        :rtype: QuerySet
        """
        query = self._query_owned(user=None, user_id=userId)
        return query


    def user_acls(self, obj_id):
        """
        Returns a list of ACL rules associated with this proj/exp/set/file.
        :param obj_id: the ID of the proj/exp/set/file
        :type obj_id: string
        :returns: QuerySet of ACLs
        :rtype: QuerySet
        """
        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            return obj.projectacl_set.select_related("user").filter(user__isnull=False,
                                             aclOwnershipType=ProjectACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            return obj.experimentacl_set.select_related("user").filter(user__isnull=False,
                                             aclOwnershipType=ExperimentACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            return obj.datasetacl_set.select_related("user").filter(user__isnull=False,
                                             aclOwnershipType=DatasetACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            return obj.datafileacl_set.select_related("user").filter(user__isnull=False,
                                             aclOwnershipType=DatafileACL.OWNER_OWNED)
        return super().get_queryset().none()


    def users(self, obj_id):
        """
        Returns a list of users who have ACL rules associated with this
        proj/exp/set/file.
        :param int obj_id: the ID of the proj/exp/set/file
        :returns: QuerySet of Users with proj/exp/set/file access
        :rtype: QuerySet
        """
        acl = self.user_acls(obj_id)
        return User.objects.filter(pk__in=[int(a.user.id) for a in acl])

    def group_acls(self, obj_id):
        """
        Returns a list of ACL rules associated with this proj/exp/set/file.
        :param obj_id: the ID of the proj/exp/set/file
        :type obj_id: string
        :returns: QuerySet of ACLs
        :rtype: QuerySet
        """
        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            return obj.projectacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ProjectACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            return obj.experimentacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ExperimentACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            return obj.datasetacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatasetACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            return obj.datafileacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatafileACL.OWNER_OWNED)
        return super().get_queryset().none()

    def groups(self, obj_id):
        """
        Returns a list of users who have ACL rules associated with this
        proj/exp/set/file.
        :param int obj_id: the ID of the proj/exp/set/file
        :returns: QuerySet of Users with proj/exp/set/file access
        :rtype: QuerySet
        """
        acl = self.group_acls(obj_id)
        return Group.objects.filter(pk__in=[int(a.group.id) for a in acl])

    def user_owned_groups(self, obj_id):
        """
        returns a list of user owned-groups which have ACL rules
        associated with this proj/exp/set/file
        :param int obj_id: the ID of the proj/exp/set/file to be edited
        :returns: QuerySet of non system Groups
        :rtype: QuerySet
        """

        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            acl = obj.projectacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ProjectACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            acl = obj.experimentacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ExperimentACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            acl = obj.datasetacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatasetACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            acl = obj.datafileacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatafileACL.OWNER_OWNED)

        return Group.objects.filter(pk__in=[str(a.group.id) for a in acl])


    def group_acls_user_owned(self, obj_id):
        """
        Returns a list of ACL rules associated with this proj/exp/set/file.
        :param int obj_id: the ID of the proj/exp/set/file
        :returns: QuerySet of ACLs
        :rtype: QuerySet
        """

        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            return obj.projectacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ProjectACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            return obj.experimentacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ExperimentACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            return obj.datasetacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatasetACL.OWNER_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            return obj.datafileacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatafileACL.OWNER_OWNED)
        return super().get_queryset().none()


    def group_acls_system_owned(self, obj_id):
        """
        Returns a list of ACL rules associated with this proj/exp/set/file.
        :param int obj_id: the ID of the proj/exp/set/file
        :returns: QuerySet of system-owned ACLs for proj/exp/set/file
        :rtype: QuerySet
        """

        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            return obj.projectacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ProjectACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            return obj.experimentacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ExperimentACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            return obj.datasetacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatasetACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            return obj.datafileacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatafileACL.SYSTEM_OWNED)
        return super().get_queryset().none()


    def system_owned_groups(self, obj_id):
        """
        returns a list of sytem-owned groups which have ACL rules
        associated with this proj/exp/set/file
        :param obj_id: the ID of the proj/exp/set/file to be edited
        :type obj_id: string
        :returns: system owned groups for proj/exp/set/file
        :rtype: QuerySet
        """

        obj = super().get(pk=obj_id)

        if self.model.get_ct(self.model).model == "project":
            acl = obj.projectacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ProjectACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model == "experiment":
            acl = obj.experimentacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=ExperimentACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model == "dataset":
            acl = obj.datasetacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatasetACL.SYSTEM_OWNED)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            acl = obj.datafileacl_set.select_related("group").filter(group__isnull=False,
                                             aclOwnershipType=DatafileACL.SYSTEM_OWNED)

        return Group.objects.filter(pk__in=[str(a.group.id) for a in acl])


    def external_users(self, obj_id):
        """
        returns a list of groups which have external ACL rules
        :param int obj_id: the ID of the proj/exp/set/file to be edited
        :returns: list of groups with external ACLs
        :rtype: list
        """

        if self.model.get_ct(self.model).model == "project":
            acl = obj.projectacl_set.select_related("user", "group").filter(
                                        user__isnull=True, group__isnull=True)
        if self.model.get_ct(self.model).model == "experiment":
            acl = obj.experimentacl_set.select_related("user", "group").filter(
                                        user__isnull=True, group__isnull=True)
        if self.model.get_ct(self.model).model == "dataset":
            acl = obj.datasetacl_set.select_related("user", "group").filter(
                                        user__isnull=True, group__isnull=True)
        if self.model.get_ct(self.model).model.replace(" ","") == "datafile":
            acl = obj.datafileacl_set.select_related("user", "group").filter(
                                        user__isnull=True, group__isnull=True)

        if not acl:
            return None

        from .auth import AuthService
        authService = AuthService()

        # Token - refactor when tokens ready
        result = []
        for a in acl:
            group = authService.searchGroups(plugin=a.pluginId,
                                             name=a.entityId)
            if group:
                result += group
        return result


    # Experiment only so far
    def public(self):
        query = self._query_all_public()
        return super().get_queryset().filter(
            query).distinct()


    # Experiment only so far
    def _query_all_public(self):
        from .models import Experiment
        return ~Q(public_access=Experiment.PUBLIC_ACCESS_NONE) &\
               ~Q(public_access=Experiment.PUBLIC_ACCESS_EMBARGO)
