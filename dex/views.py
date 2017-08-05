import os
from django.http.response import Http404
from django_downloadview import PathDownloadView


class DexDlView(PathDownloadView):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(app_dir)
    rpath = os.path.join(project_dir, 'replica.sqlite3')

    def dispatch(self, request, *args, **kwargs):
        print("DISP")
        if not self.request.user.is_superuser:
            print("NOT SU")
            raise Http404
        return super(DexDlView, self).dispatch(request, *args, **kwargs)

    def get_path(self):
        return self.rpath
