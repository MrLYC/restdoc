#!/usr/bin/env python
# encoding: utf-8

import uuid
import datetime
import random
import json
import urllib

from django import template

register = template.Library()


@register.filter(name="mock_data")
def mock_data(fields):
    result = {}
    for f in fields:
        fname = f["name"]
        ftype = f["type"]
        f_id = abs(id(f))
        if ftype == "string":
            result[fname] = uuid.uuid3(uuid.NAMESPACE_OID, str(f_id)).get_hex()[:8]
        elif ftype == "integer":
            result[fname] = f_id % 100
        elif ftype == "float":
            result[fname] = f_id / 1.0
        elif ftype == "uuid":
            result[fname] = uuid.uuid3(uuid.NAMESPACE_OID, str(f_id)).get_hex()
        elif ftype == "date":
            result[fname] = datetime.date.today().isoformat()
        elif ftype == "datetime":
            result[fname] = datetime.datetime.today().isoformat()
        elif ftype == "boolean":
            result[fname] = [True, False][f_id % 2]
    return result


@register.filter(name="pickup_required")
def pickup_required(value, fields):
    return {
        f["name"]: value[f["name"]]
        for f in fields
        if f.get("required") is True
    }


@register.filter(name="pickup_pk")
def pickup_pk(value, fields):
    return {
        f["name"]: value[f["name"]]
        for f in fields
        if f.get("pk") is True
    }


@register.filter(name="to_querystr")
def to_querystr(value, fields):
    return urllib.urlencode(pickup_pk(value, fields))


@register.filter(name="to_json")
def to_json(value):
    return json.dumps(value, indent=4)

@register.filter(name="simple_result")
def simple_result(value, method):
    return {
        "code": 200,
        "message": "ok",
        "result": [value] if method in ["GET", "DELETE"] else value
    }
