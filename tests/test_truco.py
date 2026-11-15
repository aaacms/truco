import pytest

from truco.truco import Truco


class JogadorFalso:

    def __init__(self, respostas=()):
        self.pontos = 0
        self.pediu_truco = False
        self._respostas = list(respostas)

    def avaliar_truco(self, cbr, estado, quem_pediu):
        return self._respostas.pop(0)


@pytest.fixture
def truco():
    return Truco()


@pytest.fixture
def entradas(monkeypatch):
    # entradas('1', '0'), próximos input() devolve 1, 0.

    def _definir(*valores):
        fila = list(valores)
        monkeypatch.setattr("builtins.input", lambda *_a, **_k: fila.pop(0))
        return fila

    return _definir


def humano_e_bot(*respostas_bot):
    return JogadorFalso(), JogadorFalso(respostas_bot)


# estado inicial
@pytest.mark.ret
def test_tru01_estado_inicial(truco):
    assert truco.valor_aposta == 1
    assert truco.estado_atual == ""
    assert truco.jogador_bloqueado == 0


# truco aceito deve valer 2
@pytest.mark.req
@pytest.mark.ret
@pytest.mark.xfail(strict=True, reason="DEF-04: valor da mão não sobe para 2 no truco aceito")
def test_tru02_truco_aceito_vale_dois(truco):
    j1, j2 = humano_e_bot(1)
    assert truco.pedir_truco(None, 1, j1, j2) is True
    assert truco.estado_atual == "truco"
    assert truco.retornar_valor_aposta() == 2


# truco recusado dá 1 ponto a quem cantou
@pytest.mark.req
@pytest.mark.ret
def test_tru03_truco_recusado(truco):
    j1, j2 = humano_e_bot(0)
    assert truco.pedir_truco(None, 1, j1, j2) is False
    assert (j1.pontos, j2.pontos) == (1, 0)


# bot aumenta, humano aceita o Retruco
@pytest.mark.req
def test_tru04_retruco_aceito(truco, entradas):
    entradas("1")
    j1, j2 = humano_e_bot(2)
    assert truco.pedir_truco(None, 1, j1, j2) is True
    assert truco.valor_aposta == 3
    assert truco.estado_atual == "retruco"


#  até o Vale 4 aceito
@pytest.mark.req
def test_tru06_vale_quatro_aceito(truco, entradas):
    entradas("2")
    j1, j2 = humano_e_bot(2, 1)
    assert truco.pedir_truco(None, 1, j1, j2) is True
    assert truco.valor_aposta == 4
    assert j1.pediu_truco is True and j2.pediu_truco is True


# depois do Vale 4 não pode haver novo canto
@pytest.mark.req
@pytest.mark.ifs
@pytest.mark.xfail(strict=True, reason="DEF-05: pedir_vale_quatro não grava estado vale_quatro")
def test_tru09_depois_do_vale_quatro_nao_ha_novo_canto(truco, monkeypatch, entradas):
    entradas("2")
    j1, j2 = humano_e_bot(2, 1)
    assert truco.controlador_truco(None, None, 1, j1, j2) is True
    monkeypatch.setattr("builtins.input", lambda *_a, **_k: "1")
    assert truco.controlador_truco(None, None, 2, j1, j2) is None
    assert truco.valor_aposta == 4


# tabela de decisão de controlador_truco
_DEFEITO_RETRUCO = pytest.mark.xfail(
    strict=True, reason="chama pedir_retruco no estado retruco em vez de pedir_vale_quatro (DEF-34 proposto)"
)


@pytest.mark.ifs
@pytest.mark.call
@pytest.mark.parametrize(
    "estado, bloqueado, esperado",
    [
        ("", True, None),
        ("", False, "pedir_truco"),
        ("truco", True, None),
        ("truco", False, "pedir_retruco"),
        ("retruco", True, None),
        pytest.param("retruco", False, "pedir_vale_quatro", marks=_DEFEITO_RETRUCO),
        ("vale_quatro", True, None),
        ("vale_quatro", False, None),
        ("outro", True, None),
        ("outro", False, None),
    ],
)
def test_tru17_tabela_de_decisao(truco, monkeypatch, estado, bloqueado, esperado):
    chamados = []
    for nome in ("pedir_truco", "pedir_retruco", "pedir_vale_quatro"):
        monkeypatch.setattr(truco, nome, lambda *a, _n=nome, **k: chamados.append(_n) or _n)
    truco.estado_atual = estado
    truco.jogador_bloqueado = 1 if bloqueado else 2
    resultado = truco.controlador_truco(None, None, 1, JogadorFalso(), JogadorFalso())
    assert resultado == esperado
    assert chamados == ([esperado] if esperado else [])
