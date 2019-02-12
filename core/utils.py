import us


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


def has_permission(user, state, permission):
    """
    permission:
        admin, gis, contact, write
    """
    state_groups = user.groups.filter(name__startswith=state)
    for group in state_groups:
        state, permtype = group.name.split("-")
        if permtype == 'admin':
            return True
        elif permtype == 'contact' and permission == 'write':
            return True
        elif permtype == permission:
            return True

    # no valid permission found
    return False
