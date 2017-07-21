from influxdb import InfluxDBClient


CLI = None
POINTS = []


def init(db):
    global CLI
    CLI = InfluxDBClient(
        db.conf["host"],
        db.conf["port"],
        db.conf["user"],
        db.conf["password"],
        db.conf["db"],
    )


def write(point, force_save=False):
    global CLI
    global POINTS
    POINTS.append(point)
    if len(POINTS) < 100 and force_save is False:
        return
    try:
        CLI.write_points(POINTS, batch_size=1000, time_precision="s")
        POINTS = []
    except Exception as err:
        raise err
    return
