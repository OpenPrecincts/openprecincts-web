import us
from django.core.exceptions import PermissionDenied


def all_states():
    return [(s.abbr, s.name) for s in us.STATES] + [('PR', 'Puerto Rico')]


"""
Using Django's groups for state-level permissions.

Each state will have groups for:
    * state admin
    * state gis
    * state contact
    * state write

    admin -> implies all
    gis -> implies no others
    contact -> implies write
    write -> implies no others
"""


class Permissions:
    admin = "admin"
    gis = "gis"
    contact = "contact"
    write = "write"


def has_permission(user, state, permission):
    # normalize state to abbreviation
    abbr = us.states.lookup(state).abbr
    state_groups = user.groups.filter(name__startswith=abbr)
    for group in state_groups:
        state, permtype = group.name.split(" ")
        if permtype == Permissions.admin:
            return True
        elif permtype == Permissions.contact and permission == Permissions.write:
            return True
        elif permtype == permission:
            return True

    # no valid permission found
    return False


def ensure_permission(user, state, permission):
    if not has_permission(user, state, permission):
        raise PermissionDenied
