import pytest

from truco.baralho import Baralho
from truco.carta import Carta
from truco.jogador import Jogador


def test_criar_jogador():
    jogador = Jogador("Ana")

    assert jogador.nome == "Ana"
    assert jogador.mao == []
    assert jogador.mao_rank == []
    assert jogador.pontos == 0
    assert jogador.rodadas == 0
    assert jogador.envido == 0
    assert jogador.primeiro is False
    assert jogador.ultimo is False
    assert jogador.flor is False
    assert jogador.pediu_flor is False
    assert jogador.pediu_truco is False


def test_criar_mao_retira_tres_cartas_e_calcula_envido():
    jogador = Jogador("Ana")
    baralho = Baralho()
    baralho.cartas = [Carta(4, "OUROS"), Carta(6, "COPAS"), Carta(7, "COPAS")]
    cartas = list(baralho.cartas)

    jogador.criar_mao(baralho)

    assert jogador.mao == list(reversed(cartas))
    assert baralho.cartas == []
    assert jogador.envido == 33
    assert jogador.retorna_pontos_envido() == 33


def test_criar_mao_com_baralho_completo():
    jogador = Jogador("Ana")
    baralho = Baralho()

    jogador.criar_mao(baralho)

    assert len(jogador.mao) == 3
    assert len(baralho.cartas) == 37
    assert all(c not in baralho.cartas for c in jogador.mao)


@pytest.mark.parametrize("indice", [0, 1, 2, -1])
def test_jogar_carta_por_indice(indice):
    jogador = Jogador("Ana")
    cartas = [Carta(4, "COPAS"), Carta(5, "OUROS"), Carta(6, "BASTOS")]
    jogador.mao = list(cartas)
    escolhida = cartas[indice]

    resultado = jogador.jogar_carta(indice)

    assert resultado is escolhida
    assert jogador.mao == [c for c in cartas if c is not escolhida]


@pytest.mark.parametrize("indice", [3, 5, -4])
def test_jogar_carta_com_indice_invalido(indice):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(4, "COPAS"), Carta(5, "OUROS"), Carta(6, "BASTOS")]
    antes = list(jogador.mao)

    with pytest.raises(IndexError):
        jogador.jogar_carta(indice)

    assert jogador.mao == antes


def test_jogar_carta_com_mao_vazia():
    jogador = Jogador("Ana")

    with pytest.raises(IndexError):
        jogador.jogar_carta(0)


@pytest.mark.parametrize("pontos", [0, 1, 3, 30])
def test_adicionar_pontos_e_retornar_total(pontos):
    jogador = Jogador("Ana")
    jogador.pontos = 5

    jogador.adicionar_pontos(pontos)

    assert jogador.pontos == 5 + pontos
    assert jogador.retorna_pontos_totais() == 5 + pontos


def test_adicionar_rodadas():
    jogador = Jogador("Ana")

    jogador.adicionar_rodada()
    assert jogador.rodadas == 1
    jogador.adicionar_rodada()
    assert jogador.rodadas == 2


@pytest.mark.parametrize("numeros", [[], [4], [4, 5, 6]])
def test_checar_mao(numeros):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(n, "COPAS") for n in numeros]

    assert jogador.checa_mao() is jogador.mao
    assert [c.numero for c in jogador.checa_mao()] == numeros


@pytest.mark.parametrize("dados, esperado", [
    ([(7, "COPAS"), (6, "COPAS"), (4, "OUROS")], 33),
    ([(7, "COPAS"), (4, "OUROS"), (6, "COPAS")], 33),
    ([(4, "OUROS"), (7, "COPAS"), (6, "COPAS")], 33),
    ([(5, "COPAS"), (7, "COPAS"), (6, "COPAS")], 33),
    ([(4, "COPAS"), (6, "OUROS"), (7, "BASTOS")], 7),
    ([(10, "COPAS"), (11, "OUROS"), (12, "BASTOS")], 0),
])
def test_calcular_envido(dados, esperado):
    jogador = Jogador("Ana")
    mao = [Carta(numero, naipe) for numero, naipe in dados]

    assert jogador.calcula_envido(mao) == esperado


@pytest.mark.xfail(strict=True, reason="Par com figura perde os 20 pontos no calcula_envido")
@pytest.mark.parametrize("numeros, esperado", [([7, 10], 27), ([10, 7], 27), ([10, 11], 20)])
def test_envido_com_figura_do_mesmo_naipe(numeros, esperado):
    jogador = Jogador("Ana")
    mao = [Carta(n, "COPAS") for n in numeros] + [Carta(4, "OUROS")]

    assert jogador.calcula_envido(mao) == esperado


