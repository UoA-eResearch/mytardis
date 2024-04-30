"""
Tests of the Single Sign On authentication

.. moduleauthor:: Chris Seal <c.seal@auckland.ac.nz>
"""

import logging
import sys
from contextlib import contextmanager
from typing import Dict

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.apps.single_sign_on.tests import SSOTestCase
from tardis.tardis_portal.models.access_control import UserAuthentication


@contextmanager
def streamhandler_to_console(lggr):
    # Use 'up to date' value of sys.stdout for StreamHandler,
    # as set by test runner.
    stream_handler = logging.StreamHandler(sys.stdout)
    lggr.addHandler(stream_handler)
    yield
    lggr.removeHandler(stream_handler)


def testcase_log_console(lggr):
    def testcase_decorator(func):
        def testcase_log_console(*args, **kwargs):
            with streamhandler_to_console(lggr):
                return func(*args, **kwargs)

        return testcase_log_console

    return testcase_decorator


logger = logging.getLogger("django_test")


class SingleSignOnUserTest(SSOTestCase):
    """Test case to ensure that users are created, updated and authenticated appropriately"""

    def setUp(self) -> None:
        super().setUp()

    @testcase_log_console
    def test_single_sign_on_creates_user(self):
        user_headers: Dict[str, str] = {
            f"HTTP_{settings.REMOTE_AUTH_HEADER}": "tuse001",
            f"HTTP_{settings.REMOTE_AUTH_EMAIL_HEADER}": "test@test.com",
            f"HTTP_{settings.REMOTE_AUTH_FIRST_NAME_HEADER}": "Test",
            f"HTTP_{settings.REMOTE_AUTH_SURNAME_HEADER}": "User",
            f"HTTP_{settings.REMOTE_AUTH_ORCID_HEADER}": "0000-0000-0000",
        }
        logger.debug(user_headers)
        request_factory = Client(headers=user_headers)
        logger.debug("Setting up client")
        request_factory.get("/")
        logger.debug("Got response")
        user = User.objects.get(pk=2)

        self.assertEqual(user.username, "tuse001")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        user_auth = UserAuthentication.objects.get(userProfile__user=user)
        self.assertEqual(user_auth.authenticationMethod, "sso")
        self.assertFalse(user.userprofile.isDjangoAccount)

    # def test_single_sign_on_authenticates_user(self):
    #    request_factory = Client(headers=user_headers)
    #    request_factory.get("/login/")
