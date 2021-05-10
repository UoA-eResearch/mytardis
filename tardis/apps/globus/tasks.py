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

    transfers_to_submit = [*TransferLog.objects.filter(status=1).values_list("id",flat=True)]
    transfers_to_check = [*TransferLog.objects.filter(status=2).values_list("id",flat=True)]
    #transfers_anyplz = [*TransferLog.objects.all().values_list("status",flat=True)]

    #logger.warning("Here's the content:")
    #logger.warning(transfers_to_submit)
    #logger.warning("#######################")
    #logger.warning(transfers_to_check)
    #logger.warning("#######################")
    #logger.warning(transfers_anyplz)

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

    for transfer_id in transfers_to_check:
        if transfer_id:
            #logger.warning("Updating: #"+str(transfer_id))
            transfer_status(transfer_id)#.apply_async(args=[copy.deepcopy(transfer_id)], **kwargs)
    #logger.warning(len(task_list))
    if len(task_list) < 100:
        N_to_submit = 100-len(task_list)
        #logger.warning(N_to_submit)
        #logger.warning(transfers_to_submit[:N_to_submit])
        for transfer_id in transfers_to_submit[:N_to_submit]:
            #logger.warning("submitting: #"+str(transfer_id))
            transfer_submit(transfer_id)#.apply_async(args=[copy.deepcopy(transfer_id)], **kwargs)

    #hard attempt to submit
    #transfer_submit.apply_async(args=[3], **kwargs)



#@tardis_app.task(name="apps.globus.transfer_status", ignore_result=True)
def transfer_status(transfer_id):
    logger.warning("Actually updating: #"+str(transfer_id))
    from tardis.apps.globus.models import TransferLog

    with transaction.atomic():
        # Get dfo locked for write (to prevent concurrent actions)
        transferlog = TransferLog.objects.select_for_update().get(id=int(transfer_id))

        if transferlog.status > 2:
            return False

        time.sleep(0.1)
        confidential_client = globus_sdk.ConfidentialAppAuthClient(
            client_id=settings.GLOBUS_CLIENT_ID, client_secret=settings.GLOBUS_CLIENT_SECRET)
        scopes = "urn:globus:auth:scope:transfer.api.globus.org:all"
        cc_authorizer = globus_sdk.ClientCredentialsAuthorizer(
            confidential_client, scopes)
        # create a new client
        tc = globus_sdk.TransferClient(authorizer=cc_authorizer)

        #GLOBUS API to get history of log
        task_details = tc.get_task(transferlog.transfer_id)
        if task_details["status"] == "SUCCEEDED":
            transferlog.status = transferlog.STATUS_SUCCEEDED
        if task_details["status"] == "FAILED":
            transferlog.status = transferlog.STATUS_FAILED
        transferlog.save()
        return True

#@tardis_app.task(name="apps.globus.transfer_submit", ignore_result=True)
def transfer_submit(transfer_id):
    logger.warning("starting: #"+str(transfer_id))
    from tardis.apps.globus.models import TransferLog, RemoteHost
    time.sleep(0.1)
    with transaction.atomic():

        transferlog = TransferLog.objects.select_for_update().get(id=int(transfer_id))

        if transferlog.status != transferlog.STATUS_NEW:
            # Job already submitted while this async task was pending,
            # exit without resubmitting job to Globus
            return False

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

        label =  str(transferlog.id) + " " + transferlog.initiated_by.username
        tdata = globus_sdk.TransferData(tc, local_endpoint.endpoint,
                                        transferlog.remote_host.endpoint,
                                        label=label, sync_level="checksum")

        for filepath in transferlog.datafiles.all():
            dfo_filepath = filepath.get_preferred_dfo().uri
            tdata.add_item(dfo_filepath, dfo_filepath)

        new_transfer_id = tc.submit_transfer(tdata)
        transferlog.transfer_id = new_transfer_id["task_id"]
        transferlog.status = transferlog.STATUS_SUBMITTED
        transferlog.save()
        return True
