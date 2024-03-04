"""
helper functions used in api.py
"""

from datetime import datetime

from django.template.defaultfilters import filesizeformat
from elasticsearch_dsl import Q

from tardis.tardis_portal.models import (
    Schema,
)


def cleaning_results(results, result_dict, preloaded, datafiles_dl):
    """
    Filter out and clean search result hits based on a number of critera.
    """

    for item in results:
        for hit_attrdict in item.hits.hits:
            hit = hit_attrdict.to_dict()

            # Check to see if indexed object actually exists in DB, if not then skip
            if int(hit["_source"]["id"]) not in preloaded[hit["_index"]]["objects"]:
                continue

            # Default sensitive permission and size of object
            sensitive_bool = False
            size = 0
            # If user/group has sensitive permission, update flag
            if hit["_source"]["id"] in preloaded[hit["_index"]]["sens_list"]:
                sensitive_bool = True
            # Re-package parameters into single parameter list
            param_list = []
            if "string" in hit["_source"]["parameters"]:
                param_list.extend(hit["_source"]["parameters"]["string"])
            if "numerical" in hit["_source"]["parameters"]:
                param_list.extend(hit["_source"]["parameters"]["numerical"])
            if "datetime" in hit["_source"]["parameters"]:
                param_list.extend(hit["_source"]["parameters"]["datetime"])
            hit["_source"]["parameters"] = param_list
            # Remove unused fields to reduce data sent to front-end
            hit.pop("_score")
            hit.pop("_id")
            # hit.pop("_type")
            hit.pop("sort")

            # Get count of all nested objects and download status
            if hit["_index"] == "datafile":
                if hit["_source"]["id"] in datafiles_dl:
                    hit["_source"]["userDownloadRights"] = "full"
                    size = hit["_source"]["size"]
                else:
                    hit["_source"]["userDownloadRights"] = "none"

            else:
                safe_nested_dfs_set = {*preloaded["datafile"]["objects"]}.intersection(
                    preloaded[hit["_index"]]["objects"][hit["_source"]["id"]]["dfs"]
                )
                safe_nested_dfs_count = len(safe_nested_dfs_set)
                if hit["_index"] in {"project", "experiment"}:
                    safe_nested_set = len(
                        {*preloaded["dataset"]["objects"]}.intersection(
                            preloaded[hit["_index"]]["objects"][hit["_source"]["id"]][
                                "sets"
                            ]
                        )
                    )
                # Ugly hack, should do a nicer, less verbose loop+type detection
                if hit["_index"] == "project":
                    safe_nested_exp = len(
                        {*preloaded["experiment"]["objects"]}.intersection(
                            preloaded[hit["_index"]]["objects"][hit["_source"]["id"]][
                                "exps"
                            ]
                        )
                    )
                    hit["_source"]["counts"] = {
                        "experiments": safe_nested_exp,
                        "datasets": safe_nested_set,
                        "datafiles": (safe_nested_dfs_count),
                    }
                if hit["_index"] == "experiment":
                    hit["_source"]["counts"] = {
                        "datasets": safe_nested_set,
                        "datafiles": safe_nested_dfs_count,
                    }
                if hit["_index"] == "dataset":
                    hit["_source"]["counts"] = {"datafiles": safe_nested_dfs_count}
                # Get downloadable datafiles ultimately belonging to this "hit" object
                # and calculate the total size of these files
                safe_nested_dfs_dl = [*safe_nested_dfs_set.intersection(datafiles_dl)]
                size = sum(
                    (
                        preloaded["datafile"]["objects"][id]["size"]
                        for id in safe_nested_dfs_dl
                    )
                )
                # Determine the download state of the "hit" object
                # safe_nested_dfs_dl_bool = [id in datafiles_dl for id in safe_nested_dfs]
                if safe_nested_dfs_set.issubset(datafiles_dl):
                    hit["_source"]["userDownloadRights"] = "full"
                elif safe_nested_dfs_set.intersection(datafiles_dl):
                    hit["_source"]["userDownloadRights"] = "partial"
                else:
                    hit["_source"]["userDownloadRights"] = "none"

            hit["_source"]["size"] = filesizeformat(size)

            # if no sensitive access, remove sensitive metadata from response
            for idxx, parameter in reversed([*enumerate(hit["_source"]["parameters"])]):
                if not sensitive_bool:
                    if parameter["sensitive"]:
                        hit["_source"]["parameters"].pop(idxx)
                    else:
                        hit["_source"]["parameters"][idxx].pop("sensitive")
                else:
                    if not parameter["sensitive"]:
                        hit["_source"]["parameters"][idxx].pop("sensitive")

            # Append hit to results if not already in results.
            # Due to non-identical scores in hits for non-sensitive vs sensitive search,
            # we require a more complex comparison than just 'is in' as hits are not identical
            result_dict[hit["_index"]].append(hit)
    return result_dict


