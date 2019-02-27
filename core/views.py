from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.expressions import RawSQL
from django.db.models import Count, Q
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
    contributors = _get_contributors(state=None)
    return render(request, "core/national_overview.html", {
        "states": State.objects.all().order_by('name'),
        "state_status": state_status,
        "contributors": contributors,
    })


def _get_contributors(state):
    official_filter = None
    file_filter = None

    if state:
        official_filter = Q(created_officials__locality__state=state)
        file_filter = Q(created_files__locality__state=state)

    # get merged list of user contributions
    official_contribs = User.objects.all().annotate(
        num_officials=Count('created_officials', filter=official_filter)
    ).order_by('id')
    file_contribs = {u.id: u for u in User.objects.annotate(
        num_files=Count('created_files', filter=file_filter)
    )}
    contributors = [
        {'id': u.id,
         'name': u.first_name or u.username,
         'num_officials': u.num_officials,
         'num_files': file_contribs[u.id].num_files,
         }
        for u in official_contribs
    ]

    # sort by total contributions
    contributors_filtered = []
    for c in contributors:
        c['total'] = c['num_officials'] + c['num_files']
        if c['total']:
            contributors_filtered.append(c)
    return sorted(contributors_filtered, key=lambda c: c['total'], reverse=True)


def state_overview(request, state):
    state = get_object_or_404(State, pk=state.upper())

    context = {"state": state}

    localities = Locality.objects.filter(state=state).order_by('name')
    localities = localities.annotate(
        total_officials=RawSQL(
            "SELECT COUNT(*) FROM core_official WHERE core_official.locality_id=core_locality.id",
            ()),
        total_contacts=RawSQL(
            "SELECT COUNT(*) FROM core_contactlog JOIN core_official "
            " ON core_contactlog.official_id=core_official.id "
            " WHERE core_official.locality_id=core_locality.id",
            ()),
        total_files=RawSQL(
            "SELECT COUNT(*) FROM files_file WHERE files_file.locality_id=core_locality.id",
            ()),
    )

    contributors = _get_contributors(state)

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

    user_can_contact = has_permission(request.user, state, Permissions.CONTACT)
    user_can_write = has_permission(request.user, state, Permissions.WRITE)

    context.update({
        "localities": localities,
        "localities_with_officials": localities_with_officials,
        "total_officials": total_officials,
        "localities_with_contacts": localities_with_contacts,
        "total_contacts": total_contacts,
        "localities_with_files": localities_with_files,
        "total_files": total_files,
        "user_can_contact": user_can_contact,
        "user_can_write": user_can_write,
        "contributors": contributors,
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
