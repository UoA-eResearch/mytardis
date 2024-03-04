# pylint: disable=C0302,R1702
"""
RESTful API for MyTardis search.
Implemented with Tastypie.

.. moduleauthor:: Manish Kumar <rishimanish123@gmail.com>
.. moduleauthor:: Mike Laverick <mike.laverick@auckland.ac.nz>
"""
import json

from django.conf import settings

import pytz
from django_elasticsearch_dsl.search import Search
from elasticsearch_dsl import MultiSearch
from tastypie import fields
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpUnauthorized
from tastypie.resources import Bundle, Resource
from tastypie.serializers import Serializer

from tardis.tardis_portal.api import default_authentication
from tardis.tardis_portal.models import (
    Experiment,
    Dataset,
    DataFile,
    Schema,
    ParameterName,
)
from tardis.apps.projects.models import Project
from .utils.api import (
    create_user_and_group_query,
    query_keywords_and_metadata,
    query_apply_filters,
    query_add_sorting,
    cleaning_acls,
    cleaning_ids,
    cleaning_preload,
    cleaning_parent_filter,
    cleaning_results,
)

LOCAL_TZ = pytz.timezone(settings.TIME_ZONE)
RESULTS_PER_PAGE = settings.RESULTS_PER_PAGE
MIN_CUTOFF_SCORE = settings.MIN_CUTOFF_SCORE


class PrettyJSONSerializer(Serializer):
    json_indent = 2

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        return (
            json.dumps(
                data,
                cls=json.JSONEncoder,
                sort_keys=True,
                ensure_ascii=False,
                indent=self.json_indent,
            )
            + "\n"
        )


if settings.DEBUG:
    default_serializer = PrettyJSONSerializer()
else:
    default_serializer = Serializer()


class SearchObject(object):
    """Basic TastyPie API object to hold search results"""

    def __init__(self, hits=None, total_hits=None, id=None):
        self.hits = hits
        self.total_hits = total_hits
        self.id = id


class SchemasObject(object):
    """Basic TastyPie API object to hold schemas for filter bar population"""

    def __init__(self, schemas=None, id=None):
        self.schemas = schemas
        self.id = id


class SchemasAppResource(Resource):
    """Tastypie resource for schemas"""

    schemas = fields.ApiField(attribute="schemas", null=True)

    class Meta:
        resource_name = "get-schemas"
        list_allowed_methods = ["get"]
        serializer = default_serializer
        authentication = default_authentication
        object_class = SchemasObject
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs["pk"] = bundle_or_obj.obj.id
        else:
            kwargs["pk"] = bundle_or_obj["id"]
        return kwargs

    def get_object_list(self, request):
        """
        Populates the API response with schemas and metadata fields that
        a user can access.
        TODO: Probably separate out PUBLIC_DATA schemas
        """

        # if a user is not logged in, return empty for their schemas
        if not request.user.is_authenticated:
            result_dict = {
                "project": None,
                "experiment": None,
                "dataset": None,
                "datafile": None,
            }
            return [SchemasObject(id=1, schemas=result_dict)]

        # pull out schema IDs for all accessible objects for a user
        result_dict = {}
        for string, model in {
            "project": Project,
            "experiment": Experiment,
            "dataset": Dataset,
            "datafile": DataFile,
        }:
            result_dict[string] = [
                *{
                    *model.safe.all(user=request.user)
                    .prefetch_related(string + "parameterset")
                    .values_list(string + "parameterset__schema__id", flat=True)
                }
            ]

        # create a return dictionary of schemas and their non-sensitive metadata fields
        safe_dict = {}
        # iterate over accessible schemas
        for key, val in result_dict.items():
            safe_dict[key] = {}
            for value in val:
                # if object type has schemas, add them to safe_dict
                if value is not None:
                    schema_id = str(value)
                    schema_dict = {
                        "id": schema_id,
                        "type": key,
                        "schema_name": Schema.objects.get(id=value).name,
                        "parameters": {},
                    }
                    # get parameter_names associated with schema
                    param_names = ParameterName.objects.filter(
                        schema__id=value, sensitive=False
                    )
                    for param in param_names:
                        type_dict = {
                            1: "NUMERIC",
                            2: "STRING",
                            3: "URL",
                            4: "LINK",
                            5: "FILENAME",
                            6: "DATETIME",
                            7: "LONGSTRING",
                            8: "JSON",
                        }
                        param_id = str(param.id)
                        param_dict = {
                            "id": param_id,
                            "full_name": param.full_name,
                            "data_type": type_dict[param.data_type],
                        }
                        # append parameter info to relevant schema
                        schema_dict["parameters"][param_id] = param_dict
                    # add completed schema to schema_dict ready for return
                    safe_dict[key][schema_id] = schema_dict
        return [SchemasObject(id=1, schemas=safe_dict)]

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)


