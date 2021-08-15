from django.contrib import admin
from .models import InstrumentProfile  # noqa

# Register Profile models in admin site
admin.site.register(InstrumentProfile)
