#__author__ = 'manishkumr'
#__author__ = 'mike-ivs'

# pylint: disable=R1710
# disabling complaint about return contents

import functools

from django.conf import settings
from django.dispatch import receiver

def suspendingreceiver(signal, **decorator_kwargs):
    def our_wrapper(func):
        @receiver(signal, **decorator_kwargs)
        @functools.wraps(func)
        def fake_receiver(sender, **kwargs):
            if settings.SUSPEND_ES_SIGNALS:
                return
            return func(sender, **kwargs)
        return fake_receiver
    return our_wrapper
