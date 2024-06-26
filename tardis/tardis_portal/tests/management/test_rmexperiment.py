from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from ...models import (
    DataFile,
    DatafileACL,
    DatafileParameterSet,
    Dataset,
    DatasetACL,
    DatasetParameterSet,
    Experiment,
    ExperimentACL,
    ExperimentParameter,
    ExperimentParameterSet,
    License,
)


def _create_test_user():
    user_ = User(
        username="tom",
        first_name="Thomas",
        last_name="Atkins",
        email="tommy@atkins.net",
    )
    user_.save()
    return user_


def _create_license():
    license_ = License(
        name="Creative Commons Attribution-NoDerivs 2.5 Australia",
        url="http://creativecommons.org/licenses/by-nd/2.5/au/",
        internal_description="CC BY 2.5 AU",
        allows_distribution=True,
    )
    license_.save()
    return license_


def _create_test_experiment(user, license_):
    experiment = Experiment(
        title="Norwegian Blue", description="Parrot + 40kV", created_by=user
    )
    experiment.public_access = Experiment.PUBLIC_ACCESS_FULL
    experiment.license = license_
    experiment.save()
    experiment.experimentauthor_set.create(
        order=0, author="John Cleese", url="http://nla.gov.au/nla.party-1"
    )
    experiment.experimentauthor_set.create(
        order=1, author="Michael Palin", url="http://nla.gov.au/nla.party-2"
    )
    acl = ExperimentACL(
        experiment=experiment,
        user=user,
        isOwner=True,
        canRead=True,
        canDownload=True,
        canWrite=True,
        canDelete=True,
        canSensitive=True,
        aclOwnershipType=ExperimentACL.OWNER_OWNED,
    )
    acl.save()
    return experiment


def _create_test_dataset(user, nosDatafiles):
    ds_ = Dataset(description="happy snaps of plumage")
    ds_.save()
    if not settings.ONLY_EXPERIMENT_ACLS:
        acl = DatasetACL(
            dataset=ds_,
            user=user,
            isOwner=True,
            canRead=True,
            canDownload=True,
            canWrite=True,
            canDelete=True,
            canSensitive=True,
            aclOwnershipType=DatasetACL.OWNER_OWNED,
        )
        acl.save()
    for i in range(0, nosDatafiles):
        df_ = DataFile(
            dataset=ds_, filename="file_%d" % i, size="21", sha512sum="bogus"
        )
        df_.save()
        if not settings.ONLY_EXPERIMENT_ACLS:
            acl = DatafileACL(
                datafile=df_,
                user=user,
                isOwner=True,
                canRead=True,
                canDownload=True,
                canWrite=True,
                canDelete=True,
                canSensitive=True,
                aclOwnershipType=DatafileACL.OWNER_OWNED,
            )
            acl.save()
    ds_.save()
    return ds_


def _create_test_data():
    # Create 2 experiments with 3 datasets,
    # one of which is in both experiments.
    user_ = _create_test_user()
    license_ = _create_license()
    exp1_ = _create_test_experiment(user_, license_)
    exp2_ = _create_test_experiment(user_, license_)
    ds1_ = _create_test_dataset(user_, 1)
    ds2_ = _create_test_dataset(user_, 2)
    ds3_ = _create_test_dataset(user_, 3)
    ds1_.experiments.add(exp1_)
    ds2_.experiments.add(exp1_)
    ds2_.experiments.add(exp2_)
    ds3_.experiments.add(exp2_)
    ds1_.save()
    ds2_.save()
    ds3_.save()
    exp1_.save()
    exp2_.save()
    return (exp1_, exp2_, user_)


_counter = 1


def _next_id():
    global _counter
    res = _counter
    _counter += 1
    return res


class RmExperimentTestCase(TestCase):
    def testList(self):
        self.PUBLIC_USER = User.objects.create_user(username="PUBLIC_USER_TEST")
        self.assertEqual(self.PUBLIC_USER.id, settings.PUBLIC_USER_ID)
        (exp1_, exp2_, user_) = _create_test_data()
        self.assertEqual(DataFile.objects.all().count(), 6)
        self.assertEqual(len(exp1_.get_datafiles(user_)), 3)
        self.assertEqual(len(exp2_.get_datafiles(user_)), 5)

        # Check that --list doesn't remove anything
        call_command("rmexperiment", exp1_.pk, list=True)
        self.assertEqual(DataFile.objects.all().count(), 6)
        self.assertEqual(len(exp1_.get_datafiles(user_)), 3)
        self.assertEqual(len(exp2_.get_datafiles(user_)), 5)

    def testRemove(self):
        (exp1_, exp2_, user_) = _create_test_data()
        self.assertEqual(DataFile.objects.all().count(), 6)
        self.assertEqual(len(exp1_.get_datafiles(user_)), 3)
        self.assertEqual(len(exp2_.get_datafiles(user_)), 5)

        # Remove first experiment and check that the shared dataset hasn't
        # been removed
        call_command("rmexperiment", exp1_.pk, confirmed=True)
        self.assertEqual(DataFile.objects.all().count(), 5)
        self.assertEqual(len(exp2_.get_datafiles(user_)), 5)

        # Remove second experiment
        call_command("rmexperiment", exp2_.pk, confirmed=True)
        self.assertEqual(DataFile.objects.all().count(), 0)

        # Check that everything else has been removed too
        self.assertEqual(ExperimentACL.objects.all().count(), 0)
        self.assertEqual(DatasetACL.objects.all().count(), 0)
        self.assertEqual(DatafileACL.objects.all().count(), 0)
        self.assertEqual(ExperimentParameterSet.objects.all().count(), 0)
        self.assertEqual(ExperimentParameter.objects.all().count(), 0)
        self.assertEqual(DatasetParameterSet.objects.all().count(), 0)
        self.assertEqual(DatafileParameterSet.objects.all().count(), 0)
