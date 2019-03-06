import us
import pytest
from django.contrib.auth.models import User, Group
from core.permissions import Permissions, has_permission
from core.models import State


def setup():
    User.objects.create(username="nothing")
    writer = User.objects.create(username="writer")
    contactor = User.objects.create(username="contactor")
    boss = User.objects.create(username="boss")

    write = Group.objects.create(name="NC write")
    contact = Group.objects.create(name="NC contact")
    admin = Group.objects.create(name="NC admin")

    writer.groups.add(write)
    contactor.groups.add(contact)
    boss.groups.add(admin)


@pytest.mark.django_db
def test_has_permission_basics():
    u = User.objects.get(username="writer")

    assert has_permission(u, "NC", "write")
    assert has_permission(u, "NC", Permissions.WRITE)
    assert has_permission(u, us.states.lookup("NC"), "write")
    assert has_permission(u, State(abbreviation="NC"), "write")

    assert not has_permission(u, "NC", "contact")
    assert not has_permission(u, "VA", "write")


@pytest.mark.django_db
def test_has_permission_admin():
    u = User.objects.get(username="boss")

    assert has_permission(u, "NC", "write")
    assert has_permission(u, "NC", "contact")
    assert has_permission(u, "NC", "admin")

    assert not has_permission(u, "VA", "write")


@pytest.mark.django_db
def test_has_permission_contact_implies_write():
    u = User.objects.get(username="contactor")

    assert has_permission(u, "NC", "write")
    assert has_permission(u, "NC", "contact")
    assert not has_permission(u, "NC", "admin")
