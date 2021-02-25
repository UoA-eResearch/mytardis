"""
views relevant to download cart
"""
import logging

from django.views.generic.base import TemplateView


logger = logging.getLogger(__name__)


class CartView(TemplateView):

    template_name = 'cart.html'