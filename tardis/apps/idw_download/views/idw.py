from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.base import TemplateView

# @login_required
class IDWIndexView(TemplateView):
    template_name = "idw/index.html"