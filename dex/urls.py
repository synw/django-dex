# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import DexDlView, DexMediaView


urlpatterns = [
    url(r'^get_replica/$', DexDlView.as_view(), name="dex-dl"),
    url(r'^get_media/$', DexMediaView.as_view(), name="dex-media")
]
