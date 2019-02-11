import us


def all_states():
    return [(s.abbr, s.name) for s in us.STATES] + [('PR', 'Puerto Rico')]
