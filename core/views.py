from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.forms import ModelForm
from .models import Locality, Official, ContactLog, State, PrecinctPlan
from .permissions import ensure_permission, has_permission, Permissions
from files.models import File


class OfficialForm(ModelForm):
    class Meta:
        model = Official
        fields = ['title', 'first_name', 'last_name', 'phone_number', 'email', 'job_title']


def homepage(request):
    return render(request, "core/homepage.html", {})


def national_overview(request):
    return render(request, "core/national_overview.html", {
        "states": State.objects.all()
    })


def state_overview(request, state):
    state = get_object_or_404(State, pk=state.upper())

    context = {"state": state}

    if state.precinct_plan == PrecinctPlan.COUNTY_BY_COUNTY:
        localities = Locality.objects.filter(state=state).annotate(
            total_officials=Count('officials'),
            total_contacts=Count('officials__contact_log_entries'),
        )
        localities_with_officials = sum(1 for l in localities if l.total_officials)
        localities_with_officials_pct = localities_with_officials / localities.count()
        context.update({
            "localities": localities,
            "localities_with_officials": localities_with_officials,
            "localities_with_officials_pct": localities_with_officials_pct,
        })
        return render(request, "core/state_overview.html", context)
    elif state.precinct_plan == PrecinctPlan.STATEWIDE_ORG:
        context["localities"] = None
        return render(request, "core/state_overview.html", context)
    elif state.precinct_plan in (PrecinctPlan.UNKNOWN, PrecinctPlan.EXTERNAL_PARTNER):
        context.update({
            "is_unknown": state.precinct_plan == PrecinctPlan.UNKNOWN,
            "is_external": state.precinct_plan == PrecinctPlan.EXTERNAL_PARTNER,
        })
        return render(request, "core/state_inactive.html", context)


def locality_overview(request, id):
    locality = get_object_or_404(Locality, pk=id)

    if request.method == "POST":
        ensure_permission(request.user, locality.state_id, Permissions.WRITE)
        official_form = OfficialForm(request.POST)
        if official_form.is_valid():
            official = official_form.save(commit=False)
            official.locality = locality
            official.created_by = request.user
            official.save()
            messages.info(request, f"Added {official}")
            official_form = OfficialForm()
        else:
            messages.error(request, f"Error adding official")
    else:
        official_form = OfficialForm()

    officials = Official.objects.filter(locality=locality)
    contact_log = ContactLog.objects.filter(official__locality=locality)
    files = File.objects.filter(locality=locality, active=True)
    user_can_contact = has_permission(request.user, locality.state, Permissions.CONTACT)
    user_can_write = has_permission(request.user, locality.state, Permissions.WRITE)

    return render(request, "core/locality.html", {
        "locality": locality,
        "officials": officials,
        "contact_log": contact_log,
        "files": files,
        "user_can_contact": user_can_contact,
        "user_can_write": user_can_write,
        "official_form": official_form,
    })
