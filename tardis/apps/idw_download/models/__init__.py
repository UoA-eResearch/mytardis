from typing import TypeAlias

from tardis.apps.idw_download.models.datafile import Datafile
from tardis.apps.idw_download.models.dataset import Dataset
from tardis.apps.idw_download.models.experiment import Experiment
from tardis.apps.idw_download.models.project import Project
from tardis.apps.idw_download.utils.yaml_helpers import initialise_yaml_helpers

MyTardisObject: TypeAlias = Project | Experiment | Dataset | Datafile

initialise_yaml_helpers()
