import datetime
from django.core.exceptions import FieldDoesNotExist
from dex.conf import TIME_FIELDS


def serialize_protocol(model, instance, data, measurement, time_field, enable_text_field):
    res = _format_data(model, instance, data, measurement,
                       time_field, TIME_FIELDS, enable_text_field)
    return res


def _to_date(val):
    return val.strftime('%Y-%m-%dT%H:%M:%SZ')


def _format_data(model, instance, data, measurement, time_field, time_fields, enable_text_field):
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
        if is_timefield is False:
            if enable_text_field is False:
                if not "TextField" in str(ftype):
                    tags[field] = val
                else:
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
