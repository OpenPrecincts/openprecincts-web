from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models.expressions import RawSQL
from django.db.models import Count, Q
from django.forms import ModelForm
from .models import Locality, Official, ContactLog, State
from .permissions import ensure_permission, has_permission, Permissions
from files.models import File
import json
import os
from django.conf import settings

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
def national_overview_internal(request):
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}
    contributors = _get_contributors(state=None)

    # Initialize dictionaries for officials, contacts, and files
    off = {}
    off_fields = ['created_by_id', 'created_at']
    con = {}
    con_fields =  ['contacted_by_id', 'contact_date']
    fil = {}
    fil_fields = ['created_by_id', 'created_at']

    # Initalize dictionaries sorted by state
    for state in State.objects.all().values():
        abbr = state['abbreviation']
        off[abbr] = {}
        con[abbr] = {}
        fil[abbr] = {}

    # Match user id's to info
    user = {}
    for u in User.objects.all().values():
        user[u['id']] = u['username']

    # Iterate through all of the officials
    officials = Official.objects.all()
    officials_vals = officials.values()
    official_ix = 0
    for i, o in enumerate(officials):

        # Get state abbreviation
        abbr = o.locality.state.abbreviation
        off[abbr][official_ix] = {}

        # iterate through all the necessary fields
        for field in off_fields:
            off[abbr][official_ix][field] = officials_vals[i][field]

        # iterate index
        official_ix += 1

    # Iterate through all of the contacts
    contacts = ContactLog.objects.all()
    contacts_vals = contacts.values()
    contact_ix = 0
    for i, c in enumerate(contacts):

        # Get state abbreviation
        abbr = c.official.locality.state.abbreviation
        con[abbr][contact_ix] = {}

        # iterate through all the necessary fields
        for field in con_fields:
            con[abbr][contact_ix][field] = contacts_vals[i][field]

        # iterate index
        contact_ix += 1

    # Iterate through all of the officials
    files = File.objects.all()
    files_vals = files.values()
    file_ix = 0
    for i, f in enumerate(files):

        # Get state abbreviation
        abbr = f.locality.state.abbreviation
        fil[abbr][file_ix] = {}

        # iterate through all the necessary fields
        for field in fil_fields:
            fil[abbr][file_ix][field] = files_vals[i][field]

        # iterate index
        file_ix += 1
    

    return render(request, "core/national_overview_internal.html", {
        "officials": off,
        "contact_log": con,
        "files": fil,
        "username_mapping": user,
        "states": State.objects.all().order_by('name'),
        "state_status": state_status,
        "contributors": contributors,
    })



