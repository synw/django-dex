from terminal.commands import Command, rprint, endcmd
from django.core.management import call_command
from django.utils.six import StringIO
from dex.exporter import Exporter
from django.urls.base import reverse


def replicatedb(*args):
    rprint("Migrating replica, please wait ...")
    ex = Exporter()
    out = StringIO()
    call_command("migrate", "--database=replica", "--no-color", stdout=out)
    res = out.getvalue()
    endres = res.split("\n")
    for r in endres:
        rprint(r)
    ex.clone("default", "replica", None)
    url = reverse("dex-dl")
    rprint('Ok: <a href="' + url + '">download the replica</a>')
    endcmd()


c1 = Command("replicatedb", replicatedb)

COMMANDS = [c1]
