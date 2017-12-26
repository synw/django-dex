import os
from django.http.response import Http404
from django.conf import settings
from django.utils._os import safe_join
TERM = "term" in settings.INSTALLED_APPS
if TERM is True:
    from django_downloadview import PathDownloadView


class DexDlView(PathDownloadView):
    rpath = safe_join(settings.BASE_DIR, 'replica.sqlite3')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404
        return super(DexDlView, self).dispatch(request, *args, **kwargs)

    def get_path(self):
        return self.rpath


class DexMediaView(PathDownloadView):
    rpath = safe_join(settings.BASE_DIR, 'media.zip')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404
        return super(DexMediaView, self).dispatch(request, *args, **kwargs)

    def get_path(self):
        return self.rpath
