"""
helper functions used in documents.py
"""

from django.conf import settings
from django_elasticsearch_dsl import fields

from tardis.tardis_portal.models import (
    ParameterName,
    ExperimentParameter,
    DatasetParameter,
    DatafileParameter,
)

from tardis.apps.projects.models import (
    ProjectParameter,
)


def generic_acl_structure():
    """
    Return the ES structure of an ACL.

    - pluginId = type of ACL owner: user/group/token
    - entityId = ID of the owner
    """
    return fields.NestedField(
        properties={
            "pluginId": fields.KeywordField(),
            "entityId": fields.KeywordField(),
            "canDownload": fields.BooleanField(),
            "canSensitive": fields.BooleanField(),
        }
    )


def generic_parameter_structure():
    """
    Return the ES structure of object parameters and schema.
    The parameter structure splits out string/numerical/datetime
    parameters so that ES can specifically handle each of their
    datatypes.

    - Schemas:
      - schema_id: Id of the object schemas
    - string/numerical/datetime:
      - pn_id: Id of parameter name
      - pn_name: Name of parameter name
      - value: value of parameter
      - sensitive: whether parameter name is sensitive
    """
    return fields.NestedField(
        properties={
            "string": fields.NestedField(
                properties={
                    "pn_id": fields.KeywordField(),
                    "pn_name": fields.KeywordField(),
                    "value": fields.TextField(),
                    "sensitive": fields.BooleanField(),
                }
            ),
            "numerical": fields.NestedField(
                properties={
                    "pn_id": fields.KeywordField(),
                    "pn_name": fields.KeywordField(),
                    "value": fields.FloatField(),
                    "sensitive": fields.BooleanField(),
                }
            ),
            "datetime": fields.NestedField(
                properties={
                    "pn_id": fields.KeywordField(),
                    "pn_name": fields.KeywordField(),
                    "value": fields.DateField(),
                    "sensitive": fields.BooleanField(),
                }
            ),
            "schemas": fields.NestedField(
                properties={"schema_id": fields.KeywordField()}
            ),
        },
    )


def prepare_generic_acls_build(INSTANCE_ACL_SET, return_list):
    """Returns the ACLs associated with this
    object, formatted for elasticsearch.
    """
    for acl in INSTANCE_ACL_SET:
        acl_dict = {}
        if acl["user__id"] is not None:
            acl_dict["pluginId"] = "django_user"
            acl_dict["entityId"] = acl["user__id"]
        if acl["group__id"] is not None:
            acl_dict["pluginId"] = "django_group"
            acl_dict["entityId"] = acl["group__id"]
        if acl["token__id"] is not None:
            # token access shouldn't be added to search
            # unless search is given a way of checking token expiry
            continue
        # add in permission booleans
        acl_dict["canDownload"] = acl["canDownload"]
        acl_dict["canSensitive"] = acl["canSensitive"]
        if acl_dict not in return_list:
            return_list.append(acl_dict)


def prepare_generic_acls(type, INSTANCE_ACL_SET, INSTANCE_EXPS=None):
    """Returns the ACLs associated with this
    object, formatted for elasticsearch.

    This function is mostly just a wrapper around "prepare_generic_acls_build"
    to account for current macro/micro behaviour.
    """
    return_list = []
    if settings.ONLY_EXPERIMENT_ACLS and type != "experiment":
        for exp in INSTANCE_EXPS.all():
            prepare_generic_acls_build(
                exp.experimentacl_set.select_related("user", "group", "token")
                .all()
                .exclude(user__id=settings.PUBLIC_USER_ID)
                .values(
                    "user__id",
                    "group__id",
                    "token__id",
                    "canDownload",
                    "canSensitive",
                ),
                return_list,
            )
    else:
        prepare_generic_acls_build(
            INSTANCE_ACL_SET.select_related("user", "group", "token")
            .all()
            .exclude(user__id=settings.PUBLIC_USER_ID)
            .values(
                "user__id",
                "group__id",
                "token__id",
                "canDownload",
                "canSensitive",
            ),
            return_list,
        )
    return return_list


def prepare_generic_parameters(instance, type):
    """Returns the parameters associated with the provided instance,
    formatted for elasticsearch."""

    type_dict = {
        "project": ProjectParameter,
        "experiment": ExperimentParameter,
        "dataset": DatasetParameter,
        "datafile": DatafileParameter,
    }
    OBJPARAMETERS = type_dict[type]

    # get list of object parametersets
    paramsets = list(instance.getParameterSets())
    parameter_groups = {
        "string": [],
        "numerical": [],
        "datetime": [],
        "schemas": [],
    }
    # iterate over parametersets of an object
    for paramset in paramsets:
        param_type = {1: "datetime", 2: "string", 3: "numerical"}
        # query parameters from parameterset
        param_glob = OBJPARAMETERS.objects.filter(parameterset=paramset).values_list(
            "name",
            "datetime_value",
            "string_value",
            "numerical_value",
        )
        # add schema information to dict
        parameter_groups["schemas"].append({"schema_id": paramset.schema_id})
        # iterate over parameter info "name/datetime/string/numerical"
        for sublist in param_glob:
            # query parametername info using "name"
            PN = ParameterName.objects.get(id=sublist[0])
            # build dict for param
            param_dict = {}
            type_idx = 0
            # iterate over datetime/string/numerical info
            for idx, value in enumerate(sublist[1:]):
                # if datetime/string/numerical atually contains info
                if value not in [None, ""]:
                    # add parametername info to dict
                    param_dict["pn_id"] = str(PN.id)
                    param_dict["pn_name"] = str(PN.full_name)
                    param_dict["sensitive"] = PN.sensitive
                    type_idx = idx + 1
                    # detect type of param, and add value to dict
                    if type_idx == 1:
                        param_dict["value"] = value
                    elif type_idx == 2:
                        param_dict["value"] = str(value)
                    elif type_idx == 3:
                        param_dict["value"] = float(value)
            # if parameter with a value is added, add param_dict to
            # parameters_dict
            if type_idx:
                parameter_groups[param_type[type_idx]].append(param_dict)
    return parameter_groups
