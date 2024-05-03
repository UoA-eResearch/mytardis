from datetime import timedelta
from enum import Enum

from django.conf import settings


def generate_storage_enum():
    enum_dict = {
        "DEFAULT": {
            "class": "Default",
            "retention_period": timedelta(days=settings.DEFAULT_RETENTION_PERIOD),
        }
    }
    for name in dir(settings):
        if name.startswith("RETENTION_PERIOD"):
            enum_name = name.removeprefix("RETENTION_PERIOD")
            class_name = enum_name.replace("_", " ").title()
            enum_dict[enum_name] = {
                "class": class_name,
                "retention_period": timedelta(days=getattr(settings, name)),
            }
    return Enum("StorageClassification", enum_dict)


StorageClassification = generate_storage_enum()

# class StorageClassification(Enum):
#    DEFAULT = {
#        "class": "Default",
#        "retention_period": timedelta(days=settings.DEFAULT_RETENTION_PERIOD),
#    }
