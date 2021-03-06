from io import StringIO
import pytest
from django.contrib.auth.models import User, Group
from django.core.management import call_command
from core.models import Locality, State
from contact.models import Official, EmailMessage, EmailMessageInstance
from contact.views import render_email


@pytest.fixture
def user():
    u = User.objects.create(username="testuser")
    g = Group.objects.create(name="NC contact")
    u.groups.add(g)
    return u


def setup():
    bot = User.objects.create(username="bot")
    state = State.objects.create(abbreviation='NC', name='North Carolina', census_geoid='37')
    loc = Locality.objects.create(
        name="Wake County",
        state_id=state.abbreviation,
        wikipedia_url='https://en.wikipedia.org/wiki/Wake_County,_North_Carolina',
        official_url='http://www.wakegov.com',
        ocd_id='ocd-division/country:us/state:nc/county:wake',
        census_geoid='37183',
    )
    Official.objects.create(
        first_name="Anne", email="anne@example.com", locality=loc, created_by=bot
    )
    Official.objects.create(
        first_name="Bob", email="bob@example.com", locality=loc, created_by=bot
    )
    # inactive
    Official.objects.create(
        first_name="Cherry",
        email="cherry@example.com",
        locality=loc,
        active=False,
        created_by=bot,
    )
    # no email
    Official.objects.create(first_name="Don", locality=loc, created_by=bot)


@pytest.mark.django_db
def test_bulk_email_form(client, user):
    client.force_login(user)
    state = State.objects.get(abbreviation="NC")
    # add an EmailMessage so we can test times contacted & last_contacted
    em = EmailMessage.objects.create(
        subject_template="Subj",
        body_template="Body",
        created_by=user,
        sent_at="2019-01-01T12:00Z",
        state=state,
    )
    EmailMessageInstance.objects.create(
        official=Official.objects.get(first_name="Anne"), message=em
    )

    resp = client.get("/contact/nc/")
    assert resp.status_code == 200
    # only two active officials with email addresses
    assert resp.context["officials"].count() == 2

    # pull the two officials out
    anne, bob = resp.context["officials"]
    if bob.first_name == "Anne":
        anne, bob = bob, anne

    assert anne.times_contacted == 1
    assert anne.last_contacted is not None
    assert bob.times_contacted == 0
    assert bob.last_contacted is None


@pytest.mark.django_db
def test_bulk_email_form_no_recipients(client, user):
    client.force_login(user)
    resp = client.post(
        "/contact/nc/",
        {"subject_template": "Test", "body_template": "Body", "recipients": []},
    )
    assert resp.status_code == 200
    messages = list(resp.context["messages"])
    assert str(messages[0]) == "Must specify at least one recipient."


@pytest.mark.django_db
def test_bulk_email_form_valid(client, user):
    client.force_login(user)
    resp = client.get("/contact/nc/")
    recipients = [o.id for o in resp.context["officials"]]
    resp = client.post(
        "/contact/nc/",
        {"subject_template": "Test", "body_template": "Body", "recipients": recipients},
    )
    assert resp.status_code == 302
    msg = EmailMessage.objects.get()
    assert msg.officials.count() == 2


@pytest.mark.django_db
def test_render_email():
    anne = Official.objects.get(first_name="Anne")
    msg = EmailMessage(
        subject_template="{LOCALITY} Boundaries", body_template="{NAME}, Please Help"
    )

    email, subject, body = render_email(msg, anne)
    assert email == "anne@example.com"
    assert subject == "Wake County Boundaries"
    assert body == "Anne , Please Help"


@pytest.mark.django_db
def test_preview_good(client, user):
    anne = Official.objects.get(first_name="Anne")
    state = State.objects.get(abbreviation="NC")
    msg = EmailMessage.objects.create(
        subject_template="{LOCALITY} Boundaries",
        body_template="{NAME}, Please Help",
        state=state,
        created_by=user,
    )
    EmailMessageInstance.objects.create(official=anne, message=msg)

    resp = client.get("/contact/preview/1/")
    assert resp.status_code == 200
    assert resp.context["email"] == msg


@pytest.mark.django_db
def test_preview_error(client, user):
    anne = Official.objects.get(first_name="Anne")
    state = State.objects.get(abbreviation="NC")
    msg = EmailMessage.objects.create(
        subject_template="{LOCALITY} Boundaries",
        body_template="{NAME}, Please Help {BAD-VAR}",
        state=state,
        created_by=user,
    )
    EmailMessageInstance.objects.create(official=anne, message=msg)

    resp = client.get("/contact/preview/1/")
    assert resp.status_code == 200
    messages = list(resp.context["messages"])
    assert "BAD-VAR" in str(messages[0])


@pytest.mark.django_db
def test_send_emails_basic(user, mailoutbox):
    anne = Official.objects.get(first_name="Anne")
    state = State.objects.get(abbreviation="NC")
    msg = EmailMessage.objects.create(
        subject_template="{LOCALITY} Boundaries",
        body_template="{NAME}, Please Help",
        state=state,
        created_by=user,
    )
    EmailMessageInstance.objects.create(official=anne, message=msg)

    # nothing approved
    out = StringIO()
    call_command("send_emails", stdout=out)
    assert "No messages" in out.getvalue()

    # approve then send
    msg.approved_by = user
    msg.approved_at = "2019-02-15T00:00:00Z"
    msg.save()

    out = StringIO()
    call_command("send_emails", stdout=out)
    assert len(mailoutbox) == 1

    # nothing approved & unsent
    out = StringIO()
    call_command("send_emails", stdout=out)
    assert "No messages" in out.getvalue()
