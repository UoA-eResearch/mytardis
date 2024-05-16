from typing import TypeAlias

from tardis.apps.idw.models.datafile import Datafile
from tardis.apps.idw.models.dataset import Dataset
from tardis.apps.idw.models.experiment import Experiment
from tardis.apps.idw.models.project import Project
from tardis.apps.idw.utils.yaml_helpers import initialise_yaml_helpers

MyTardisObject: TypeAlias = Project | Experiment | Dataset | Datafile

initialise_yaml_helpers()
