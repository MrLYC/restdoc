#!/usr/bin/env python
# coding=utf-8

import json

from django.apps import apps
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import models as dj_models

from django.db.models.fields import NOT_PROVIDED


class Command(BaseCommand):
    field_type_mappings = {
        (
            dj_models.IntegerField, dj_models.BigIntegerField,
            dj_models.AutoField,
        ): "integer",
        (
            dj_models.BooleanField,
        ): "boolean",
        (
            dj_models.FloatField, dj_models.DecimalField,
        ): "float",
        (
            dj_models.DateField, dj_models.DateTimeField,
        ): "datetime",
        (
            dj_models.CharField, dj_models.TextField,
        ): "string",
    }

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+')
        parser.add_argument("-a", "--app", default=""),
        parser.add_argument('-m', "--methods", nargs='+', default=[
            "POST", "GET", "UPDATE", "DELETE",
        ])

    def get_type_by_field(self, field):
        if isinstance(field, dj_models.ForeignKey):
            return self.get_type_by_field(field.related_model._meta.pk)

        for k, v in self.field_type_mappings.items():
            if isinstance(field, k):
                return v

    def handle(self, *args, **kwargs):
        app = kwargs.pop("app")
        methods = kwargs.pop("methods")

        schema = {"endpoint": "api/v1/"}
        models = schema["models"] = []

        for m in kwargs.pop("models"):
            model = apps.get_model(app, m)
            meta = model._meta
            item = {
                "methods": [
                    {"name": method}
                    for method in methods
                ],
                "name": meta.model_name,
                "description": meta.verbose_name,
                "pk": [meta.pk.name],
            }
            models.append(item)
            fields = item["fields"] = []
            required = item["required"] = []

            for f in meta.fields:
                if f.hidden:
                    continue

                if f.default is NOT_PROVIDED:
                    required.append(f.name)
                elif f.default is None and f.null == False:
                    required.append(f.name)

                field_item = {
                    "name": f.name,
                    "description": f.verbose_name,
                    "type": self.get_type_by_field(f),
                }

                if (
                    f.default is not NOT_PROVIDED and
                    (f.default is not None or f.null is True)
                ):
                    field_item["default"] = f.default
                fields.append(field_item)

        print json.dumps(schema, indent=4)
