import us
from django.shortcuts import render, get_object_or_404
from .models import Locality, Official, ContactLog


def _states():
    return [(s.abbr, s.name) for s in us.STATES] + [('PR', 'Puerto Rico')]


def national_overview(request):
    return render(request, "core/national_overview.html", {
        "states": _states()
    })


def state_overview(request, state):
    state = us.states.lookup(state)
    localities = Locality.objects.filter(state=state)

    return render(request, "core/state_overview.html", {
        "state": state,
        "localities": localities,
    })


def locality_overview(request, id):
    locality = get_object_or_404(Locality, pk=id)
    officials = Official.objects.filter(locality=locality)
    contact_log = ContactLog.objects.filter(official__locality=locality)

    return render(request, "core/locality.html", {
        "locality": locality,
        "officials": officials,
        "contact_log": contact_log,
    })