def cleaning_parent_filter(results, filter_level):
    """
    filter out hits results based upon level of parent filtering
    """

    # Define parent_type for experiment/datafile
    # (N/A for project, hardcoded for dataset)
    parent_child = {"experiment": "projects", "dataset": "experiments"}
    # Define hierarchy of types for filter levels
    hierarch = [3, 2, 1]  # {"experiments":3, "datasets":2, "datafiles":1}
    for idx, item in enumerate(results[1:]):
        # if active filter level higher than current object type:
        # apply "parent-in-result" filter
        if hierarch[idx] < filter_level:
            parent_ids = [objj["_source"]["id"] for objj in results[idx].hits.hits]
            parent_ids_set = {*parent_ids}

            for obj_idx, obj in reversed([*enumerate(item.hits.hits)]):
                if obj["_index"] != "datafile":
                    parent_es_ids = [
                        parent["id"]
                        for parent in obj["_source"][parent_child[obj["_index"]]]
                    ]
                    if not any(itemm in parent_es_ids for itemm in parent_ids):
                        results[idx + 1].hits.hits.pop(obj_idx)
                else:
                    if (
                        obj["_source"]["dataset"]["id"] not in parent_ids_set
                    ):  # parent object is idx-1, but idx in enumerate
                        # is already shifted by -1, so straight idx
                        results[idx + 1].hits.hits.pop(obj_idx)
    return results


def cleaning_preload(preloaded, projects, experiments, datasets, datafiles):
    """
    Populate the preload dictionary with IDs and child IDs of search results.
    """

    # Probably a cleaner/simpler way to do this, but hey ho!
    for otype, id_list in {
        "project": projects,
        "experiment": experiments,
        "dataset": datasets,
        "datafile": datafiles,
    }.items():
        # iterate over objects in list - each list element has the obj_id
        # followed by separated lists of any children objects
        for ids in id_list:
            # extract object ID
            obj_id = ids[0]
            # Check if the ID already exists in preloaded dict
            if obj_id in preloaded[otype]["objects"]:
                # add nested children to the dict
                # Note: Datafiles don't have children so only in the else clause
                if otype == "dataset":
                    preloaded[otype]["objects"][obj_id]["dfs"].add(ids[1])
                elif otype == "experiment":
                    preloaded[otype]["objects"][obj_id]["sets"].add(ids[1])
                    preloaded[otype]["objects"][obj_id]["dfs"].add(ids[2])
                elif otype == "project":
                    preloaded[otype]["objects"][obj_id]["exps"].add(ids[1])
                    preloaded[otype]["objects"][obj_id]["sets"].add(ids[2])
                    preloaded[otype]["objects"][obj_id]["dfs"].add(ids[3])
            else:
                # create the new dict for the object and populate with
                # children (proj/exp/set) or datafile size (datafile)
                new_dict = {}
                if otype == "datafile":
                    new_dict["size"] = ids[1]
                elif otype == "dataset":
                    new_dict["dfs"] = {ids[1]}
                elif otype == "experiment":
                    new_dict["sets"] = {ids[1]}
                    new_dict["dfs"] = {ids[2]}
                elif otype == "project":
                    new_dict["exps"] = {ids[1]}
                    new_dict["sets"] = {ids[2]}
                    new_dict["dfs"] = {ids[3]}
                # assign new dict to preloaded dict
                preloaded[otype]["objects"][obj_id] = new_dict
    return preloaded


