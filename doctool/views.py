import json

from django.shortcuts import render


def render_doc(request):
    return render(request, "doc.html", json.loads(request.body))
