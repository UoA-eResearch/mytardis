"""
Tests of the Single Sign On authentication

.. moduleauthor:: Chris Seal <c.seal@auckland.ac.nz>
"""

from typing import Dict
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.tardis_portal.models.access_control import UserAuthentication


class SingleSignOnUserTest(TestCase):
    """Test case to ensure that users are created, updated and authenticated appropriately"""

    def setUp(self) -> None:
        self.PUBLIC_USER = User.objects.create_user(username="PUBLIC_USER_TEST")
        self.assertEqual(self.PUBLIC_USER.id, settings.PUBLIC_USER_ID)

    @patch("webpack_loader.loader.WebpackLoader.get_bundle")
    def test_single_sign_on_creates_user(self):
        user_headers: Dict[str, str] = {
            f"HTTP_{settings.REMOTE_AUTH_HEADER}": "tuse001",
            f"HTTP_{settings.REMOTE_AUTH_EMAIL_HEADER}": "test@test.com",
            f"HTTP_{settings.REMOTE_AUTH_FIRST_NAME_HEADER}": "Test",
            f"HTTP_{settings.REMOTE_AUTH_SURNAME_HEADER}": "User",
            f"HTTP_{settings.REMOTE_AUTH_ORCID_HEADER}": "0000-0000-0000",
        }
        request_factory = Client(headers=user_headers)
        request_factory.get("/")
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
