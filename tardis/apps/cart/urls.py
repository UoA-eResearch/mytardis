from django.conf.urls import url

from tardis.apps.cart.views import CartView

urlpatterns = [
    url(r'^$', CartView.as_view(), name='cart')
]