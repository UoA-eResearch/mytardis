"""
Tests of the Single Sign On authentication

.. moduleauthor:: Chris Seal <c.seal@auckland.ac.nz>
"""

from datetime import datetime, timedelta
from typing import Dict
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user
from django.contrib.auth.models import User
from django.test import Client, TestCase

from tardis.tardis_portal.models.access_control import UserAuthentication, UserProfile


class SingleSignOnUserTest(TestCase):
    """Test case to ensure that users are created, updated and authenticated appropriately"""

    def setUp(self) -> None:
        self.PUBLIC_USER = User.objects.create_user(username="PUBLIC_USER_TEST")
        self.assertEqual(self.PUBLIC_USER.id, settings.PUBLIC_USER_ID)
        self.user_headers: Dict[str, str] = {
            f"{settings.REMOTE_AUTH_HEADER}": "tuse001",
            f"{settings.REMOTE_AUTH_EMAIL_HEADER}": "test@test.com",
            f"{settings.REMOTE_AUTH_FIRST_NAME_HEADER}": "Test",
            f"{settings.REMOTE_AUTH_SURNAME_HEADER}": "User",
            f"{settings.REMOTE_AUTH_ORCID_HEADER}": "0000-0000-0000",
        }

    @patch("webpack_loader.loader.WebpackLoader.get_bundle")
    def test_single_sign_on_creates_user(self, mock_webpack_get_bundle):
        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.get("/login/", headers=self.user_headers)
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user.username, "tuse001")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
        user_profile = UserProfile.objects.get(user=user)
        self.assertFalse(user_profile.isDjangoAccount)
        user_auth = UserAuthentication.objects.get(userProfile=user_profile)
        self.assertEqual(user_auth.authenticationMethod, "sso")
        self.assertTrue(get_user(self.client).is_authenticated)
        self.assertAlmostEqual(
            self.client.session.get_expiry_age(),
            settings.SESSION_COOKIE_AGE,
        )
        self.client.session.flush()

    @patch("webpack_loader.loader.WebpackLoader.get_bundle")
    def test_header_updates_user(self, mock_webpack_get_bundle):
        incomplete_header: Dict[str, str] = {
            f"{settings.REMOTE_AUTH_HEADER}": "tuse001",
            f"{settings.REMOTE_AUTH_FIRST_NAME_HEADER}": "Bob",
            f"{settings.REMOTE_AUTH_SURNAME_HEADER}": "",
            f"{settings.REMOTE_AUTH_ORCID_HEADER}": "",
        }
        response = self.client.get("/login/", headers=incomplete_header)
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user.username, "tuse001")
        self.assertEqual(user.first_name, "Bob")
        self.assertEqual(user.last_name, "")
        self.client.logout()
        self.client.session.flush()
        response = self.client.get("/login/", headers=self.user_headers)
        self.assertEqual(response.status_code, 302)
        user = get_user(self.client)
        self.assertEqual(user.username, "tuse001")
        self.assertEqual(user.email, "test@test.com")
        self.assertEqual(user.first_name, "Test")
        self.assertEqual(user.last_name, "User")