def interactive_map(request):
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}
    return render(request, "core/interactive_map.html", {
        "states": State.objects.all().order_by('name'),
        "state_status": state_status,
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
    print(state)
    state = get_object_or_404(State, pk=state.upper())

    context = {"state": state}

    localities = Locality.objects.filter(state=state)
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

    context.update({
        "localities": localities,
        "localities_with_officials": localities_with_officials,
        "total_officials": total_officials,
        "localities_with_contacts": localities_with_contacts,
        "total_contacts": total_contacts,
        "localities_with_files": localities_with_files,
        "total_files": total_files,
        #"contributors": contributors,
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
            messages.info(request, "Added {official}")
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

def state_overview_internal_map(request, state):
    state = get_object_or_404(State, pk=state.upper())
    context = {"state": state}
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}

    # Initialize dictionaries for officials, contacts, and files
    off = {}
    off_fields = ['created_by_id', 'created_at']
    con = {}
    con_fields =  ['contacted_by_id', 'contact_date']
    fil = {}
    fil_fields = ['created_by_id', 'created_at']
    geoid = {} 
    
    for local in Locality.objects.filter(state=state):

        # Initialize dictionaries
        name = local.name
        off[name] = {}
        con[name] = {}
        fil[name] = {}
        
        # Map locality names to geoid
        geoid[name] = local.census_geoid

        # Add Officials
        ix = 0
        for o in Official.objects.filter(locality=local).all():
            # Initalize locality dictionary
            off[name][ix] = {}
            off[name][ix]['created_by'] = o.created_by.username
            off[name][ix]['created_at'] = o.created_at
            ix += 1

        # Add Contacts
        ix = 0
        for c in ContactLog.objects.filter(official__locality=local).all():
            con[name][ix] = {}
            con[name][ix]['contacted_by'] = c.contacted_by.username
            con[name][ix]['contact_date'] = c.contact_date
            ix += 1

        # Add Files
        ix = 0
        for f in File.objects.filter(locality=local).all():
            fil[name][ix] = {}
            fil[name][ix]['created_by_id'] = f.created_by.username
            fil[name][ix]['created_at'] = f.created_at


    localities = Locality.objects.filter(state=state)
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
        # Pass in data about officials, contact log, and user ids
        "officials": off,
        "contact_log": con,
        "files": fil,
        "geoid": geoid,
        "state_status": state_status,
    })
    return render(request, "core/state_overview_internal_map.html", context)

def state_overview_internal(request, state):
    state = get_object_or_404(State, pk=state.upper())

    context = {"state": state}

    ############################################################################################
    state_status = {s.abbreviation: s.status().value
                    for s in State.objects.all()}
    #################################################################################################

    # Convert querysets for Officials, ContactLog, and Files into dictionaries
    localities = Locality.objects.filter(state=state)
    localities_values = Locality.objects.filter(state=state).values()

    # Get Officials in the state
    off = {}
    official_ix = 0
    # Loop through each official in each loaclity
    for i, l in enumerate(localities_values):
        officials = Official.objects.filter(locality=localities[i])

        # Create dictionary for officials in a given county
        off[l['name']] = {}

        for o in officials.values():
            # Give each official an index to access in dictionary 
            off[l['name']][official_ix] = {}

            # add all fields
            for name in o.keys():
                off[l['name']][official_ix][name] = o[name]

            # Increment index
            official_ix += 1

        # Reset official index for locality
        official_ix = 0

    # Get ContactLog in the state
    con = {}
    contact_ix = 0
    # Loop through each contnact for each official in each loaclity
    for i, l in enumerate(localities_values):

        officials = Official.objects.filter(locality=localities[i])

        # Create dictionary for each contact log in a given county
        con[l['name']] = {}

        for o in officials:
            contact = ContactLog.objects.filter(official=o)

            for c in contact.values():
                # Give each contact log entry an index to access in dictionary 
                con[l['name']][contact_ix] = {}

                # add all fields
                for name in c.keys():
                    con[l['name']][contact_ix][name] = c[name]

                # Increment index
                contact_ix += 1

        # Reset official index for locality
        contact_ix = 0

    # Match user id's to info
    user = {}
    for u in User.objects.all().values():
        user[u['id']] = u['username']

    localities = Locality.objects.filter(state=state)
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
        # Pass in data about officials, contact log, and user ids
        "officials": off,
        "contact_log": con,
        "username_mapping": user,
        ############################################################################################
        "state_status": state_status,
        #################################################################################################
    })
    return render(request, "core/state_overview_internal.html", context)

def default_map(request):
    mapbox_access_token = 'pk.eyJ1IjoiY29ubm9ybW9mZmF0dCIsImEiOiJjanNubjllcnowNXRtNDVxbXJycGk2bGphIn0.tIVxZ6bTWPunc1fe1Xpmdw'
    return render(request, 'core/default_map.html', 
        {'mapbox_access_token':mapbox_access_token})

def alabama_map(request):
    path = os.path.join(settings.STATICFILES_DIRS[0], 'geodata', 'AL-01-alabama-counties.json')
    al = open(path)
    al = json.load(al)
    al = json.dumps(al)
    return render(request, 'core/alabama_map.html', {'alabama': al})