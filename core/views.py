import uuid
import us
from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from django.views import View
from .models import Locality, Official, ContactLog, File


def _states():
    return [(s.abbr, s.name) for s in us.STATES] + [('PR', 'Puerto Rico')]


def national_overview(request):
    return render(request, "core/national_overview.html", {
        "states": _states()
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


def make_s3_path(locality, id, stage, filename):
    stage = {"S": "source", "I": "intermediate"}
    bucket = "raw.openprecincts.org"
    return f"s3://{bucket}/{locality.state_abbreviation}/{stage}/{locality.census_geoid}/{id}-{filename}"


class UploadFiles(View):
    def post(self, request):
        locality = Locality.objects.get(pk=request.POST['locality'])
        for file in request.FILES.getlist("files"):
            new_uuid = uuid.uuid4()
            File.objects.create(
                id=new_uuid,
                stage="S",
                mime_type=file.content_type,
                size=file.size,
                s3_path=make_s3_path(locality, new_uuid, "S", file.name),
                locality=locality,
                source_filename=file.name,
                created_by=request.user,
            )

        return render(request, "core/thanks.html")
