"""
test_upload_views.py

Tests for view methods relating to uploads

.. moduleauthor::  Russell Sim <russell.sim@monash.edu>
.. moduleauthor::  Steve Androulakis <steve.androulakis@monash.edu>
.. moduleauthor::  James Wettenhall <james.wettenhall@monash.edu>
.. moduleauthor:: Mike Laverick <mike.laverick@auckland.ac.nz>
"""
from unittest import skipIf
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.test.client import Client

from ...models import DataFile, Dataset, DatasetACL, Experiment, ExperimentACL


class UploadTestCase(TestCase):
    def setUp(self):
        from os import mkdir, path
        from tempfile import mkdtemp

        user = "tardis_user1"
        pwd = "secret"  # nosec
        email = ""
        self.user = User.objects.create_user(user, email, pwd)
        self.user.user_permissions.add(
            Permission.objects.get(codename="change_experiment")
        )

        user2 = "tardis_user2"
        pwd2 = "secret"  # nosec
        email2 = "seconduser@test.com"
        self.user2 = User.objects.create_user(user2, email2, pwd2)
        self.user2.user_permissions.add(
            Permission.objects.get(codename="change_experiment")
        )

        self.test_dir = mkdtemp()

        self.exp = Experiment(
            title="test exp1", institution_name="monash", created_by=self.user
        )
        self.exp.save()

        acl = ExperimentACL(
            user=self.user,
            experiment=self.exp,
            canRead=True,
            canDownload=True,
            canWrite=True,
            canDelete=True,
            canSensitive=True,
            isOwner=True,
            aclOwnershipType=ExperimentACL.OWNER_OWNED,
        )
        acl.save()

        self.dataset = Dataset(description="dataset description...")
        self.dataset.save()
        self.dataset.experiments.add(self.exp)
        self.dataset.save()

        path_parts = [
            settings.FILE_STORE_PATH,
            "%s-%s"
            % (quote(self.dataset.description, safe="") or "untitled", self.dataset.id),
        ]
        self.dataset_path = path.join(*path_parts)

        if not path.exists(self.dataset_path):
            mkdir(self.dataset_path)

        # write test file

        self.filename = "testfile.txt"
        self.filename2 = "testfile2.txt"

        with open(
            path.join(self.test_dir, self.filename), "w", encoding="utf-8"
        ) as self.file1:
            self.file1.write("Test file 1")
            self.file1.close()

        self.file1 = open(  # pylint: disable=consider-using-with
            path.join(self.test_dir, self.filename), "r", encoding="utf-8"
        )

    def tearDown(self):
        from shutil import rmtree

        self.file1.close()
        rmtree(self.test_dir)
        rmtree(self.dataset_path)
        self.exp.delete()

    @skipIf(settings.ONLY_EXPERIMENT_ACLS is False, "skipping Macro ACL specific test")
    def test_file_upload_macro(self):
        from os import path

        client = Client()
        client.login(username="tardis_user1", password="secret")  # nosec
        session_id = client.session.session_key

        client.post(
            "/upload/" + str(self.dataset.id) + "/",
            {"Filedata": self.file1, "session_id": session_id},
        )

        test_files_db = DataFile.objects.filter(dataset__id=self.dataset.id)
        self.assertTrue(path.exists(path.join(self.dataset_path, self.filename)))
        target_id = Dataset.objects.first().id
        self.assertEqual(self.dataset.id, target_id)
        url = test_files_db[0].file_objects.all()[0].uri
        self.assertEqual(
            url,
            path.relpath(
                "%s/testfile.txt" % self.dataset_path, settings.FILE_STORE_PATH
            ),
        )
        self.assertTrue(test_files_db[0].file_objects.all()[0].verified)

    @skipIf(settings.ONLY_EXPERIMENT_ACLS is True, "skipping Micro ACL specific test")
    def test_file_upload_micro(self):
        from os import path

        self.datasetacl = DatasetACL(
            user=self.user,
            dataset=self.dataset,
            canRead=True,
            canDownload=True,
            canWrite=True,
            canDelete=True,
            canSensitive=True,
            isOwner=True,
            aclOwnershipType=DatasetACL.OWNER_OWNED,
        )
        self.datasetacl.save()

        client = Client()
        client.login(username="tardis_user1", password="secret")  # nosec
        session_id = client.session.session_key
        response = client.post(
            "/upload/" + str(self.dataset.id) + "/",
            {"Filedata": self.file1, "session_id": session_id},
        )
        # User should now be able to upload file
        self.assertEqual(response.status_code, 200)

        test_files_db = DataFile.objects.filter(dataset__id=self.dataset.id)
        self.assertTrue(path.exists(path.join(self.dataset_path, self.filename)))
        target_id = Dataset.objects.first().id
        self.assertEqual(self.dataset.id, target_id)
        url = test_files_db[0].file_objects.all()[0].uri
        self.assertEqual(
            url,
            path.relpath(
                "%s/testfile.txt" % self.dataset_path, settings.FILE_STORE_PATH
            ),
        )
        self.assertTrue(test_files_db[0].file_objects.all()[0].verified)

    def test_upload_complete(self):
        from django.http import HttpRequest, QueryDict

        from ...views.upload import upload_complete

        data = [
            ("filesUploaded", "1"),
            ("speed", "really fast!"),
            ("allBytesLoaded", "2"),
            ("errorCount", "0"),
        ]
        post = QueryDict("&".join(["%s=%s" % (k, v) for (k, v) in data]))
        request = HttpRequest()
        request.user = self.user
        request.POST = post
        response = upload_complete(request)
        self.assertTrue(b"<p>Number: 1</p>" in response.content)
        self.assertTrue(b"<p>Errors: 0</p>" in response.content)
        self.assertTrue(b"<p>Bytes: 2</p>" in response.content)
        self.assertTrue(b"<p>Speed: really fast!</p>" in response.content)
