from __future__ import print_function
from django.core.management.base import BaseCommand
from dex.exporter import Exporter
from dex.conf import MEASUREMENT, TIME_FIELD


class Command(BaseCommand):
    help = 'Export data'

    def add_arguments(self, parser):
        parser.add_argument('db', type=str)
        parser.add_argument(
            '-a',
            default=None,
            dest='appname',
            help='Name of the app to export',
        )
        parser.add_argument(
            '-m',
            default=None,
            dest='measurement',
            help='Name of the measurement',
        )
        parser.add_argument(
            '-t',
            default=None,
            dest='time_field',
            help='Name of the default time field',
        )
        parser.add_argument(
            '-s',
            default=0,
            dest='stats',
            help='Return json stats',
        )

    def handle(self, *args, **options):
        global MEASUREMENT
        global TIME_FIELD
        if options["measurement"] is not None:
            MEASUREMENT = options["measurement"]
        if options["time_field"] is not "date":
            TIME_FIELD = options["time_field"]
        db = options["db"]
        ex = Exporter(db)
        if ex.err != None:
            print("ERROR", ex.err)
            return
        ex.run(MEASUREMENT, TIME_FIELD, options["appname"], options["stats"])