@pytest.mark.parametrize("numeros", [[], [7]])
def test_envido_sem_par_de_cartas_lanca_erro(numeros):
    jogador = Jogador("Ana")
    mao = [Carta(n, "COPAS") for n in numeros]

    with pytest.raises(ValueError):
        jogador.calcula_envido(mao)


@pytest.mark.parametrize("naipes, esperado", [
    (["COPAS", "COPAS", "COPAS"], True),
    (["OUROS", "COPAS", "COPAS"], False),
    (["COPAS", "OUROS", "COPAS"], False),
    (["COPAS", "COPAS", "OUROS"], False),
    (["COPAS", "OUROS", "BASTOS"], False),
])
def test_detectar_flor(naipes, esperado):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(4, naipe) for naipe in naipes]

    assert jogador.checa_flor() is esperado


def test_resetar_limpa_rodada_e_preserva_pontos_da_partida():
    jogador = Jogador("Ana")
    jogador.mao = [Carta(7, "COPAS")]
    jogador.pontos = 10
    jogador.rodadas = 2
    jogador.flor = True
    jogador.pediu_truco = True

    jogador.resetar()

    assert jogador.mao == []
    assert jogador.rodadas == 0
    assert jogador.flor is False
    assert jogador.pediu_truco is False
    assert jogador.pontos == 10
    assert jogador.nome == "Ana"


@pytest.mark.parametrize("numeros, esperado", [
    ([], ""),
    ([4], "[0] 4 de COPAS\n"),
    ([4, 5, 6], "[0] 4 de COPAS\n[1] 5 de COPAS\n[2] 6 de COPAS\n"),
])
def test_mostrar_mao(numeros, esperado, capsys):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(n, "COPAS") for n in numeros]
    antes = list(jogador.mao)

    jogador.mostrar_mao(None)

    assert capsys.readouterr().out == esperado
    assert jogador.mao == antes


@pytest.mark.parametrize(
    "naipes, pediu_truco, flor_anterior, opcoes", [
        ([], False, False, [9]),
        (["COPAS"], False, False, [9]),
        (["COPAS", "OUROS"], False, False, [4, 9]),
        (["COPAS", "OUROS"], True, False, [9]),
        (["COPAS", "OUROS", "BASTOS"], False, False, [4, 6, 7, 8, 9]),
        (["COPAS", "OUROS", "BASTOS"], True, False, [6, 7, 8, 9]),
        (["COPAS", "COPAS", "COPAS"], False, False, [4, 5, 6, 7, 8, 9]),
        (["COPAS", "COPAS", "COPAS"], True, False, [5, 6, 7, 8, 9]),
        (["COPAS", "COPAS", "COPAS"], False, True, [4, 6, 7, 8, 9]),
    ],
)
def test_mostrar_opcoes(naipes, pediu_truco, flor_anterior, opcoes, capsys):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(4 + i, naipe) for i, naipe in enumerate(naipes)]
    jogador.pediu_truco = pediu_truco
    jogador.flor = flor_anterior
    antes = list(jogador.mao)
    mensagens = {
        4: "[4] Truco", 5: "[5] Flor", 6: "[6] Envido",
        7: "[7] Real Envido", 8: "[8] Falta Envido", 9: "[9] Ir ao baralho",
    }
    linhas_cartas = [f"[{i}] {4 + i} de {naipe}" for i, naipe in enumerate(naipes)]
    esperado = "\n".join(linhas_cartas + [mensagens[opcao] for opcao in opcoes]) + "\n"

    jogador.mostrar_opcoes(None)

    assert capsys.readouterr().out == esperado
    assert jogador.flor is (flor_anterior or 5 in opcoes)
    assert jogador.pediu_truco is pediu_truco
    assert jogador.mao == antes


def test_mostrar_opcoes_nao_repete_flor(capsys):
    jogador = Jogador("Ana")
    jogador.mao = [Carta(n, "COPAS") for n in [4, 5, 6]]

    jogador.mostrar_opcoes(None)
    primeira_exibicao = capsys.readouterr().out
    jogador.mostrar_opcoes(None)
    segunda_exibicao = capsys.readouterr().out

    assert "[5] Flor\n" in primeira_exibicao
    assert segunda_exibicao == primeira_exibicao.replace("[5] Flor\n", "")
    assert jogador.flor is True
