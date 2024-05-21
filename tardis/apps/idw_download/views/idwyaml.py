import logging

from django.http import HttpResponse

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tardis.apps.projects.models import Project
from tardis.apps.idw_download.models.ingestion_metadata import IngestionMetadata
from tardis.apps.idw_download.utils.dataset import wrangle_dataset_into_IDW_YAML
from tardis.apps.idw_download.utils.experiment import wrangle_experiment_into_IDW_YAML
from tardis.apps.idw_download.utils.project import wrangle_project_into_IDW_YAML
from tardis.tardis_portal.api_v2.serializers.dataset import DatasetSerializer
from tardis.tardis_portal.api_v2.serializers.experiment import ExperimentSerializer
from tardis.tardis_portal.api_v2.serializers.project import ProjectSerializer
from tardis.tardis_portal.models.dataset import Dataset
from tardis.tardis_portal.models.experiment import Experiment

logger = logging.getLogger("__name__")


class IDWYAMLView(generics.ListAPIView):

    permission_classes = [IsAuthenticated]
    project_serialiser_class = ProjectSerializer
    experiment_serialiser_class = ExperimentSerializer
    dataset_serialiser_class = DatasetSerializer

    def get(self, request, *args, **kwargs):
        ingestion_metadata = IngestionMetadata()
        logger.debug(request.user)
        project_queryset = Project.safe.all(user=request.user)
        experiment_queryset = Experiment.safe.all(user=request.user)
        dataset_queryset = Dataset.safe.all(user=request.user)

        project_serialiser = self.project_serialiser_class(
            project_queryset, context={"request": request}, many=True
        )
        experiment_serialiser = self.experiment_serialiser_class(
            experiment_queryset, context={"request": request}, many=True
        )
        dataset_serialiser = self.dataset_serialiser_class(
            dataset_queryset, context={"request": request}, many=True
        )

        response_results = {
            "projects": project_serialiser.data,
            "experiments": experiment_serialiser.data,
            "datasets": dataset_serialiser.data,
        }
        ingestion_metadata.projects = [
            wrangle_project_into_IDW_YAML(project)
            for project in response_results["projects"]
        ]
        ingestion_metadata.experiments = [
            wrangle_experiment_into_IDW_YAML(experiment)
            for experiment in response_results["experiments"]
        ]
        ingestion_metadata.datasets = [
            wrangle_dataset_into_IDW_YAML(dataset)
            for dataset in response_results["datasets"]
        ]
        # response = Response(response_results)        # Convert response data to YAML
        data = ingestion_metadata._to_yaml()

        # Create a YAML file
        response = HttpResponse(data, content_type="application/yaml")
        response["Content-Disposition"] = 'attachment; filename="ingestion.yaml"'
        return response