def cleaning_ids(user, groups, objtype):
    """
    Function to build up generic object queries to get ID information
    on objects, and specifically also the size of Datafiles.
    """

    if objtype == "project":
        prefetch_fields = [
            "project__experiments",
            "project__experiments__datasets",
            "project__experiments__datasets__datafile",
        ]
        value_fields = [field + "__id" for field in prefetch_fields]

    if objtype == "experiment":
        prefetch_fields = [
            "experiment__datasets",
            "experiment__datasets__datafile",
        ]
        value_fields = [field + "__id" for field in prefetch_fields]

    if objtype == "dataset":
        prefetch_fields = [
            "dataset__datafile",
        ]
        value_fields = [field + "__id" for field in prefetch_fields]

    if objtype == "datafile":
        prefetch_fields = None
        value_fields = ["datafile__size"]

    id_list = cleaning_acls(
        user,
        groups,
        objtype,
        prefetch_fields=prefetch_fields,
        value_fields=value_fields,
        flat=False,
    )
    return id_list


def cleaning_acls(
    user,
    groups,
    objtype,
    canSensitive=False,
    canDownload=False,
    prefetch_fields=None,
    values_list=None,
    flat=True,
):
    """
    Function to build up generic object queries to get ACL or ID information
    on objects.
    """
    if objtype == "project":
        entity = user.projectacls
    if objtype == "experiment":
        entity = user.experimentacls
    if objtype == "dataset":
        entity = user.datasetacls
    if objtype == "datafile":
        entity = user.datafileacls

    query = cleaning_acl_query(
        entity,
        objtype,
        canSensitive=canSensitive,
        canDownload=canDownload,
        prefetch_fields=prefetch_fields,
        values_list=values_list,
        flat=flat,
    )
    for group in groups:

        if objtype == "project":
            entity = group.projectacls
        if objtype == "experiment":
            entity = group.experimentacls
        if objtype == "dataset":
            entity = group.datasetacls
        if objtype == "datafile":
            entity = group.datafileacls

        query |= cleaning_acl_query(
            entity,
            objtype,
            canSensitive=canSensitive,
            canDownload=canDownload,
            prefetch_fields=prefetch_fields,
            values_list=values_list,
            flat=flat,
        )
    return [*query.distinct()]


def cleaning_acl_query(
    entity_acls,
    objtype,
    canSensitive=False,
    canDownload=False,
    prefetch_fields=None,
    values_list=None,
    flat=True,
):
    """
    Function to build up generic object queries to get ACL or ID information
    on objects.
    """
    # build query on object and related ACLs
    query = entity_acls.select_related(objtype)

    # apply specific ACL perm filter
    if canSensitive == True:
        query = query.filter(canSensitive=True)
    if canDownload == True:
        query = query.filter(canSensitive=True)

    # if prefetch_fields are specified, add prefetch to query
    if prefetch_fields is not None:
        query = query.prefetch_related(*prefetch_fields)

    # exclude too-new/expired ACLs
    query = query.exclude(
        effectiveDate__gte=datetime.today(),
        expiryDate__lte=datetime.today(),
    )

    # add OBJ__id to values_list return
    value_list_to_add = [objtype + "__id"]
    # if list of extra values_list specified, add them to query
    if values_list is not None:
        value_list_to_add.extend(*values_list)

    return query.values_list(*value_list_to_add, flat=flat)


def query_add_sorting(request_sorting, obj, sort_dict):
    """
    Function to build up sorting filters that need to be applied to
    a search query
    """
    # make sure sorting request contains info
    if request_sorting is not None:
        # check if current object/model is in sorting request
        if obj in request_sorting:
            # iterate over sort options
            for sort in request_sorting[obj]:

                # process nested sort filters
                if len(sort["field"]) > 1:
                    # if in this dict then field adds .raw to end of sort
                    if sort["field"][-1] in {
                        "fullname",
                        "name",
                        "title",
                        "description",
                        "filename",
                    }:
                        search_field = ".".join(sort["field"]) + ".raw"
                    else:
                        search_field = ".".join(sort["field"])
                    # build up sorting dict options
                    sort_dict[search_field] = {
                        "order": sort["order"],
                        "nested_path": ".".join(sort["field"][:-1]),
                    }
                # process non-nested sort filters
                if len(sort["field"]) == 1:
                    # these fields need to have .raw added to them
                    if sort["field"][0] in {
                        "principal_investigator",
                        "name",
                        "title",
                        "description",
                        "filename",
                    }:
                        sort_dict[sort["field"][0] + ".raw"] = {"order": sort["order"]}
                    # size field needs specific handling
                    elif sort["field"][0] == "size":
                        # for datafile size is easy to calculate
                        if obj == "datafile":
                            sort_dict[sort["field"][0]] = {"order": sort["order"]}
                        # for parent models we need ACL context for this,
                        # which is currently not available in ES.
                        else:
                            # DO THIS SORTING AFTER ELASTICSEARCH
                            pass
                    else:
                        sort_dict[sort["field"][0]] = {"order": sort["order"]}
    return sort_dict


