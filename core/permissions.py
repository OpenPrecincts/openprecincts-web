import us
from enum import Enum
from django.core.exceptions import PermissionDenied


STATE_NAME_TO_ABBR = {s.name: s.abbr for s in us.states.STATES_AND_TERRITORIES}


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


class Permissions(Enum):
    ADMIN = "admin"
    GIS = "gis"
    CONTACT = "contact"
    WRITE = "write"


def has_permission(user, state, permission):
    # normalize state to abbreviation
    if hasattr(state, 'abbreviation'):
        abbr = state.abbreviation
    else:
        abbr = us.states.lookup(state).abbr
    state_groups = user.groups.filter(name__startswith=abbr)
    for group in state_groups:
        state, permtype = group.name.split(" ")
        if permtype == Permissions.ADMIN.value:
            return True
        elif permtype == Permissions.CONTACT.value and permission == Permissions.WRITE.value:
            return True
        elif permtype == permission:
            return True

    # no valid permission found
    return False


def ensure_permission(user, state, permission):
    if not has_permission(user, state, permission):
        raise PermissionDenied
