import pathlib

import pytest

from truco.baralho import Baralho
from truco.interface import Interface
from truco.jogador import Jogador
from truco.jogo import Jogo


@pytest.fixture
def jogo():
    return Jogo()


@pytest.fixture
def jogadores():
    return Jogador("A"), Jogador("B")



@pytest.mark.req
@pytest.mark.call
@pytest.mark.ret
@pytest.mark.parametrize(
    "a, b, vencedora",
    [
        ("1E", "1B", "1E"),   # manilha x manilha
        ("7E", "7O", "7E"),
        ("1B", "7E", "1B"),
        ("1E", "3C", "1E"),   # manilha x comum
        ("7O", "2C", "7O"),
        ("3C", "2O", "3C"),   # comum x comum
        ("12C", "11O", "12C"),
        ("4C", "5O", "5O"),
    ],
)
def test_jog01_carta_vencedora(jogo, mk, a, b, vencedora):
    ca, cb = mk(a), mk(b)
    esperada = ca if vencedora == a else cb
    assert jogo.verificar_carta_vencedora(ca, cb) is esperada
    assert jogo.verificar_carta_vencedora(cb, ca) is esperada


# (parda)
@pytest.mark.req
@pytest.mark.ret
@pytest.mark.xfail(strict=True, reason="DEF-03: parda não existe, devolve a 1ª carta")
@pytest.mark.parametrize("a, b", [("3C", "3O"), ("7C", "7B"), ("12E", "12O")])
def test_jog02_empate_vira_parda(jogo, mk, a, b):
    resultado = jogo.verificar_carta_vencedora(mk(a), mk(b))
    assert resultado is None or resultado == "Empate"


# verifica ganhador
@pytest.mark.ret
@pytest.mark.msg
def test_jog03_verificar_ganhador_devolve_e_imprime(jogo, mk, capsys):
    c1, c2 = mk("1E"), mk("3C")
    assert jogo.verificar_ganhador(c1, c2, Interface()) is c1
    assert "Carta ganhadora: 1 de ESPADAS" in capsys.readouterr().out


# adiciona rodada
@pytest.mark.ifs
@pytest.mark.ret
def test_jog04_adicionar_rodada(jogo, jogadores, mk):
    j1, j2 = jogadores
    c1, c2 = mk("3C"), mk("2O")

    assert jogo.adicionar_rodada(j1, j2, c1, c2, c1) == 1
    assert (j1.rodadas, j2.rodadas) == (1, 0)

    assert jogo.adicionar_rodada(j1, j2, c1, c2, c2) == 2
    assert (j1.rodadas, j2.rodadas) == (1, 1)

    assert jogo.adicionar_rodada(j1, j2, c1, c2, mk("4C")) == "Erro"
    assert (j1.rodadas, j2.rodadas) == (1, 1)


# primeiro jogador
@pytest.mark.ifs
def test_jog05_quem_joga_primeiro(jogo, jogadores, mk):
    j1, j2 = jogadores
    c1, c2 = mk("3C"), mk("2O")

    jogo.quem_joga_primeiro(j1, j2, c1, c2, c1)
    assert (j1.primeiro, j2.primeiro) == (True, False)

    jogo.quem_joga_primeiro(j1, j2, c1, c2, c2)
    assert (j1.primeiro, j2.primeiro) == (False, True)


@pytest.mark.ifs
@pytest.mark.parametrize(
    "r1, r2, ultimo, primeiro_esperado",
    [
        (0, 0, 1, (True, False)),   # j1 foi o último -> j1 abre
        (0, 0, 2, (False, True)),   # j2 foi o último -> j2 abre
        (1, 0, 1, (False, False)),  # com rodada jogada, nada muda
        (0, 1, 2, (False, False)),
    ],
)
def test_jog06_quem_inicia_rodada(jogo, jogadores, r1, r2, ultimo, primeiro_esperado):
    j1, j2 = jogadores
    j1.rodadas, j2.rodadas = r1, r2
    (j1 if ultimo == 1 else j2).ultimo = True
    jogo.quem_inicia_rodada(j1, j2)
    assert (j1.primeiro, j2.primeiro) == primeiro_esperado


# fuga de jogador, mantem mao
@pytest.mark.req
@pytest.mark.msg
def test_jog07_fuga_do_j2_mantem_j1_como_mao(jogo, jogadores, capsys):
    j1, j2 = jogadores
    jogo.jogador_fugiu(j2, j1, j2, 1)
    assert "Jogador fugiu!" in capsys.readouterr().out
    assert (j1.primeiro, j2.primeiro) == (True, False)


# jogador fugiu, passou mao
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF: jogador_fugiu sempre define j1 como mão")
def test_jog07_fuga_do_j1_passa_a_mao_ao_j2(jogo, jogadores):
    j1, j2 = jogadores
    jogo.jogador_fugiu(j1, j1, j2, 1)
    assert (j1.primeiro, j2.primeiro) == (False, True)


# baralho cheio
@pytest.mark.call
@pytest.mark.parametrize("criar", ["criar_jogador", "criar_bot"])
def test_jog08_criar_com_baralho_cheio(jogo, criar):
    baralho = Baralho()
    ator = getattr(jogo, criar)("X", baralho)
    assert ator.nome == "X"
    assert len(ator.mao) == 3
    assert len(baralho.cartas) == 37


# 2 cartas baralho
@pytest.mark.exc
@pytest.mark.parametrize("criar", ["criar_jogador", "criar_bot"])
def test_jog08_criar_com_baralho_de_2_cartas(jogo, criar):
    baralho = Baralho()
    baralho.cartas = baralho.cartas[:2]
    with pytest.raises(IndexError):
        getattr(jogo, criar)("X", baralho)


# estado inicial
@pytest.mark.ret
def test_jog09_estado_inicial(jogo):
    assert jogo.rodadas == []
    assert jogo.trucoPontos == 1


# alternar entre maos
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-21: __main__ nunca chama quem_inicia_rodada")
def test_jog10_main_alterna_a_mao():
    fonte = (pathlib.Path(__file__).parent.parent / "truco" / "__main__.py").read_text()
    assert "quem_inicia_rodada" in fonte
