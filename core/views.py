from django.contrib.auth.decorators import login_not_required
from django.shortcuts import render

from core.utils import init_context


@login_not_required
def index_view(request):
    payload = init_context(title="Accueil")

    return render(request, "core/index.html", payload)