class SearchAppResource(Resource):
    """Tastypie resource for search"""

    hits = fields.ApiField(attribute="hits", null=True)
    total_hits = fields.ApiField(attribute="total_hits", null=True)

    class Meta:
        resource_name = "search"
        list_allowed_methods = ["post"]
        serializer = default_serializer
        authentication = default_authentication
        object_class = SearchObject
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs["pk"] = bundle_or_obj.obj.id
        else:
            kwargs["pk"] = bundle_or_obj["id"]

        return kwargs

    def get_object_list(self, request):
        return request

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_create(self, bundle, **kwargs):
        bundle = self.create_search_results(bundle)
        return bundle

    def create_search_results(self, bundle):
        user = bundle.request.user
        if not user.is_authenticated:
            # Return a 401 error to ask users to log in.
            raise ImmediateHttpResponse(
                response=HttpUnauthorized(
                    "Search not yet available for public use; Please log in."
                )
            )
            # result_dict = simple_search_public_data(query_text)
            # return [SearchObject(id=1, hits=result_dict)]
        groups = user.groups.all()

        # This holds the "text" from all the object specific "keyword" search bars,
        # which may ALL have been populated with the same text via the menubar search bar
        query_text = bundle.data.get("query", None)
        # This holds all of the intrinsic and schema-specific metadata filters per object
        filters = bundle.data.get("filters", None)
        # result specific bundles for pagination and sorting
        request_sorting = bundle.data.get("sort", None)
        request_size = bundle.data.get("size", 20)
        request_offset = bundle.data.get("offset", 0)
        # result specific bundle to trigger a object specific search update
        request_type = bundle.data.get("type", None)

        """Mock input
        request_for_pag = True
        if request_for_pag:
            request_offset = 37
            request_size = 50
            request_sorting = [#{ 'field': ["title"], 'order': "desc" },
                               #{ 'field': ["experiments","title"], 'order': "desc" },
                               { 'field': ["size"], 'order': "desc" }]
            request_type = 'datafile' 
        """

        # if API request object type isn't specified default to all object types
        if request_type is None:
            index_list = ["project", "experiment", "dataset", "datafile"]
            title_list = ["name", "title", "description", "filename"]
        # If API request object type is specified then specify object type + parent
        # heirarchy object types, and their intrinsic "title" field names
        else:
            # probably some nicer structure/way to do this
            type_2_list = {
                "project": {"index": ["project"], "match": ["name"]},
                "experiment": {
                    "index": ["project", "experiment"],
                    "match": ["name", "title"],
                },
                "dataset": {
                    "index": ["project", "experiment", "dataset"],
                    "match": ["name", "title", "description"],
                },
                "datafile": {
                    "index": ["project", "experiment", "dataset", "datafile"],
                    "match": ["name", "title", "description", "filename"],
                },
            }
            index_list = type_2_list[request_type]["index"]
            title_list = type_2_list[request_type]["match"]

        # Numerically specify the order of heirarchy
        hierarchy = {"project": 4, "experiment": 3, "dataset": 2, "datafile": 1}
        # Define a numerical filter_level for objects, below which we enforce a
        # parent-must-be-in-results criteria
        filter_level = 0

        # create multisearch object to search all 4 objects in parallel
        ms = MultiSearch(index=index_list)

        # iterate over object types required in this search request
        for idx, obj in enumerate(index_list):

            # add user/group criteria to searchers
            query_obj = create_user_and_group_query(user=user, groups=groups)

            # Search on title/keywords + on non-sensitive metadata
            if query_text is not None:
                # parent-child filter isn't enforced here right now
                # if filter_level < hierarchy[obj]:
                #    filter_level = hierarchy[obj]
                if obj in query_text.keys():
                    query_obj = query_keywords_and_metadata(
                        query_obj, query_text, obj, idx, title_list
                    )

            # Apply intrinsic filters + metadata filters to search
            if filters is not None:
                # filter_op = filters['op']     This isn't used for now
                query_obj, filter_level = query_apply_filters(
                    query_obj, filters, obj, filter_level, hierarchy
                )

            # Define fields not to return in the search results
            excluded_fields_list = [
                "end_time",
                "institution",
                "principal_investigator",
                "created_by",
                "end_time",
                "update_time",
                "instrument",
                "file_extension",
                "modification_time",
                "parameters.string.pn_id",
                "parameters.numerical.pn_id",
                "parameters.datetime.pn_id",
                "acls",
            ]
            # "description" field is crucial for datasets, but too verbose for experiments
            if obj != "dataset":
                excluded_fields_list.append("description")

            # Apply sorting filters based upon request and defaults
            sort_dict = {}
            sort_dict = query_add_sorting(request_sorting, obj, sort_dict)

            # If sort dict is still empty even after filters, add in the defaults
            if not sort_dict:
                sort_dict = {title_list[idx] + ".raw": {"order": "asc"}}

            # Finally, add the search to the multi-search object, ready for execution
            ms = ms.add(
                Search(index=obj)
                .sort(sort_dict)
                .extra(size=RESULTS_PER_PAGE, min_score=MIN_CUTOFF_SCORE)
                .query(query_obj)
                .source(excludes=excluded_fields_list)
            )

        # execute the multi-search object and return results
        results = ms.execute()

        # --------------------
        # Post-search cleaning
        # --------------------

        # load in object IDs for all objects a user has sensitive access to
        projects_sens = cleaning_acls(user, groups, "project", canSensitive=True)
        experiments_sens = cleaning_acls(user, groups, "experiment", canSensitive=True)
        datasets_sens = cleaning_acls(user, groups, "dataset", canSensitive=True)
        datafiles_sens = cleaning_acls(user, groups, "datafile", canSensitive=True)

        # load in datafile IDs for all datafiles a user has download access to
        datafiles_dl = cleaning_acls(user, groups, "datafile", canDownload=True)

        # re-structure into convenient dictionary
        preloaded = {
            "project": {"sens_list": projects_sens, "objects": {}},
            "experiment": {"sens_list": experiments_sens, "objects": {}},
            "dataset": {"sens_list": datasets_sens, "objects": {}},
            "datafile": {"sens_list": datafiles_sens, "objects": {}},
        }

        # load in object IDs for all objects a user has read access to,
        # and IDs for all of the object's nested-children - regardless of user
        # access to these child objects (the access check come later)
        projects = cleaning_ids(user, groups, "project")
        experiments = cleaning_ids(user, groups, "experiment")
        datasets = cleaning_ids(user, groups, "dataset")
        datafiles = cleaning_ids(user, groups, "datafile")

        # add data to preloaded["objects"] dictionary with ID as key
        # and nested items as value - key/values.
        preloaded = cleaning_preload(
            preloaded, projects, experiments, datasets, datafiles
        )

        # Create the result object which will be returned to the front-end
        result_dict = {k: [] for k in ["project", "experiment", "dataset", "datafile"]}

        # If filters are active, enforce the "parent in results" criteria on relevant objects
        if filter_level:
            results = cleaning_parent_filter(results, filter_level)

        # Count the number of search results after elasticsearch + parent filtering
        total_hits = {
            index_list[idx]: len(type.hits.hits) for idx, type in enumerate(results)
        }

        # Pagination done before final cleaning to reduce "clean_parent_ids" duration
        # Default Pagination handled by response.get if key isn't specified
        for item in results:
            item.hits.hits = item.hits.hits[
                request_offset : (request_offset + request_size)
            ]

        # Clean and prepare the results "hit" objects and append them to the results_dict
        result_dict = cleaning_results(results, result_dict, preloaded, datafiles_dl)

        # Removes parent IDs from hits once parent-filtering applied
        # Removed for tidiness in returned response to front-end
        # Define parent_type for experiment/datafile (N/A for project)
        parent_child = {
            "experiment": "projects",
            "dataset": "experiments",
            "datafile": "dataset",
        }
        for objs in ["experiment", "dataset", "datafile"]:
            for obj_idx, obj in reversed([*enumerate(result_dict[objs])]):
                del result_dict[objs][obj_idx]["_source"][parent_child[obj["_index"]]]

        # If individual object type requested, limit the returned values to that object type
        if request_type is not None:
            result_dict = {request_type: result_dict.pop(request_type)}
            total_hits = {request_type: total_hits.pop(request_type)}

        # add search results to bundle, and return bundle
        bundle.obj = SearchObject(id=1, hits=result_dict, total_hits=total_hits)
        return bundle

    # def get_object_list(self, request):
    #    user = request.user
    #    query_text = request.GET.get("query", None)
    #    if not user.is_authenticated:
    #        result_dict = simple_search_public_data(query_text)
    #        return [SearchObject(id=1, hits=result_dict)]
    #    groups = user.groups.all()
    #    index_list = ["experiments", "dataset", "datafile"]
    #    ms = MultiSearch(index=index_list)
    #    query_exp = Q("match", title=query_text)
    #    query_exp_oacl = Q("term", acls__entityId=user.id) | Q(
    #        "term", public_access=100
    #    )
    #    for group in groups:
    #        query_exp_oacl = query_exp_oacl | Q("term", acls__entityId=group.id)
    #    query_exp = query_exp & query_exp_oacl
    #    ms = ms.add(
    #        Search(index="experiments")
    #        .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
    #        .query(query_exp)
    #    )
    #    query_dataset = Q("match", description=query_text)
    #    query_dataset_oacl = Q("term", acls__entityId=user.id) | Q(
    #        "term", public_access=100
    #    )
    #    for group in groups:
    #        query_dataset_oacl = query_dataset_oacl | Q("term", acls__entityId=group.id)
    #    query_dataset = query_dataset & query_dataset_oacl
    #    ms = ms.add(
    #        Search(index="dataset")
    #        .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
    #        .query(query_dataset)
    #    )
    #    query_datafile = Q("match", filename=query_text)
    #    query_datafile_oacl = Q("term", acls__entityId=user.id) | Q(
    #        "term", public_access=100
    #    )
    #    for group in groups:
    #        query_datafile_oacl = query_datafile_oacl | Q(
    #            "term", acls__entityId=group.id
    #        )
    #    query_datafile = query_datafile & query_datafile_oacl
    #    ms = ms.add(
    #        Search(index="datafile")
    #        .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
    #        .query(query_datafile)
    #    )
    #    results = ms.execute()
    #    result_dict = {k: [] for k in ["experiments", "datasets", "datafiles"]}
    #    for item in results:
    #        for hit in item.hits.hits:
    #            if hit["_index"] == "dataset":
    #                result_dict["datasets"].append(hit.to_dict())
    #            elif hit["_index"] == "experiments":
    #                result_dict["experiments"].append(hit.to_dict())
    #            elif hit["_index"] == "datafile":
    #                result_dict["datafiles"].append(hit.to_dict())
    #    return [SearchObject(id=1, hits=result_dict)]