def Q_nested(path, query):
    """wrapper function for readability of nested ES Queries"""
    query = Q({"nested": {"path": path, "query": query}})
    return query


def Q_must(query_list):
    """wrapper function for readability of must ES Queries"""
    query = Q({"bool": {"must": query_list}})
    return query


def create_user_and_group_query(user, groups):
    """
    This function creates an initial search query object and requires that
    any results must have an appropriate User OR Group ACL for a user + any
    of their groups.
    """
    # query where ACL must match entityId=User.id and pluginId=django_user
    query_obj = Q_nested(
        path="acls",
        query=Q_must(
            query_list=[
                Q({"match": {"acls.entityId": user.id}}),
                Q({"term": {"acls.pluginId": "django_user"}}),
            ]
        ),
    )
    # queries where ACL must match entityId=group.id and pluginId=django_group
    for group in groups:
        query_obj_group = Q_nested(
            path="acls",
            query=Q_must(
                query_list=[
                    Q({"match": {"acls.entityId": group.id}}),
                    Q({"term": {"acls.pluginId": "django_group"}}),
                ]
            ),
        )
        # add each group query as an OR to existing query
        query_obj = query_obj | query_obj_group
    return query_obj


def query_keywords_and_metadata(query_obj, query_text, object_type, idx, title_list):
    """
    This function takes an existing search query and adds matches for
    keywords or non-sensitive metadata fields.
    """
    # query where object "title" must match query_text for given object
    query_obj_text = Q({"match": {title_list[idx]: query_text[object_type]}})
    # query where non-sensitive parameters of object must match query_text for given object
    query_obj_text_meta = Q_nested(
        path="parameters.string",
        query=Q_must(
            query_list=[
                Q({"match": {"parameters.string.value": query_text[object_type]}}),
                Q({"term": {"parameters.string.sensitive": False}}),
            ]
        ),
    )
    # stack up query by matching "title" OR "non-sensitive metadata"
    query_obj_text_meta = query_obj_text | query_obj_text_meta
    # stack keyword+metadata query with existing query via AND (we expect it's the user/group query)
    query_obj = query_obj & query_obj_text_meta
    return query_obj


def _query_filter_on_parameters_type(ptype, param_id, oper, value):
    """
    This function is a generic handler to build an individual parameter query. It deals with
    the following types of metadata: "string", "numerical", "datetime".
    """

    # cast the type field into the correct spelling for object document structure
    type_mapping = {"STRING": "string", "NUMERIC": "numerical", "DATETIME": "datetime"}
    ptype = type_mapping[ptype]

    # tweak the operators and value structure based up parameter type
    if ptype == "string":
        base_oper = oper
        query_val = value

    elif ptype in ["numerical", "datetime"]:
        base_oper = "range"
        query_val = {oper: value}

    # create and return query on parameter using provided inputs
    query_obj = Q_nested(
        path="parameters." + ptype,
        query=Q_must(
            query_list=[
                Q({"match": {"parameters." + ptype + ".pn_id": str(param_id)}}),
                Q({base_oper: {"parameters." + ptype + ".value": query_val}}),
                Q({"term": {"parameters." + ptype + ".sensitive": False}}),
            ]
        ),
    )
    return query_obj


def _query_filter_on_parameters(query_obj, filter, obj, filter_level, hierarchy, oper):
    """
    This function is a component of the more general "query_apply_filters" function.
    Here we build up queries on Schema-parameter / metadata filters.
    """

    # Hardcode of Schema types+numbers here
    num_2_type = {
        1: "experiment",
        2: "dataset",
        3: "datafile",
        6: "project",
    }

    # extract schema + parameter id from API request
    schema_id, param_id = filter["target"][0], filter["target"][1]

    # check filter is applied to correct object type
    if num_2_type[Schema.objects.get(id=schema_id).type] == obj:
        # redefine "parent-in-results" threshold if required
        if filter_level < hierarchy[obj]:
            filter_level = hierarchy[obj]

        # check if filter query is list of options or a single value
        # (elasticsearch can actually handle delimiters in a single string...)
        if isinstance(filter["content"], list):
            # if filter is a list, create an "OR" operator list of search queries
            # and pass each value individually to build "OR" query
            Qdict = {"should": []}
            for option in filter["content"]:
                query = _query_filter_on_parameters_type(
                    filter["type"], param_id, oper, option
                )
                Qdict["should"].append(query)
            # final "OR" query is built up from the individual ones
            query_obj_filt = Q({"bool": Qdict})

        else:
            # if filter content not a list of options then pass filter content
            # directly as the value to search on
            query_obj_filt = _query_filter_on_parameters_type(
                filter["type"], param_id, oper, filter["content"]
            )

        # as before, combine filter query with existing query
        query_obj = query_obj & query_obj_filt

        # return both the query_obj and the filter level variable
        return query_obj, filter_level


