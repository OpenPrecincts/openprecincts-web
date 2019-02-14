import re
import pytest
from django.contrib import auth
from django.contrib.auth.models import User


@pytest.mark.django_db
def test_signup_good(client):
    resp = client.post("/accounts/signup/",
                       {"email": "test@example.com", "display_name": "test",
                        "state": "NC"})
    assert resp.status_code == 302
    u = User.objects.filter(email="test@example.com")
    assert u.count()
    assert u[0].password == ""
    assert u[0].profile.state == "NC"


@pytest.mark.django_db
def test_signup_duplicate(client):
    User.objects.create(email="test@example.com")

    # reject duplicate email
    resp = client.post("/accounts/signup/",
                       {"email": "test@example.com", "display_name": "test",
                        "state": "DC"})
    assert resp.status_code == 200       # show form again with error
    assert not resp.context["form"].is_valid()
    assert User.objects.count() == 1


@pytest.mark.django_db
def test_login(client, mailoutbox):
    newuser = User.objects.create(email="test@example.com")
    resp = client.post("/accounts/login/", {"email": "test@example.com"})
    assert resp.status_code == 200

    # ensure email comes through
    assert len(mailoutbox) == 1
    m = mailoutbox[0]
    url = re.findall(r'https?://\S+', m.body)
    assert url
    assert list(m.to) == ['test@example.com']

    # hit magic URL and we should be logged in
    client.get(url[0])
    user = auth.get_user(client)
    assert user == newuser


@pytest.mark.django_db
def test_login_invalid_email(client, mailoutbox):
    resp = client.post("/accounts/login/", {"email": "test@example.com"})
    assert resp.status_code == 200
    assert not resp.context["form"].is_valid()
