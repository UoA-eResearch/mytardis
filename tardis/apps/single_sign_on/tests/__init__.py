"""
test/__init__.py

.. moduleauthor:: CHris Seal <c.seal@auckland.ac.nz>
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

class SSOTestCase(TestCase):

    def setUp(self):
        self.PUBLIC_USER = User.objects.create_user(username="PUBLIC_USER_TEST")
        self.assertEqual(self.PUBLIC_USER.id, settings.PUBLIC_USER_ID)
         