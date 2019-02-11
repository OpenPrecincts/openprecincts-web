import us
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Locality, Official, ContactLog
from .utils import all_states
from files.models import File


def national_overview(request):
    return render(request, "core/national_overview.html", {
        "states": all_states()
    })


def state_overview(request, state):
    state = us.states.lookup(state)
    localities = Locality.objects.filter(state=state).annotate(
        total_officials=Count('officials'),
        total_contacts=Count('officials__contact_log_entries'),
    )
    localities_with_officials = sum(1 for l in localities if l.total_officials)
    localities_with_officials_pct = localities_with_officials / localities.count()
    return render(request, "core/state_overview.html", {
        "state": state,
        "localities": localities,
        "localities_with_officials": localities_with_officials,
        "localities_with_officials_pct": localities_with_officials_pct,
    })


def locality_overview(request, id):
    locality = get_object_or_404(Locality, pk=id)
    officials = Official.objects.filter(locality=locality)
    contact_log = ContactLog.objects.filter(official__locality=locality)
    files = File.objects.filter(locality=locality, active=True)

    return render(request, "core/locality.html", {
        "locality": locality,
        "officials": officials,
        "contact_log": contact_log,
        "files": files,
    })