def _query_filter_on_intrinsic_schemas(query_obj, filter, oper):
    """
    This function is applies "filter by schema" to a search query.
    """
    # check if filter query is list of options, or single value
    if isinstance(filter["content"], list):
        # If its a list of filters, build up several queries and combine them with OR
        Qdict = {"should": []}
        for option in filter["content"]:
            qry = Q_nested(
                path="parameters.schemas",
                query=Q({oper: {"parameters.schemas.schema_id": option}}),
            )
            Qdict["should"].append(qry)
        query_obj_filt = Q({"bool": Qdict})
    else:
        # if its a single filter, just create one query
        query_obj_filt = Q_nested(
            path="parameters.schemas",
            query=Q({oper: {"parameters.schemas.schema_id": filter["content"]}}),
        )

    # combine this filter with the existing query and return it
    query_obj = query_obj & query_obj_filt
    return query_obj


def _query_filter_on_intrinsic_fields(query_obj, filter, oper, target_fieldtype):
    """
    This function is applies "filter by intrinsic object fields" to a search query.
    It separates the fields into two groups: "string" fields and "datetime" fields.
    String fields: name, description, title, tags, filename, file_extension
    Datetime fields: created_time, start_time, end_time
    """

    # if the filter type is on a string field
    if filter["type"] == "STRING":
        # string filters can be comma separated lists, so check for list or single
        if isinstance(filter["content"], list):
            # if filter is a list, build individual queries for each filter and combine
            # using an "OR"
            Qdict = {"should": []}
            for option in filter["content"]:
                # Special treatment for file extension to remove leading fullstops
                if target_fieldtype == "file_extension":
                    if option[0] == ".":
                        option = option[1:]
                # add individual query to list of query components
                qry = Q({oper: {target_fieldtype: option}})
                Qdict["should"].append(qry)
            # build final query from individual components
            query_obj_filt = Q({"bool": Qdict})
        else:
            # Special treatment for file extension to remove leading fullstops
            if target_fieldtype == "file_extension":
                if filter["content"][0] == ".":
                    filter["content"] = filter["content"][1:]
            # simply build the filter query
            query_obj_filt = Q({oper: {target_fieldtype: filter["content"]}})
    # if the filter type is a datetime field
    elif filter["type"] == "DATETIME":
        # simply build the single query
        query_obj_filt = Q({"range": {target_fieldtype: {oper: filter["content"]}}})
    # combine the filter query with existing search query and return it
    query_obj = query_obj & query_obj_filt
    return query_obj


def _query_filter_relations_builder(target_fieldtype, oper, nested_fieldtype, option):
    """
    This function is a generic query builder for the relational filter queries.
    """
    # rest_list
    query_obj = Q_nested(
        path=target_fieldtype,
        query=Q(
            {
                oper: {
                    ".".join(
                        [
                            target_fieldtype,
                            nested_fieldtype,
                        ]
                    ): option
                }
            }
        ),
    )

    return query_obj


