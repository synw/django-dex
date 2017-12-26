from term.commands import Command, rprint
from django.core.management import call_command
from django.utils.six import StringIO
from dex.export import Exporter
from django.urls.base import reverse


def replicatedb(request, cmd_args):
    ex = Exporter()
    ex.archive_replicas()
    out = StringIO()
    rprint("Migrating replica, please wait ...")
    call_command("migrate", "--database=replica", "--no-color", stdout=out)
    res = out.getvalue()
    endres = res.split("\n")
    for r in endres:
        rprint(r)
    ex.clone("default", "replica", None)
    url = reverse("dex-dl")
    rprint('<a href="' + url + '">Download the replica</a>')


def replicatemedia(request, cmd_args):
    ex = Exporter()
    out = StringIO()
    ex.remove_media_archive()
    res = out.getvalue()
    endres = res.split("\n")
    for r in endres:
        rprint(r)
    rprint("Archiving media directory, please wait ...")
    ex.zipdir()
    rprint("[Ok] Media directory zipped")
    url = reverse("dex-media")
    rprint('<a href="' + url + '">Download the media files</a>')


c1 = Command("replicatedb", replicatedb, "Replicate the database")
c2 = Command("getmedia", replicatemedia, "Zip and download the media files")

COMMANDS = [c1, c2]
