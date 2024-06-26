"""
views to do with metadata, parameters etc. Mostly ajax page inclusions
"""

import logging

from django.contrib.auth.decorators import login_required

from ..auth import decorators as authz
from ..forms import (
    create_parameter_add_form,
    create_parameterset_edit_form,
    save_parameter_add_form,
    save_parameter_edit_form,
)
from ..models import (
    DataFile,
    DatafileParameterSet,
    Dataset,
    DatasetParameterSet,
    Experiment,
    ExperimentParameterSet,
    ParameterName,
    Schema,
)
from ..shortcuts import render_response_index, return_response_error
from ..views.utils import remove_csrf_token

logger = logging.getLogger(__name__)


@login_required
def edit_experiment_par(request, parameterset_id):
    parameterset = ExperimentParameterSet.objects.get(id=parameterset_id)
    if authz.has_write(request, parameterset.experiment.id, "experiment"):
        view_sensitive = authz.has_sensitive_access(
            request, parameterset.experiment.id, "experiment"
        )
        return edit_parameters(
            request, parameterset, otype="experiment", view_sensitive=view_sensitive
        )
    return return_response_error(request)


@login_required
def edit_dataset_par(request, parameterset_id):
    parameterset = DatasetParameterSet.objects.get(id=parameterset_id)
    if authz.has_write(request, parameterset.dataset.id, "dataset"):
        view_sensitive = authz.has_sensitive_access(
            request, parameterset.dataset.id, "dataset"
        )
        return edit_parameters(
            request, parameterset, otype="dataset", view_sensitive=view_sensitive
        )
    return return_response_error(request)


@login_required
def edit_datafile_par(request, parameterset_id):
    parameterset = DatafileParameterSet.objects.get(id=parameterset_id)
    if authz.has_write(request, parameterset.datafile.id, "datafile"):
        view_sensitive = authz.has_sensitive_access(
            request, parameterset.datafile.id, "datafile"
        )
        return edit_parameters(
            request, parameterset, otype="datafile", view_sensitive=view_sensitive
        )
    return return_response_error(request)


def edit_parameters(request, parameterset, otype, view_sensitive=False):
    parameternames = ParameterName.objects.filter(
        schema__namespace=parameterset.schema.namespace
    )
    for parameter in parameterset.parameters:
        parameternames = parameternames.exclude(id=parameter.name.id)

    success = False
    valid = True

    if request.method == "POST":
        request = remove_csrf_token(request)

        class DynamicForm(
            create_parameterset_edit_form(parameterset, request, post=True)
        ):
            pass

        form = DynamicForm(request.POST)

        if form.is_valid():
            save_parameter_edit_form(
                parameterset, request, view_sensitive=view_sensitive
            )

            success = True
        else:
            valid = False

    else:

        class DynamicForm(
            create_parameterset_edit_form(
                parameterset, request, view_sensitive=view_sensitive
            )
        ):
            pass

        form = DynamicForm()

    # this prefix is added to urls if otype = project
    # workaround for separate app using communal function
    project_url = ""
    if otype == "project":
        project_url = "/project"

    c = {
        "schema": parameterset.schema,
        "form": form,
        "parameternames": parameternames,
        "type": otype,
        "success": success,
        "parameterset_id": parameterset.id,
        "valid": valid,
        "prefix": project_url,
        #'can_view_sensitive': view_sensitive,
    }

    return render_response_index(request, "tardis_portal/ajax/parameteredit.html", c)


@login_required
def add_datafile_par(request, datafile_id):
    parentObject = DataFile.objects.get(id=datafile_id)
    if authz.has_write(request, parentObject.id, "datafile"):
        return add_par(request, parentObject, otype="datafile", stype=Schema.DATAFILE)
    return return_response_error(request)


@login_required
def add_dataset_par(request, dataset_id):
    parentObject = Dataset.objects.get(id=dataset_id)
    if authz.has_write(request, parentObject.id, "dataset"):
        return add_par(request, parentObject, otype="dataset", stype=Schema.DATASET)
    return return_response_error(request)


@login_required
def add_experiment_par(request, experiment_id):
    parentObject = Experiment.objects.get(id=experiment_id)
    if authz.has_write(request, parentObject.id, "experiment"):
        return add_par(
            request, parentObject, otype="experiment", stype=Schema.EXPERIMENT
        )
    return return_response_error(request)


def add_par(request, parentObject, otype, stype):
    all_schema = Schema.objects.filter(type=stype, immutable=False)

    if "schema_id" in request.GET:
        schema_id = request.GET["schema_id"]
    elif all_schema.count() > 0:
        schema_id = all_schema[0].id
    else:
        return render_response_index(
            request, "tardis_portal/ajax/parameter_set_unavailable.html", {}
        )

    schema = Schema.objects.get(id=schema_id)

    parameternames = ParameterName.objects.filter(schema__namespace=schema.namespace)

    success = False
    valid = True

    if request.method == "POST":
        request = remove_csrf_token(request)

        class DynamicForm(
            create_parameter_add_form(schema.namespace, parentObject, request=request)
        ):
            pass

        form = DynamicForm(request.POST)

        if form.is_valid():
            save_parameter_add_form(schema.namespace, parentObject, request)

            success = True
        else:
            valid = False

    else:

        class DynamicForm(create_parameter_add_form(schema.namespace, parentObject)):
            pass

        form = DynamicForm()

    # this prefix is added to urls if otype = project
    # workaround for separate app using communal function
    project_url = ""
    if otype == "project":
        project_url = "/project"

    c = {
        "schema": schema,
        "form": form,
        "parameternames": parameternames,
        "type": otype,
        "success": success,
        "valid": valid,
        "parentObject": parentObject,
        "all_schema": all_schema,
        "schema_id": schema.id,
        "prefix": project_url,
    }

    return render_response_index(request, "tardis_portal/ajax/parameteradd.html", c)
