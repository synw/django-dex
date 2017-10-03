from __future__ import print_function
from django.core.management.base import BaseCommand
from django.core.management import call_command
from dex.exporter import Exporter


class Command(BaseCommand):
    help = 'Clone a database: python manage.py clonedb sourcedb_name destinationdb_name'

    def add_arguments(self, parser):
        parser.add_argument('source', type=str)
        parser.add_argument('dest', type=str)
        parser.add_argument('-apps',
                            dest='applist',
                            default=None,
                            help='Applications to clone: ex: app1,app2,app3',
                            )
        parser.add_argument('-m',
                            dest='migrate',
                            action='store_true',
                            default=False,
                            help='Migrate the destination database',
                            )
        parser.add_argument('-verb',
                            dest='verbosity',
                            default=1,
                            help='Set verbosity',
                            )

    def handle(self, *args, **options):
        ex = Exporter()
        source = options["source"]
        dest = options["dest"]
        applist = options["applist"]
        if options["migrate"] is not False:
            call_command("migrate", "--database=" + dest)
        if applist is not None:
            applist = str.split(options["applist"], ",")
        ex.clone(source, dest, applist=applist, verbosity=options["verbosity"])
