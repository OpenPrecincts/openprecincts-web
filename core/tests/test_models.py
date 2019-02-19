from core.models.locality import State, StateStatus


def test_state_collection_status():
    s = State(abbreviation="NC", name="NC", census_geoid="00")

    # all in Unknown state: inactive
    assert s.collection_status() == "inactive"

    # all need to be done: wip
    s.task_collect = False
    s.task_contact = False
    s.task_files = False
    assert s.collection_status() == "wip"

    # some are done, some aren't: wip
    s.task_collect = True
    assert s.collection_status() == "wip"

    # all are done
    s.task_contact = True
    s.task_files = True
    assert s.collection_status() == "complete"

    # simpler case, we only need to do files: wip
    s.task_collect = None
    s.task_contact = None
    s.task_files = False
    assert s.collection_status() == "wip"

    # and we did the files, done
    s.task_files = True
    assert s.collection_status() == "complete"


def test_state_cleaning_status():
    s = State(abbreviation="NC", name="NC", census_geoid="00")

    s.task_files = False
    s.task_digitization = False

    # if we need to do collection first, cleaning status will be inactive
    assert s.cleaning_status() == "inactive"

    # goes to WIP when collection is done
    s.task_files = True
    assert s.cleaning_status() == "wip"

    # done when digitization is done
    s.task_digitization = True
    assert s.cleaning_status() == "complete"


def test_state_final_status():
    s = State(abbreviation="NC", name="NC", census_geoid="00")

    s.task_files = False
    s.task_digitization = False
    s.task_verification = False
    s.task_published = False

    # state starts out as inactive
    assert s.final_status() == "inactive"

    # still inactive after collection is done
    s.task_files = True
    assert s.final_status() == "inactive"

    # WIP after we're done with digitization
    s.task_digitization = True
    assert s.final_status() == "wip"

    # WIP after we start verification
    s.task_verification = True
    assert s.final_status() == "wip"

    # and, done!
    s.task_published = True
    assert s.final_status() == "complete"


def test_state_status():
    s = State(abbreviation="NC", name="NC", census_geoid="00")

    assert s.status() == StateStatus.UNKNOWN

    s.task_files = False
    s.task_digitization = False
    s.task_verification = False
    s.task_published = False

    assert s.status() == StateStatus.IN_PROGRESS

    s.task_files = True
    assert s.status() == StateStatus.COLLECTION_COMPLETE

    s.task_digitization = True
    s.task_verification = True
    s.task_published = True
    assert s.status() == StateStatus.FULLY_COMPLETE
