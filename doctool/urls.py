#!/usr/bin/env python
# encoding: utf-8

from django.conf.urls import url

urlpatterns = [
    url(r'^render/?$', 'doctool.views.render_doc', name='render_doc'),
]
