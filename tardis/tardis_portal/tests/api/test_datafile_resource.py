'''
Testing the DataFile resource in MyTardis's Tastypie-based REST API

.. moduleauthor:: Grischa Meyer <grischa@gmail.com>
.. moduleauthor:: James Wettenhall <james.wettenhall@monash.edu>
'''
import hashlib
import json
import os
import tempfile
import unittest

import mock

from django.db.utils import DatabaseError
from django.test.client import Client

import magic

from ...models.datafile import DataFile, DataFileObject
from ...models.dataset import Dataset
from ...models.parameters import ParameterName
from ...models.parameters import Schema
from ...models.access_control import ObjectACL
from ...auth.localdb_auth import django_user
from . import MyTardisResourceTestCase

@unittest.skip("Tests need refactoring due to API changes")
class DataFileResourceTest(MyTardisResourceTestCase):
    def setUp(self):
        super().setUp()
        self.django_client = Client()
        self.django_client.login(username=self.username,
                                 password=self.password)
        self.testds = Dataset()
        self.testds.description = "test dataset"
        self.testds.save()
        acl = ObjectACL(
            pluginId=django_user,
            entityId=str(self.user.id),
            content_object=self.testds,
            canRead=True,
            canDownload=True,
            canWrite=True,
            canSensitive=True,
            isOwner=True,
            aclOwnershipType=ObjectACL.OWNER_OWNED,
        )
        acl.save()
        self.testds.experiments.add(self.testexp)
        df_schema_name = "http://datafileshop.com/"
        self.test_schema = Schema(namespace=df_schema_name,
                                  schema_type=Schema.DATAFILE)
        self.test_schema.save()
        self.test_parname1 = ParameterName(schema=self.test_schema,
                                           name="fileparameter1",
                                           data_type=ParameterName.STRING)
        self.test_parname1.save()
        self.test_parname2 = ParameterName(schema=self.test_schema,
                                           name="fileparameter2",
                                           data_type=ParameterName.NUMERIC)
        self.test_parname2.save()

        self.datafile = DataFile(dataset=self.testds,
                                 filename="testfile.txt",
                                 size="42", md5sum='bogus')
        self.datafile.save()
        acl = ObjectACL(
            pluginId=django_user,
            entityId=str(self.user.id),
            content_object=self.datafile,
            canRead=True,
            canDownload=True,
            canWrite=True,
            canSensitive=True,
            isOwner=True,
            aclOwnershipType=ObjectACL.OWNER_OWNED,
        )
        acl.save()
    def test_post_single_file(self):
        ds_id = self.testds.id
        post_data = """{
    "dataset": "/api/v1/dataset/%d/",
    "filename": "mytestfile.txt",
    "md5sum": "930e419034038dfad994f0d2e602146c",
    "size": "8",
    "mimetype": "text/plain",
    "parameter_sets": [{
        "schema": "http://datafileshop.com/",
        "parameters": [{
            "name": "fileparameter1",
            "value": "123"
        },
        {
            "name": "fileparameter2",
            "value": "123"
        }]
    }]
}""" % ds_id

        post_file = tempfile.NamedTemporaryFile()
        file_content = b"123test\n"
        post_file.write(file_content)
        post_file.flush()
        post_file.seek(0)
        datafile_count = DataFile.objects.count()
        dfo_count = DataFileObject.objects.count()
        self.assertHttpCreated(self.django_client.post(
            '/api/v1/dataset_file/',
            data={"json_data": post_data, "attached_file": post_file}))
        self.assertEqual(datafile_count + 1, DataFile.objects.count())
        self.assertEqual(dfo_count + 1, DataFileObject.objects.count())
        new_file = DataFile.objects.order_by('-pk')[0]
        self.assertEqual(file_content, new_file.get_file().read())

    def test_create_df_for_staging(self):
        ds_id = Dataset.objects.first().id
        post_data = {
            "dataset": "/api/v1/dataset/%d/" % ds_id,
            "filename": "mytestfile.txt",
            "md5sum": "930e419034038dfad994f0d2e602146c",
            "size": "8",
            "mimetype": "text/plain",
            "parameter_sets": []
        }

        datafile_count = DataFile.objects.count()
        dfo_count = DataFileObject.objects.count()
        response = self.django_client.post(
            '/api/v1/dataset_file/',
            json.dumps(post_data),
            content_type='application/json')
        self.assertHttpCreated(response)
        self.assertEqual(datafile_count + 1, DataFile.objects.count())
        self.assertEqual(dfo_count + 1, DataFileObject.objects.count())
        new_datafile = DataFile.objects.order_by('-pk')[0]
        new_dfo = DataFileObject.objects.order_by('-pk')[0]
        self.assertEqual(response.content, new_dfo.get_full_path().encode())

        # Now check we can submit a verification request for that file:
        response = self.django_client.get(
            '/api/v1/dataset_file/%s/verify/'
            % new_datafile.id)
        self.assertHttpOK(response)

    def test_shared_fs_single_file(self):
        pass

    def test_shared_fs_many_files(self):  # noqa # TODO too complex
        '''
        tests sending many files with known permanent location
        (useful for Australian Synchrotron ingestions)
        '''
        files = [{'content': b'test123\n'},
                 {'content': b'test246\n'}]
        from django.conf import settings
        for file_dict in files:
            post_file = tempfile.NamedTemporaryFile(
                dir=settings.DEFAULT_STORAGE_BASE_DIR)
            file_dict['filename'] = os.path.basename(post_file.name)
            file_dict['full_path'] = post_file.name
            post_file.write(file_dict['content'])
            post_file.flush()
            post_file.seek(0)
            file_dict['object'] = post_file

        def clumsily_build_uri(res_type, dataset):
            return '/api/v1/%s/%d/' % (res_type, dataset.id)

        def md5sum(filename):
            md5 = hashlib.md5()  # nosec
            with open(filename, 'rb') as file_obj:
                for chunk in iter(
                        lambda: file_obj.read(128*md5.block_size), b''):
                    md5.update(chunk)
            return md5.hexdigest()

        def guess_mime(filename):
            mime = magic.Magic(mime=True)
            return mime.from_file(filename)

        json_data = {"objects": []}
        for file_dict in files:
            file_json = {
                'dataset': clumsily_build_uri('dataset', self.testds),
                'filename': os.path.basename(file_dict['filename']),
                'md5sum': md5sum(file_dict['full_path']),
                'size': os.path.getsize(file_dict['full_path']),
                'mimetype': guess_mime(file_dict['full_path']),
                'replicas': [{
                    'url': file_dict['filename'],
                    'location': 'default',
                    'protocol': 'file',
                }],
            }
            json_data['objects'].append(file_json)

        datafile_count = DataFile.objects.count()
        dfo_count = DataFileObject.objects.count()
        self.assertHttpAccepted(self.api_client.patch(
            '/api/v1/dataset_file/',
            data=json_data,
            authentication=self.get_credentials()))
        self.assertEqual(datafile_count + 2, DataFile.objects.count())
        self.assertEqual(dfo_count + 2, DataFileObject.objects.count())
        # fake-verify DFO, so we can access the file:
        for newdfo in DataFileObject.objects.order_by('-pk')[0:2]:
            newdfo.verified = True
            newdfo.save()
        for sent_file, new_file in zip(
                reversed(files), DataFile.objects.order_by('-pk')[0:2]):
            self.assertEqual(sent_file['content'], new_file.get_file().read())

    def test_download_file(self):
        '''
        Re-run the upload test in order to create a verified file to
        download - it will be verified immediately becase
        CELERY_ALWAYS_EAGER is True in test_settings.py

        Then download the file, check the HTTP status code and check
        the file content.
        '''
        self.test_post_single_file()
        uploaded_file = DataFile.objects.order_by('-pk')[0]
        response = self.api_client.get(
            '/api/v1/dataset_file/%d/download/' % uploaded_file.id,
            authentication=self.get_credentials())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.getvalue(), b"123test\n")

    def test_failed_dfo_creation(self):
        """Ensure we roll back DataFile creation if DataFileObject creation fails

        The DataFile creation should be rolled back because of the @transaction.atomic
        decorator before api.py's DataFileAppResource class's obj_create method.
        """
        ds_id = Dataset.objects.first().id
        post_data = {
            "dataset": "/api/v1/dataset/%d/" % ds_id,
            "filename": "mytestfile.txt",
            "md5sum": "930e419034038dfad994f0d2e602146c",
            "size": "8",
            "mimetype": "text/plain",
            "parameter_sets": [],
        }

        datafile_count = DataFile.objects.count()
        dfo_count = DataFileObject.objects.count()

        with mock.patch(
            "tardis.tardis_portal.models.datafile.DataFileObject.save"
        ) as dfo_save_mock:
            dfo_save_mock.side_effect = DatabaseError("database connection error")
            # If we used the default SERVER_NAME of "testserver" below,
            # Tastypie would re-raise the exception, rather than returning
            # a 500 error in JSON format, which would then generate a 500.html
            # response which would expect the webpack bundle to be available.
            # We just want to test the case where Tastypie returns a JSON response
            # with 500 status, so we change the SERVER_NAME:
            with self.assertRaises(DatabaseError):
                response = self.django_client.post(
                    "/api/v1/dataset_file/",
                    json.dumps(post_data),
                    content_type="application/json",
                    SERVER_NAME="not-testserver"
                )
                self.assertHttpApplicationError(response)

        # Ensure that we haven't created a DataFile or a DataFileObject:
        self.assertEqual(datafile_count, DataFile.objects.count())
        self.assertEqual(dfo_count, DataFileObject.objects.count())
