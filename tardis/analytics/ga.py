"""
Google analyitics tracking
"""

import logging
import random

from django.conf import settings

import requests

GA_ID = getattr(settings, "GOOGLE_ANALYTICS_ID", None)
GA_USER_TRACKING = getattr(settings, "GOOGLE_ANALYTICS_USER_TRACKING", False)

logger = logging.getLogger(__name__)


def _track_event(payload, cid=None, uid=None):  # pragma: no cover
    """
    example_payload = {
        't': 'event',
        'ec': 'category',
        'ea': 'action',
        'el': 'label',
        'ev': 1,
    }

    :param payload: analytics data
    :type payload: dict
    :param cid: cid, optional
    :type cid: basestring or int
    :param uid:
    :type uid: basestring

    """
    if GA_ID is None:
        return

    data = {"v": "1", "tid": GA_ID, "cid": cid or random.randint(1, 1000)}
    if GA_USER_TRACKING and uid is not None:
        data["uid"] = uid
    data.update(payload)

    try:
        response = requests.post(
            "http://www.google-analytics.com/collect", data=data, timeout=300
        )
        response.raise_for_status()
    except (requests.ConnectionError, requests.HTTPError) as e:
        logger.debug(f"Google analytics error: {e}, payload: {data}")


def track_login(label, session_id, ip, user):  # pragma: no cover
    _track_event(
        {
            "t": "event",
            "sc": "start",
            "uip": ip,
            "ec": "auth",
            "ea": "login",
            "el": label,
        },
        cid=session_id,
        uid=user.id,
    )


def track_logout(label, session_id, ip, user):  # pragma: no cover
    _track_event(
        {
            "t": "event",
            "sc": "end",
            "uip": ip,
            "ec": "auth",
            "ea": "logout",
            "el": label,
        },
        cid=session_id,
        uid=user.id,
    )


def track_download(
    label, session_id, ip, user, total_size=None, num_files=None, ua=None
):  # pragma: no cover
    payload = {
        "t": "event",
        "uip": ip,
        "ec": "transfer",
        "ea": "download",
        "el": label,
    }
    if total_size is not None:
        payload["ev"] = total_size
    if num_files is not None:
        payload.update(
            {
                "cd1": "num_files",
                "cm1": num_files,
            }
        )
    if ua is not None:
        payload["ua"] = ua
    _track_event(payload, cid=session_id, uid=user.id)
