'''
RESTful API for MyTardis search.
Implemented with Tastypie.

.. moduleauthor:: Manish Kumar <rishimanish123@gmail.com>
'''
import json
import datetime
import pytz

from django.conf import settings

from tastypie import fields
from tastypie.resources import Resource, Bundle
from tastypie.serializers import Serializer
from django_elasticsearch_dsl.search import Search
from elasticsearch_dsl import MultiSearch, Q
from django.template.defaultfilters import filesizeformat

from tardis.tardis_portal.api import default_authentication
from tardis.tardis_portal.auth import decorators as authz
from tardis.tardis_portal.models import (Project, Experiment, Dataset, DataFile,
                                         Instrument, ExperimentParameter,
                                         DatasetParameter, DatafileParameter,
                                         Schema, ParameterName)

import logging

LOCAL_TZ = pytz.timezone(settings.TIME_ZONE)
MAX_SEARCH_RESULTS = settings.MAX_SEARCH_RESULTS
MIN_CUTOFF_SCORE = settings.MIN_CUTOFF_SCORE

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


class SearchObject(object):
    def __init__(self, hits=None, id=None):
        self.hits = hits
        self.id = id


class SchemasObject(object):
    def __init__(self, schemas=None, id=None):
        self.schemas = schemas
        self.id = id


class SchemasAppResource(Resource):
    """Tastypie resource for schemas"""
    schemas = fields.ApiField(attribute='schemas', null=True)

    class Meta:
        resource_name = 'get-schemas'
        list_allowed_methods = ['get']
        serializer = default_serializer
        authentication = default_authentication
        object_class = SchemasObject
        always_return_data = True

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj['id']

        return kwargs

    def get_object_list(self, request):
        logging.warn("Testing search app: get schemas")
        if not request.user.is_authenticated:
            result_dict = {
                           "projects" : None,
                           "experiments" : None,
                           "datasets" : None,
                           "datafiles" : None
                           }
            return [SchemasObject(id=1, schemas=result_dict)]
        result_dict = {
                       "projects" : list(set(list(Project.safe.all(request.user
                                    ).prefetch_related('projectparameterset'
                                    ).values_list("projectparameterset__schema__id", flat=True)))),
                       "experiments" : list(set(list(Experiment.safe.all(request.user
                                       ).prefetch_related('projectparameterset'
                                       ).values_list("experimentparameterset__schema__id", flat=True)))),
                       "datasets" : list(set(list(Dataset.safe.all(request.user
                                       ).prefetch_related('projectparameterset'
                                       ).values_list("datasetparameterset__schema__id", flat=True)))),
                       "datafiles" : list(set(list(DataFile.safe.all(request.user
                                       ).prefetch_related('projectparameterset'
                                       ).values_list("datafileparameterset__schema__id", flat=True))))
                       }
        safe_dict = {}
        for key in result_dict:
            safe_dict[key] = {}
            for value in result_dict[key]:
                if value is not None:
                    schema_id = str(value)
                    schema_dict = {
                                   "id" : schema_id,
                                   "type" : key,
                                   "schema_name" : Schema.objects.get(id=value).name,
                                   "parameters": {}
                                   }
                    param_names = ParameterName.objects.filter(schema__id=value)
                    for param in param_names:
                        type_dict = {1:"NUMERIC",
                                     2:"STRING",
                                     3:"URL",
                                     4:"LINK",
                                     5:"FILENAME",
                                     6:"DATETIME",
                                     7:"LONGSTRING",
                                     8:"JSON"}
                        param_id = str(param.id)
                        param_dict = {
                                      "id" : param_id,
                                      "full_name": param.full_name,
                                      "data_type": type_dict[param.data_type]
                                      }
                        schema_dict["parameters"][param_id] = param_dict
                    safe_dict[key][schema_id] = schema_dict

        return [SchemasObject(id=1, schemas=safe_dict)]


    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)


