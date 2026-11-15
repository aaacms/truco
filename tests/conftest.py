import pytest

from truco.carta import Carta


def carta(codigo):
    naipes = {"E": "ESPADAS", "O": "OUROS", "C": "COPAS", "B": "BASTOS"}
    return Carta(int(codigo[:-1]), naipes[codigo[-1]])


@pytest.fixture
def mk():
    return carta