def _query_filter_on_intrinsic_relations(query_obj, filter, oper, target_fieldtype):
    """
    This function is applies "filter by intrinsic relations" to a search query.
    This includes the following relational fields (and the object on which it acts):
     - principal_investigator (Project),
     - projects (Experiment),
     - instrument (Dataset),
     - institution (Project),
     - experiments (Dataset),
     - dataset (Datafile),
    """

    # extract the the nested field type from filter
    nested_fieldtype = filter["target"][2]
    # determine if filter is a list of filters or individual search term
    if isinstance(filter["content"], list):
        Qdict = {"should": []}
        # iterate over options and bu8ild individual queries to combine with "OR"
        for option in filter["content"]:
            qry = _query_filter_relations_builder(
                target_fieldtype, oper, nested_fieldtype, option
            )
            Qdict["should"].append(qry)
        # build final query out of individual components
        query_obj_filt = Q({"bool": Qdict})
    else:
        # if individual search term, simply build it
        query_obj_filt = _query_filter_relations_builder(
            target_fieldtype, oper, nested_fieldtype, filter["content"]
        )
    # Special handling for list of principal investigators
    if target_fieldtype == "principal_investigator":
        # principal investigator builds on existing intrinsic relation query!
        Qdict_lr = {"should": [query_obj_filt]}
        # determine if filter is a list of filters or individual search term
        if isinstance(filter["content"], list):
            Qdict = {"should": []}
            # iterate over options and bu8ild individual queries to combine with "OR"
            for option in filter["content"]:
                qry = _query_filter_relations_builder(
                    target_fieldtype, "term", "username", option
                )
                Qdict["should"].append(qry)
            # build final query out of individual components
            query_obj_filt = Q({"bool": Qdict})
        else:
            # if individual search term, simply build it
            query_obj_filt = _query_filter_relations_builder(
                target_fieldtype, "term", "username", filter["content"]
            )
        # build special "OR" query for principal_investigator search
        Qdict_lr["should"].append(query_obj_filt)
        query_obj_filt = Q({"bool": Qdict_lr})
    # combine intrinsic relation filter with existing search query and return
    query_obj = query_obj & query_obj_filt
    return query_obj


def _query_filter_on_intrinsics(query_obj, filter, obj, filter_level, hierarchy, oper):
    """
    This function is a component of the more general "query_apply_filters" function.
    Here we build up queries on intrinsic filters such as filter by Schema, filter by object
    properties, filter by related object properties.
    """

    # Extract out the filter object type and the filter field/variable name
    target_objtype, target_fieldtype = (
        filter["target"][0],
        filter["target"][1],
    )

    # Of course, only process filter if it's the right object for this object search
    if target_objtype == obj:
        # Update the heirarchy level at which the
        # "parent-in-results" criteria must be applied
        if filter_level < hierarchy[obj]:
            filter_level = hierarchy[obj]

        # Apply "Selected Schema" filter
        if target_fieldtype == "schema":
            query_obj = _query_filter_on_intrinsic_schemas(query_obj, filter, oper)

        # Apply filters that act on fields which are intrinsic to the object (Proj,exp,set,file)
        if target_fieldtype in {
            "name",
            "description",
            "title",
            "tags",
            "filename",
            "file_extension",
            "created_time",
            "start_time",
            "end_time",
        }:
            query_obj = _query_filter_on_intrinsic_fields(
                query_obj, filter, oper, target_fieldtype
            )

        # Apply filters that act on fields which are intrinsic to related objects (instruments, users, etc)
        if target_fieldtype in {
            "principal_investigator",
            "projects",
            "instrument",
            "institution",
            "experiments",
            "dataset",
        }:

            query_obj = _query_filter_on_intrinsic_relations(
                query_obj, filter, oper, target_fieldtype
            )

    # return function-updated query_obj, and filter_level
    return query_obj, filter_level


def query_apply_filters(query_obj, filters, obj, filter_level, hierarchy):
    """
    This function takes an existing search query and adds matches for
    the various filters on metadata that can be applied.
    """

    # combination logic of filters can theoretically be applied, but not supported yet.
    # filter_op = filters['op']     This isn't used for now

    filterlist = filters["content"]

    # Define operator translations between API and ES
    operator_dict = {
        "is": "term",
        "contains": "match",
        ">=": "gte",
        "<=": "lte",
    }

    # Iterate over filters in request
    for filter in filterlist:

        # Extract required operator for filter
        oper = operator_dict[filter["op"]]

        # Apply Schema-parameter / metadata filters to search
        if filter["kind"] == "schemaParameter":
            query_obj, filter_level = _query_filter_on_parameters(
                query_obj, filter, obj, filter_level, hierarchy, oper
            )

        # Apply intrinsic object filters to search
        if filter["kind"] == "typeAttribute":
            query_obj, filter_level = _query_filter_on_intrinsics(
                query_obj, filter, obj, filter_level, hierarchy, oper
            )

    return query_obj, filter_level