class SearchAppResource(Resource):
    """Tastypie resource for simple-search"""
    hits = fields.ApiField(attribute='hits', null=True)

    class Meta:
        resource_name = 'simple-search'
        list_allowed_methods = ['post']
        serializer = default_serializer
        authentication = default_authentication
        object_class = SearchObject
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
        bundle = self.dehydrate(bundle)
        return bundle


    def dehydrate(self, bundle):
        logging.warn("Testing search app")
        user = bundle.request.user

        query_text = bundle.data.get('query', None)

        filters = bundle.data.get('filters', None)

        if not user.is_authenticated:
            result_dict = simple_search_public_data(query_text)
            return [SearchObject(id=1, hits=result_dict)]
        groups = user.groups.all()
        index_list = ['project', 'experiment', 'dataset', 'datafile']
        match_list = ['name','title','description','filename']
        filter_level = 0

        ms = MultiSearch(index=index_list)
        ms_sens = MultiSearch(index=index_list)

        for idx, obj in enumerate(index_list):

            # add user/group criteria to searchers
            query_obj = Q("term", objectacls__entityId=user.id) #| \Q("term", public_access=100)
            for group in groups:
                query_obj = query_obj | Q("term", objectacls__entityId=group.id)


            if query_text is not None:
                if query_text is not "":

                    # Search on title/keywords + on non-sensitive metadata
                    query_obj_text = Q({"match": {match_list[idx]:query_text}})
                    query_obj_text_meta = Q(
                        {"nested" : {
                            "path":"parameters", "query": Q(
                                {"bool": {"must":[
                                    Q({"match": {"parameters.value":query_text}}),
                                    Q({"match": {"parameters.sensitive":"False"}})
                                ]}}
                            )
                        }})
                    query_obj_text_meta = query_obj_text | query_obj_text_meta

                    # Search on sensitive metadata only
                    query_obj_sens_meta = Q(
                        {"nested" : {
                            "path":"parameters", "query": Q(
                                {"bool": {"must":[
                                    Q({"match": {"parameters.value":query_text}}),
                                    Q({"match": {"parameters.sensitive":"True"}})
                                ]}}
                            )
                        }})
                    query_obj_sens_meta = query_obj_text | query_obj_sens_meta

                    query_obj_sens = query_obj & query_obj_sens_meta
                    query_obj = query_obj & query_obj_text_meta


            if filters is not None:
                #filter_level = True
                #filter_op = filters['op']     This isn't used for now
                filterlist = filters["content"]
                for filter in filterlist:

                    # Expand this with more logic
                    operator_dict = {"is":"term", "contains":"match"}

                    # hack pass to ignore non-added logic
                    if operator_dict.get(filter['op'], None) is None:
                        continue

                    oper = operator_dict[filter['op']]

                    # Only filter type for now
                    if filter["kind"] == "schemaParameter":

                        schema_id, param_id = filter["target"][0], filter["target"][1]
                        num_2_type = {1:'experiment', 2:'dataset', 3:'datafile', 11:'project'}
                        hierarchy = {'project':4, 'experiment':3, 'dataset':2, 'datafile':1}

                        # check filter is applied to correct object type
                        if num_2_type[Schema.objects.get(id=schema_id).schema_type] == obj:
                            if filter_level < hierarchy[obj]:
                                filter_level = hierarchy[obj]
                            # check if filter query is list of options, or single value
                            # (elasticsearch can actually handle delimiters in a single string...)
                            if isinstance(filter["content"], list):

                                Qdict = {"should" : []}

                                for option in filter["content"]:

                                    qry = Q(
                                        {"nested" : {
                                            "path":"parameters", "query": Q(
                                                {"bool": {"must":[
                                                    Q({"match": {"parameters.pn_id":str(param_id)}}),
                                                    Q({"match": {"parameters.value":option}})
                                                ]}}
                                            )
                                        }})

                                    Qdict["should"].append(qry)

                                query_obj_filt = Q({"bool" : Qdict})

                            else:
                                query_obj_filt = Q(
                                    {"nested" : {
                                        "path":"parameters", "query": Q(
                                            {"bool": {"must":[
                                                Q({"match": {"parameters.pn_id":str(param_id)}}),
                                                Q({"match": {"parameters.value":filter["content"]}})
                                            ]}}
                                        )
                                    }})


                            query_obj = query_obj & query_obj_filt
                            if query_text is not None:
                                if query_text is not "":
                                    query_obj_sens = query_obj_sens & query_obj_filt


            ms = ms.add(Search(index=obj)
                        .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
                        .query(query_obj))

            if query_text is not None:
                if query_text is not "":
                    ms_sens = ms_sens.add(Search(index=obj)
                                     .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
                                     .query(query_obj_sens))

        results = ms.execute()
        if query_text is not None:
            if query_text is not "":
                results_sens = ms_sens.execute()

        result_dict = {k: [] for k in ["projects", "experiments", "datasets", "datafiles"]}

        def clean_response(request, results, result_dict, sensitive=False):
            for item in results:
                for hit in item.hits.hits:

                    # Prevents search hits based purely upon sensitive metadata matches,
                    # for users/groups who do not have sensitive permission
                    if sensitive:
                        if not authz.has_sensitive_access(request, hit["_source"]["id"], hit["_index"]):
                            continue

                    # Default sensitive permission and size of object
                    sensitive_bool = False
                    size = 0

                    # Skip hit if hit_obj not accessible (elasticsearch checks for ACL entry for user/group,
                    # not whether the entry gives or prevents access)
                    if not authz.has_access(request, hit["_source"]["id"], hit["_index"]):
                        continue

                    # If user/group has sensitive permission, update flag
                    if authz.has_sensitive_access(request, hit["_source"]["id"], hit["_index"]):
                        sensitive_bool = True

                    # Get total/nested size of object, respecting ACL access to child objects
                    size = authz.get_nested_size(request, hit["_source"]["id"], hit["_index"])

                    # Must work on copy of current iterable
                    safe_hit = hit.copy()

                    # Remove ACLs and add size to repsonse
                    safe_hit["_source"].pop("objectacls")
                    safe_hit["_source"]["size"] = filesizeformat(size)

                    # Get count of all nested objects and download status
                    if hit["_index"] != 'datafile':
                        safe_hit["_source"]["counts"] = authz.get_nested_count(request,
                                                            hit["_source"]["id"], hit["_index"])

                        safe_hit["_source"]["userDownloadRights"] = authz.get_nested_has_download(request,
                                                            hit["_source"]["id"], hit["_index"])

                    else:
                        if authz.has_download_access(request, hit["_source"]["id"],
                                                     hit["_index"]):
                            safe_hit["_source"]["userDownloadRights"] = "full"
                        else:
                            safe_hit["_source"]["userDownloadRights"] = "none"

                    # if no sensitive access, remove sensitive metadata from response
                    if not sensitive_bool:
                        for idxx, parameter in enumerate(hit["_source"]["parameters"]):
                            is_sensitive = authz.get_obj_parameter(parameter["pn_id"],
                                              hit["_source"]["id"], hit["_index"])

                            if is_sensitive.sensitive_metadata:
                                safe_hit["_source"]["parameters"].pop(idxx)

                    # Append hit to final results if not already in results.
                    # Due to non-identical scores in hits for non-sensitive vs sensitive search,
                    # we require a more complex comparison than just 'is in' as hits are not identical
                    if safe_hit["_source"]['id'] not in [objj["_source"]['id'] for objj in result_dict[hit["_index"]+"s"]]:
                        result_dict[hit["_index"]+"s"].append(safe_hit)


        def filter_parent_child(result_dict, filter_level):

            # Define parent_type for experiment/datafile (N/A for project, hardcoded for dataset)
            parent_child = {"experiment":"project", "datafile":"dataset"}

            # Define hierarchy of types for filter levels
            hierarchy = {"experiments":3, "datasets":2, "datafiles":1}
            for objs in ["experiments", "datasets", "datafiles"]:
                if hierarchy[objs] < filter_level:
                    for obj_idx, obj in reversed(list(enumerate(result_dict[objs]))):
                        if obj["_index"] != 'dataset':
                            if obj["_source"][parent_child[obj["_index"]]]["id"] not in [objj["_source"]['id'] \
                                    for objj in result_dict[parent_child[obj["_index"]]+"s"]]:
                                result_dict[objs].pop(obj_idx)
                        else:
                            exp_ids = [parent['id'] for parent in obj["_source"]["experiments"]]
                            if not any(item in exp_ids for item in [objj["_source"]['id'] for objj in result_dict["experiments"]]):
                                result_dict[objs].pop(obj_idx)


        clean_response(bundle.request, results, result_dict)
        if query_text is not None:
            if query_text is not "":
                clean_response(bundle.request, results_sens, result_dict, sensitive=True)

        if filter_level:
            filter_parent_child(result_dict, filter_level)

        # add search results to bundle, and return bundle
        bundle.obj = SearchObject(id=1, hits=result_dict)
        return bundle


