from django.apps import AppConfig
from tardis.app_config import AbstractTardisAppConfig


# class GlobusConfig(AbstractTardisAppConfig):
#     name = 'tardis.apps.globus'
#     verbose_name = 'Globus'

class CartConfig(AbstractTardisAppConfig):
    name = 'tardis.apps.cart'
    verbose_name = "Cart"
