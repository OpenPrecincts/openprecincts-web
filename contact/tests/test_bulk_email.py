import pytest
from django.contrib.auth.models import User
from core.models import Locality
from contact.models import Official, EmailMessage
from contact.views import render_email


@pytest.fixture
def user():
    return User.objects.create(username="testuser")


def setup():
    bot = User.objects.create(username="bot")
    loc = Locality.objects.get(name="Wake County", state__abbreviation="NC")
    Official.objects.create(first_name="Anne", email="anne@example.com", locality=loc,
                            created_by=bot)
    Official.objects.create(first_name="Bob", email="bob@example.com", locality=loc,
                            created_by=bot)
    # inactive
    Official.objects.create(first_name="Cherry", email="cherry@example.com", locality=loc,
                            active=False, created_by=bot)
    # no email
    Official.objects.create(first_name="Don", locality=loc, created_by=bot)


@pytest.mark.django_db
def test_bulk_email_form(client, user):
    # add an EmailMessage so we can test times contacted & last_contacted
    em = EmailMessage.objects.create(
        subject_template="Subj",
        body_template="Body",
        created_by=user,
        sent_at='2019-01-01T12:00Z',
    )
    em.officials.add(Official.objects.get(first_name='Anne'))

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
def test_bulk_email_form_no_recipients(client):
    resp = client.post("/contact/nc/",
                       {"subject_template": "Test",
                        "body_template": "Body",
                        "recipients": [],
                        })
    assert resp.status_code == 200
    messages = list(resp.context['messages'])
    assert str(messages[0]) == "Must specify at least one recipient."


@pytest.mark.django_db
def test_bulk_email_form_valid(client, user):
    client.force_login(user)
    resp = client.get("/contact/nc/")
    recipients = [o.id for o in resp.context["officials"]]
    resp = client.post("/contact/nc/",
                       {"subject_template": "Test",
                        "body_template": "Body",
                        "recipients": recipients,
                        })
    assert resp.status_code == 302
    msg = EmailMessage.objects.get()
    assert msg.officials.count() == 2


@pytest.mark.django_db
def test_render_email():
    anne = Official.objects.get(first_name='Anne')
    msg = EmailMessage(subject_template="{LOCALITY} Boundaries",
                       body_template="{NAME}, Please Help")

    email, subject, body = render_email(msg, anne)
    assert email == "anne@example.com"
    assert subject == "Wake County Boundaries"
    assert body == "Anne , Please Help"


@pytest.mark.django_db
def test_preview_good(client, user):
    anne = Official.objects.get(first_name='Anne')
    msg = EmailMessage.objects.create(
        subject_template="{LOCALITY} Boundaries",
        body_template="{NAME}, Please Help",
        created_by=user,
    )
    msg.officials.add(anne)

    resp = client.get("/contact/preview/1/")
    assert resp.status_code == 200
    assert resp.context["email"] == msg


@pytest.mark.django_db
def test_preview_error(client, user):
    anne = Official.objects.get(first_name='Anne')
    msg = EmailMessage.objects.create(
        subject_template="{LOCALITY} Boundaries",
        body_template="{NAME}, Please Help {BAD-VAR}",
        created_by=user,
    )
    msg.officials.add(anne)

    resp = client.get("/contact/preview/1/")
    assert resp.status_code == 200
    messages = list(resp.context['messages'])
    assert 'BAD-VAR' in str(messages[0])