# WARNING: This is busted
def simple_search_public_data(query_text):
    result_dict = {k: [] for k in ["experiments", "datasets", "datafiles"]}
    index_list = ['experiment', 'dataset', 'datafile']
    ms = MultiSearch(index=index_list)
    query_exp = Q("match", title=query_text)
    query_exp_oacl = Q("term", public_access=100)
    query_exp = query_exp & query_exp_oacl
    ms = ms.add(Search(index='experiment')
                .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE)
                .query(query_exp))
    query_dataset = Q("match", description=query_text)
    query_dataset = query_dataset | Q("match", tags=query_text)
    query_dataset_oacl = Q("term", **{'experiment.public_access': 100})
    ms = ms.add(Search(index='dataset')
                .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE).query(query_dataset)
                .query('nested', path='experiment', query=query_dataset_oacl))
    query_datafile = Q("match", filename=query_text)
    query_datafile_oacl = Q("term", **{'dataset.experiment.public_access': 100})
    ms = ms.add(Search(index='datafile')
                .extra(size=MAX_SEARCH_RESULTS, min_score=MIN_CUTOFF_SCORE).query(query_datafile)
                .query('nested', path='dataset.experiment', query=query_datafile_oacl))
    results = ms.execute()
    for item in results:
        for hit in item.hits.hits:
            safe_hit = hit.copy()
            safe_hit["_source"].pop("objectacls")
            result_dict[hit["_index"]+'s'].append(safe_hit)

    return result_dict
