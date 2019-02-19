from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from django.forms import ModelForm
from .models import Locality, Official, ContactLog, State
from .permissions import ensure_permission, has_permission, Permissions
from files.models import File


class OfficialForm(ModelForm):
    class Meta:
        model = Official
        fields = ['title', 'first_name', 'last_name', 'phone_number', 'email', 'job_title']


def homepage(request):
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}
    return render(request, "core/homepage.html",
                  {'state_status': state_status})


def national_overview(request):
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}
    return render(request, "core/national_overview.html", {
        "states": State.objects.all(),
        "state_status": state_status,
    })


def state_overview(request, state):
    state = get_object_or_404(State, pk=state.upper())

    context = {"state": state}

    localities = Locality.objects.filter(state=state).annotate(
        total_officials=Count('officials'),
        total_contacts=Count('officials__contact_log_entries'),
        total_files=Count('files'),
    )
    # TODO: ensure file count only includes source files

    # compute totals
    localities_with_officials = 0
    total_officials = 0
    localities_with_contacts = 0
    total_contacts = 0
    localities_with_files = 0
    total_files = 0
    for l in localities:
        if l.total_officials:
            total_officials += l.total_officials
            localities_with_officials += 1
        if l.total_contacts:
            total_contacts += l.total_contacts
            localities_with_contacts += 1
        if l.total_files:
            total_files += l.total_files
            localities_with_files += 1

    context.update({
        "localities": localities,
        "localities_with_officials": localities_with_officials,
        "total_officials": total_officials,
        "localities_with_contacts": localities_with_contacts,
        "total_contacts": total_contacts,
        "localities_with_files": localities_with_files,
        "total_files": total_files,
    })
    return render(request, "core/state_overview.html", context)


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
