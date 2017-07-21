import datetime
import json
import time
import importlib
from django.core.exceptions import FieldDoesNotExist
from dex.conf import TIME_FIELDS


def serialize_protocol(model, instance, data, measurement, time_field):
    res = _format_data(model, instance, data, measurement,
                       time_field, TIME_FIELDS)
    return res


def _to_date(val):
    return val.strftime('%Y-%m-%dT%H:%M:%SZ')


def _format_data(model, instance, data, measurement, time_field, time_fields):
    modelname = model.__name__
    tags = {"modelname": modelname}
    t = int(datetime.datetime.now().timestamp())
    timefield = None
    is_timefield = False
    if modelname in time_fields:
        timefield = time_fields[modelname]
    for field in data:
        try:
            ftype = model._meta.get_field(field).get_internal_type
        except FieldDoesNotExist:
            ftype = "unknown"
        val = data[field]
        if 'DateTimeField' in str(ftype) and timefield is None:
            val = getattr(instance, field)
            if val is not None:
                tv = int(val.timestamp())
                tags[field] = tv
        if not "TextField" in str(ftype) and is_timefield is False:
            tags[field] = val
        if field == time_field or (timefield is not None and field == timefield):
            val = getattr(instance, field)
            if val is not None:
                tv = int(val.timestamp())
                t = _to_date(val)

    fields = {"num": 1}
    data = {
        "measurement": measurement,
        "tags": tags,
        "fields": fields,
        "time": t,
    }
    return data


def get_serializer(path):
    function_string = path
    mod_name, func_name = function_string.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    serz = getattr(mod, func_name)
    #print(serz, type(serz))
    return serz
