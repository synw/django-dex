# -*- coding: utf-8 -*-

from django.conf.urls import url
from .views import DexDlView


urlpatterns = [
    url(r'^download/$', DexDlView.as_view(), name="dex-dl")
]
