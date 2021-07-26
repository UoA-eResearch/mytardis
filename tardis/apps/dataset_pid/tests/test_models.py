from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from tardis.tardis_portal.models.experiment import Experiment
from tardis.tardis_portal.models.dataset import Dataset
from tardis.apps.dataset_pid.models import DatasetPID


class ModelsTestCase(TestCase):
    def test_dataset_has_pid(self):
        user = "testuser"
        pwd = User.objects.make_random_password()
        user = User.objects.create(
            username=user,
            email="testuser@example.test",
            first_name="Test",
            last_name="User",
        )
        user.set_password(pwd)
        user.save()
        experiment = Experiment.objects.create(
            title="Test Experiment",
            created_by=user,
            public_access=Experiment.PUBLIC_ACCESS_FULL,
        )
        experiment.save()
        dataset1 = Dataset(description="test dataset1")
        dataset1.save()
        dataset1.experiments.add(experiment)
        dataset1.save()
        self.assertTrue(hasattr(dataset1, "pid"))

    def test_adding_value_to_pid(self):
        user = "testuser"
        pwd = User.objects.make_random_password()
        user = User.objects.create(
            username=user,
            email="testuser@example.test",
            first_name="Test",
            last_name="User",
        )
        user.set_password(pwd)
        user.save()
        experiment = Experiment.objects.create(
            title="Test Experiment",
            created_by=user,
            public_access=Experiment.PUBLIC_ACCESS_FULL,
        )
        experiment.save()
        dataset = Dataset(description="test dataset1")
        dataset.save()
        dataset.experiments.add(experiment)
        dataset.save()
        pid = "my_test_pid"
        dataset_key = dataset.id
        datasetpid = DatasetPID.objects.get(dataset=dataset_key)
        print(datasetpid.id)
        print(dataset.pid.id)
        datasetpid.pid = pid
        print(datasetpid.pid)
        datasetpid.save(["pid"])
        print(dataset.pid.pid)
        self.assertTrue(dataset.pid.pid == pid)

    def test_duplicate_pids_raises_error(self):
        user = "testuser"
        pwd = User.objects.make_random_password()
        user = User.objects.create(
            username=user,
            email="testuser@example.test",
            first_name="Test",
            last_name="User",
        )
        user.set_password(pwd)
        user.save()
        experiment = Experiment.objects.create(
            title="Test Experiment",
            created_by=user,
            public_access=Experiment.PUBLIC_ACCESS_FULL,
        )
        experiment.save()
        dataset1 = Dataset(description="test dataset1")
        dataset1.save()
        dataset1.experiments.add(experiment)
        dataset1.save()
        dataset2 = Dataset(description="test dataset2")
        dataset2.save()
        dataset2.experiments.add(experiment)
        dataset2.save()
        pid = "my_test_pid"
        dataset1.pid.pid = pid
        dataset1.save()
        with self.assertRaises(IntegrityError):
            dataset2.pid.pid = pid
            dataset2.save()
