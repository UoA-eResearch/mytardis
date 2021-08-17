'''
AJAX URLS
'''
from django.conf.urls import include, url

from tardis.tardis_portal.views import (
    retrieve_parameters,
    dataset_json,
    display_datafile_details,
    experiment_datasets_json,
    experiment_latest_dataset,
    experiment_recent_datasets,
    retrieve_experiment_metadata,
    retrieve_dataset_metadata,
    retrieve_datafile_list,
    cache_dataset,
    retrieve_user_list,
    retrieve_group_list,
    retrieve_group_list_by_user,
    upload_complete,
    experiment_description,
    experiment_datasets,
    retrieve_owned_exps_list,
    retrieve_shared_exps_list,
    edit_datafile_par,
    edit_dataset_par,
    edit_experiment_par,
    add_datafile_par,
    add_dataset_par,
    add_experiment_par,
    choose_rights,
    share,
    experiment_dataset_transfer,
    retrieve_licenses,
    feedback
)

json_urls = [
    url(r'^dataset/(?P<dataset_id>\d+)$', dataset_json,
        name='tardis.tardis_portal.views.dataset_json'),
    url(r'^experiment/(?P<experiment_id>\d+)/dataset/$',
        experiment_datasets_json,
        name='tardis.tardis_portal.views.experiment_datasets_json'),
    url(r'^experiment/(?P<experiment_id>\d+)/dataset/(?P<dataset_id>\d+)$',
        dataset_json,
        name='tardis.tardis_portal.views.dataset_json'),
]

ajax_urls = [
    url(r'^parameters/(?P<datafile_id>\d+)/$', retrieve_parameters),
    url(r'^datafile_details/(?P<datafile_id>\d+)/$',
        display_datafile_details),
    url(r'^dataset_metadata/(?P<dataset_id>\d+)/$', retrieve_dataset_metadata,
        name='tardis.tardis_portal.views.retrieve_dataset_metadata'),
    url(r'^experiment_metadata/(?P<experiment_id>\d+)/$',
        retrieve_experiment_metadata,
        name='tardis.tardis_portal.views.retrieve_experiment_metadata'),
    url(r'^datafile_list/(?P<dataset_id>\d+)/$', retrieve_datafile_list,
        name='tardis.tardis_portal.views.retrieve_datafile_list'),
    url(r'^cache_dataset/(?P<dataset_id>\d+)/$', cache_dataset,
        name='cache_dataset'),
    url(r'^user_list/$', retrieve_user_list),
    url(r'^group_list/$', retrieve_group_list),
    url(r'^group_list_by_user/$', retrieve_group_list_by_user),
    url(r'^upload_complete/$', upload_complete),
    url(r'^experiment/(?P<experiment_id>\d+)/description$',
        experiment_description,
        name='tardis.tardis_portal.views.experiment_description'),
    url(r'^experiment/(?P<experiment_id>\d+)/datasets$', experiment_datasets),
    url(r'^experiment/(?P<experiment_id>\d+)/latest_dataset$',
        experiment_latest_dataset),
    url(r'^experiment/(?P<experiment_id>\d+)/recent_datasets$',
        experiment_recent_datasets),
    url(r'^owned_exps_list/$', retrieve_owned_exps_list,
        name='tardis.tardis_portal.views.retrieve_owned_exps_list'),
    url(r'^owned_proj_list/$', retrieve_owned_proj_list,
        name='tardis.tardis_portal.views.retrieve_owned_proj_list'),
    url(r'^shared_exps_list/$', retrieve_shared_exps_list,
        name='tardis.tardis_portal.views.retrieve_shared_exps_list'),
    url(r'^edit_datafile_parameters/(?P<parameterset_id>\d+)/$',
        edit_datafile_par,
        name='tardis.tardis_portal.views.edit_datafile_par'),
    url(r'^edit_dataset_parameters/(?P<parameterset_id>\d+)/$',
        edit_dataset_par,
        name='tardis.tardis_portal.views.edit_dataset_par'),
    url(r'^edit_experiment_parameters/(?P<parameterset_id>\d+)/$',
        edit_experiment_par,
        name='tardis.tardis_portal.views.edit_experiment_par'),
    url(r'^add_datafile_parameters/(?P<datafile_id>\d+)/$',
        add_datafile_par,
        name='tardis.tardis_portal.views.add_datafile_par'),
    url(r'^add_dataset_parameters/(?P<dataset_id>\d+)/$',
        add_dataset_par,
        name='tardis.tardis_portal.views.add_dataset_par'),
    url(r'^add_experiment_parameters/(?P<experiment_id>\d+)/$',
        add_experiment_par,
        name='tardis.tardis_portal.views.add_experiment_par'),
    url(r'^experiment/(?P<experiment_id>\d+)/rights$', choose_rights,
        name='tardis.tardis_portal.views.choose_rights'),
    url(r'^experiment/(?P<experiment_id>\d+)/share$', share,
        name='tardis.tardis_portal.views.share'),
    url(r'^experiment/(?P<experiment_id>\d+)/dataset-transfer$',
        experiment_dataset_transfer,
        name='tardis.tardis_portal.views.experiment_dataset_transfer'),
    url(r'^license/list$', retrieve_licenses,
        name='tardis.tardis_portal.views.retrieve_licenses'),
    url(r'^json/', include(json_urls)),
    url(r'^feedback/', feedback,
        name='tardis.tardis_portal.views.feedback'),
]
