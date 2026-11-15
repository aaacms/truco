import pytest

from truco.baralho import Baralho
from truco.carta import Carta


def test_criar_baralho_com_quarenta_cartas_unicas():
    baralho = Baralho()
    combinacoes = {(c.numero, c.naipe) for c in baralho.cartas}

    assert len(baralho.cartas) == 40
    assert len(combinacoes) == 40
    assert all(isinstance(c, Carta) for c in baralho.cartas)


@pytest.mark.parametrize("naipe", ["ESPADAS", "OUROS", "COPAS", "BASTOS"])
def test_numeros_de_cada_naipe(naipe):
    baralho = Baralho()

    numeros = sorted(c.numero for c in baralho.cartas if c.naipe == naipe)

    assert numeros == [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]


def test_embaralhar_preserva_as_cartas():
    baralho = Baralho()
    antes = set(baralho.cartas)

    baralho.embaralhar()

    assert len(baralho.cartas) == 40
    assert set(baralho.cartas) == antes


def test_retirar_carta_retorna_a_ultima_e_reduz_baralho():
    baralho = Baralho()
    ultima = baralho.cartas[-1]

    retirada = baralho.retirar_carta()

    assert isinstance(retirada, Carta)
    assert retirada is ultima
    assert len(baralho.cartas) == 39
    assert retirada not in baralho.cartas


def test_retirar_todas_as_cartas_e_tentar_retirar_do_baralho_vazio():
    baralho = Baralho()
    retiradas = []

    for quantidade in range(40, 0, -1):
        retiradas.append(baralho.retirar_carta())
        assert len(baralho.cartas) == quantidade - 1

    assert len(set(retiradas)) == 40
    assert baralho.cartas == []
    with pytest.raises(IndexError):
        baralho.retirar_carta()


def test_resetar_esvazia_listas():
    baralho = Baralho()
    baralho.vira = [baralho.cartas[0]]
    baralho.manilhas = [baralho.cartas[1]]

    baralho.resetar()

    assert baralho.cartas == []
    assert baralho.manilhas == []
    assert baralho.vira == []


@pytest.mark.parametrize("vazio", [False, True])
def test_printar_baralho(vazio, capsys):
    baralho = Baralho()
    if vazio:
        baralho.cartas = []
    antes = list(baralho.cartas)
    esperado = "".join(f"[] {c.numero} de {c.naipe}\n" for c in antes)

    baralho.printar_baralho()

    assert capsys.readouterr().out == esperado
    assert baralho.cartas == antes
