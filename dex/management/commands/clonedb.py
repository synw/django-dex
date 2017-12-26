from __future__ import print_function
from goerr import err
from django.core.management.base import BaseCommand
from django.core.management import call_command
from dex.export import Exporter


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
        parser.add_argument('-a',
                            dest='archive',
                            action='store_true',
                            default=False,
                            help='Archive current replica',
                            )

    def handle(self, *args, **options):
        try:
            ex = Exporter()
        except Exception as e:
            err.new(e, self.handle, "Can not initialize exporter")
        if options["archive"] is True:
            ex.archive_replicas()
        source = options["source"]
        dest = options["dest"]
        applist = options["applist"]
        if options["migrate"] is not False:
            try:
                call_command("migrate", "--database=" + dest)
            except Exception as e:
                err.new(e, self.handle,
                        "Can not migrate destination database " + dest)
        if applist is not None:
            applist = str.split(options["applist"], ",")
        try:
            ex.clone(source, dest, applist=applist,
                     verbosity=int(options["verbosity"]))
        except Exception as e:
            err.new(e, self.handle,
                    "Can not clone database")
        if err.exists:
            err.throw()
