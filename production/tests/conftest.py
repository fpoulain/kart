import pytest

from people.tests.conftest import *  # noqa
from utils.tests.conftest import *  # noqa

from . import factories


@pytest.fixture
def staff_task(db_ready):
    return factories.StaffTaskFactory()


@pytest.fixture
def production_staff_task(db_ready):
    return factories.ProductionStaffTaskFactory()


@pytest.fixture
def production(db_ready):
    return factories.ProductionFactory()


@pytest.fixture
def anonymous_artwork(db_ready):
    return factories.ArtworkFactory(authors=[])


@pytest.fixture
def artwork(db_ready, artist):
    return factories.ArtworkFactory(authors=[artist])


@pytest.fixture
def film_genre(db_ready):
    return factories.FilmGenreFactory()


@pytest.fixture
def installation_genre(db_ready):
    return factories.InstallationGenreFactory()


@pytest.fixture
def event(db_ready):
    return factories.EventFactory()


@pytest.fixture
def main_event(db_ready, event):
    return factories.EventFactory(main_event=True, subevents=[event])


@pytest.fixture
def itinerary(db_ready):
    return factories.ItineraryFactory()
