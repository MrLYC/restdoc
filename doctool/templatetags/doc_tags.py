#!/usr/bin/env python
# encoding: utf-8

import uuid
import datetime
import random
import json
import urllib
import re

from django import template

register = template.Library()


@register.filter(name="mock_data")
def mock_data(fields):
    result = {}
    for f in fields:
        fname = f["name"]
        fval = f.get("default", NotImplemented)
        if fval is not NotImplemented:
            result[fname] = fval
            continue

        ftype = f.get("type", "string")
        f_id = abs(id(f))
        if ftype == "string":
            result[fname] = uuid.uuid3(uuid.NAMESPACE_OID, str(f_id)).get_hex()[:8]
        elif ftype == "integer":
            result[fname] = f_id % 100
        elif ftype == "float":
            result[fname] = f_id % 100 / 1.0
        elif ftype == "uuid":
            result[fname] = uuid.uuid3(uuid.NAMESPACE_OID, str(f_id)).get_hex()
        elif ftype == "date":
            result[fname] = datetime.date.today().isoformat()
        elif ftype == "datetime":
            result[fname] = datetime.datetime.today().isoformat()
        elif ftype == "boolean":
            result[fname] = [True, False][f_id % 2]
        elif ftype.endswith("list"):
            result[fname] = []
    return result


@register.filter(name="is_required_field")
def is_required_field(field, model):
    required_fields = set(model.get("required", ()))
    return field in required_fields


@register.filter(name="pickup_required")
def pickup_required(value, model):
    required_fields = set(model.get("required", ()))
    return {
        f["name"]: value.get(f["name"])
        for f in model["fields"]
        if f["name"] in required_fields
    }


@register.filter(name="is_pk_field")
def is_pk_field(field, model):
    pk_fields = set(model.get("pk", ()))
    return field in pk_fields


@register.filter(name="pickup_pk")
def pickup_pk(value, model):
    pk_fields = set(model.get("pk", ()))
    return {
        f["name"]: value.get(f["name"])
        for f in model["fields"]
        if f["name"] in pk_fields
    }


@register.filter(name="to_querystr")
def to_querystr(value, model):
    return urllib.urlencode(pickup_pk(value, model))


@register.filter(name="to_json")
def to_json(value):
    return json.dumps(value, indent=4)

@register.filter(name="simple_result")
def simple_result(value, method):
    return {
        "ret_code": 200,
        "message": "ok",
        "result": [value] if method in ["GET", "DELETE"] else value
    }


class Plural(object):
    def GetMatchAndApplyFuncs(strPattern, strSearch, strReplace):
        def MatchRule(strWord):
            return re.search(strPattern, strWord)

        def ApplyRule(strWord):
            return re.sub(strSearch, strReplace, strWord)

        return (MatchRule, ApplyRule)

    g_tlPattern = (
        ('[sxz]$', '$', 'es'),
        ('[^aeioudgkprt]h$', '$', 'es'),
        ('(qu|[^aeiou])y$', 'y$', 'ies'),
        ('$', '$', 's'),
    )
    g_lsRules = [GetMatchAndApplyFuncs(strPattern, strSearch, strReplace) for (strPattern, strSearch, strReplace) in g_tlPattern]

    @register.filter(name="plural")
    def GetPlural(strWord):
        if not strWord:
            return ""

        for fnMatch, fnApply in Plural.g_lsRules:
            if fnMatch(strWord):
                return fnApply(strWord)
