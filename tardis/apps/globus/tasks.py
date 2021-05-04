import logging
import time

from django.conf import settings
from django.db import transaction
import globus_sdk

from tardis.celery import tardis_app

logger = logging.getLogger(__name__)


# import Globus credentials from a settings.py (code in settings: if app enabled)
# endpoint activation? Separate credentials? or add tardis as admin of endpoints too

@tardis_app.task(name="apps.globus.globus_transfers", ignore_result=True)
def globus_transfers(**kwargs):
    from .models import TransferLog

    kwargs['transaction_lock'] = kwargs.get('transaction_lock', True)

    transfers_to_submit = TransferLog.objects.filter(status=1)
    transfers_to_check = TransferLog.objects.filter(status=2)

    # hit globus API for number of pending transfers
    confidential_client = globus_sdk.ConfidentialAppAuthClient(
        client_id=settings.GLOBUS_CLIENT_ID, client_secret=settings.GLOBUS_CLIENT_SECRET)
    scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
    cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
        confidential_client, scopes)
    # create a new client
    tc = globus_sdk.TransferClient(authorizer=cc_authorizer)
    task_list = list(tc.task_list(num_results=100, filter='status:ACTIVE,INACTIVE'))
    task_list = [task["task_id"] for task in task_list]

    for transfer in transfers_to_check:
        if transfer.transfer_id not in task_list:
            transfer_status.apply_async(args=[transfer.id], **kwargs)


    if len(task_list) < 100:
        N_to_submit = 100-len(task_list)
        for transfer in transfers_to_submit[:N_to_submit]:
            transfer_submit.apply_async(args=[transfer.id], **kwargs)


@tardis_app.task(name="apps.globus.transfer_status", ignore_result=True)
def transfer_status(transfer_id, *args, **kwargs):

    from tardis.apps.globus.models import TransferLog
    time.sleep(0.1)
    confidential_client = globus_sdk.ConfidentialAppAuthClient(
        client_id=settings.GLOBUS_CLIENT_ID, client_secret=settings.GLOBUS_CLIENT_SECRET)
    scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
    cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
        confidential_client, scopes)
    # create a new client
    tc = globus_sdk.TransferClient(authorizer=cc_authorizer)

    # Get dfo locked for write (to prevent concurrent actions)
    if kwargs.pop('transaction_lock', False):
        with transaction.atomic():
            transferlog = TransferLog.objects.select_for_update().get(id=transfer_id)
            #GLOBUS API to get history of log
            task_details = tc.get_task(transfer_id)
            if task_details == "SUCCEEDED":
                transferlog.status = transferlog.STATUS_SUCCEEDED
            if task_details == "FAILED":
                transferlog.status = transferlog.STATUS_FAILED
            transferlog.save()



@tardis_app.task(name="apps.globus.transfer_submit", ignore_result=True)
def transfer_submit(transfer_id, *args, **kwargs):
    from tardis.apps.globus.models import TransferLog, RemoteHost
    time.sleep(0.1)
    confidential_client = globus_sdk.ConfidentialAppAuthClient(
        client_id=settings.GLOBUS_CLIENT_ID, client_secret=settings.GLOBUS_CLIENT_SECRET)
    scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
    cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
        confidential_client, scopes)
    # create a new client
    tc = globus_sdk.TransferClient(authorizer=cc_authorizer)

    # TODO remove this horrible hardcode
    local_endpoint = RemoteHost.objects.get(pk=1)
    # Get dfo locked for write (to prevent concurrent actions)
    if kwargs.pop('transaction_lock', False):
        with transaction.atomic():

            transferlog = TransferLog.objects.select_for_update().get(id=transfer_id)
            label =  str(transferlog.id) + " " + transferlog.initiated_by.username
            tdata = globus_sdk.TransferData(tc, local_endpoint.endpoint,
                                            transferlog.remote_host.endpoint,
                                            label=label, sync_level="checksum")

            for filepath in transferlog.datafiles.objects.all():
                tdata.add_item(filepath.get_absolute_filepath(), filepath.filename)

            new_transfer_id = tc.submit_transfer(tdata)
            transferlog.transfer_id = new_transfer_id
            transferlog.status = transferlog.STATUS_SUBMITTED
            transferlog.save()
