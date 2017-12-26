import os
from django.http.response import Http404
from django.conf import settings
from django.utils._os import safe_join
TERM = "terminal" in settings.INSTALLED_APPS
if TERM is True and "django_downloadview" in settings.INSTALLED_APPS is True:
    from django_downloadview import PathDownloadView


class DexDlView(PathDownloadView):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(app_dir)
    rpath = safe_join(project_dir, 'replica.sqlite3')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404
        return super(DexDlView, self).dispatch(request, *args, **kwargs)

    def get_path(self):
        return self.rpath


class DexMediaView(PathDownloadView):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(app_dir)
    rpath = safe_join(project_dir, 'media.zip')

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_superuser:
            raise Http404
        return super(DexMediaView, self).dispatch(request, *args, **kwargs)

    def get_path(self):
        return self.rpath
