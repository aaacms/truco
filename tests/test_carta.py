import pytest

from truco.carta import Carta


def test_criar_carta_e_retornar_dados():
    carta = Carta(7, "COPAS")

    assert carta.numero == 7
    assert carta.naipe == "COPAS"
    assert carta.retornar_numero() == 7
    assert carta.retornar_naipe() == "COPAS"
    assert carta.retornar_carta() == "7 de COPAS"
 

@pytest.mark.parametrize("numero, esperado", [
    (1, 12), (2, 16), (3, 24), (4, 1), (5, 2),
    (6, 3), (7, 4), (10, 6), (11, 7), (12, 8),
])
def test_pontos_de_carta_comum(numero, esperado):
    carta = Carta(numero, "COPAS")

    assert carta.retornar_pontos_carta(carta) == esperado


@pytest.mark.parametrize("numero, naipe, esperado", [
    (1, "ESPADAS", 52), (1, "BASTOS", 50),
    (7, "ESPADAS", 42), (7, "OUROS", 40),
])
def test_pontos_de_manilha(numero, naipe, esperado):
    carta = Carta(numero, naipe)

    assert carta.retornar_pontos_carta(carta) == esperado


@pytest.mark.parametrize("menor, maior", [
    ((4, "COPAS"), (3, "COPAS")),
    ((3, "COPAS"), (7, "OUROS")),
    ((7, "OUROS"), (7, "ESPADAS")),
    ((7, "ESPADAS"), (1, "BASTOS")),
    ((1, "BASTOS"), (1, "ESPADAS")),
])
def test_comparar_cartas_nas_duas_ordens(menor, maior):
    baixa = Carta(*menor)
    alta = Carta(*maior)

    assert baixa.verificar_carta_alta(baixa, alta) is alta
    assert baixa.verificar_carta_alta(alta, baixa) is alta
    assert baixa.verificar_carta_baixa(baixa, alta) is baixa
    assert baixa.verificar_carta_baixa(alta, baixa) is baixa


def test_comparar_manilha_com_ela_mesma():
    carta = Carta(1, "ESPADAS")

    assert carta.verificar_carta_alta(carta, carta) is carta
    assert carta.verificar_carta_baixa(carta, carta) is carta


@pytest.mark.parametrize("numeros, pontos, classificacao", [
    ([3, 6, 4], [24, 3, 1], ["Alta", "Media", "Baixa"]),
    ([4, 3, 6], [1, 24, 3], ["Baixa", "Alta", "Media"]),
    ([6, 4, 3], [3, 1, 24], ["Media", "Baixa", "Alta"]),
])
def test_classificar_tres_cartas(numeros, pontos, classificacao):
    cartas = [Carta(numero, "COPAS") for numero in numeros]

    resultado = cartas[0].classificar_carta(cartas)

    assert resultado == (pontos, classificacao)


@pytest.mark.parametrize("numero, esperado", [
    (1, 1), (2, 2), (3, 3), (4, 4), (5, 5),
    (6, 6), (7, 7), (10, 0), (11, 0), (12, 0),
])
def test_pontos_de_envido(numero, esperado):
    carta = Carta(numero, "COPAS")

    assert carta.retornar_pontos_envido(carta) == esperado


@pytest.mark.parametrize("naipe, codigo", [
    ("ESPADAS", 1), ("OUROS", 2), ("BASTOS", 3), ("COPAS", 4),
])
def test_codificar_naipe(naipe, codigo):
    carta = Carta(4, naipe)

    assert carta.retornar_naipe_codificado() == codigo


@pytest.mark.parametrize("indice, esperado", [
    (None, "[] 7 de COPAS\n"), (0, "[0] 7 de COPAS\n"),
])
def test_exibir_carta(indice, esperado, capsys):
    carta = Carta(7, "COPAS")

    carta.exibir_carta(indice)

    assert capsys.readouterr().out == esperado
