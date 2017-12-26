from term.commands import Command, rprint
from django.core.management import call_command
from django.utils.six import StringIO
from dex.export import Exporter
from django.urls.base import reverse


def replicatedb(request, cmd_args):
    rprint("Migrating replica, please wait ...")
    ex = Exporter()
    ex.archive_replicas()
    out = StringIO()
    call_command("migrate", "--database=replica", "--no-color", stdout=out)
    res = out.getvalue()
    endres = res.split("\n")
    for r in endres:
        rprint(r)
    ex.clone("default", "replica", None)
    url = reverse("dex-dl")
    rprint('Ok: <a href="' + url + '">download the replica</a>')


c1 = Command("replicatedb", replicatedb, "Replicate the database")

COMMANDS = [c1]
3
