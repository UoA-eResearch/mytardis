from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

from tardis.tardis_portal.templatetags.approved_user_tags import (
    check_if_user_not_approved,
)

from tardis.apps.yaml_dump.views.idw import idw


def add_idw_menu_item(request, user_menu):
    """Add a 'Manage SSH Keys' item to the user menu

    :param request: an HTTP Request instance
    :type request: :class:`django.http.HttpRequest`
    :param user_menu: user menu context to modify
    :type user_menu: list
    :return: user_menu list
    :rtype: list
    """
    # if check_if_user_not_approved(request):
    #     return user_menu
    idw_menu_item = {
        "url": reverse(idw),
        "icon": "fa fa-magic",
        "label": "Get Instrument Data Wizard"
    }
    # Find the index of "Manage Account" item so we can add item after it.
    # If we can't find it, just insert it at the beginning
    item_index = next(
        (
            i + 1
            for i, menu_item in enumerate(user_menu)
            if "label" in menu_item and menu_item["label"] == "Group Management"
        ),
        0,
    )

    user_menu.insert(item_index, idw_menu_item)
    return user_menu
