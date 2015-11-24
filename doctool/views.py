import json
import os
import re

from django.http import HttpResponse
from django.template.loader import render_to_string

EmptyLineRex = re.compile(r"^(\s*\n){3}", re.M | re.S)


def render_doc(request):
    result = os.linesep.join(
        i.rstrip()
        for i in EmptyLineRex.split(
            render_to_string("doc.html", json.loads(request.body))
        )
    )
    return HttpResponse(result)
