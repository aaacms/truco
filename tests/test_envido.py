import pytest

from truco.envido import Envido


class JogadorFalso:
    def __init__(self, envido=0, respostas=(), pontos=0, nome="J"):
        self.nome = nome
        self.envido = envido
        self.pontos = pontos
        self._respostas = list(respostas)

    def retorna_pontos_envido(self):
        return self.envido

    def avaliar_envido(self, cbr, tipo, quem_pediu, pontos):
        return self._respostas.pop(0)


class InterfaceFalsa:
    def __init__(self):
        self.vencedores = []

    def mostrar_vencedor_envido(self, vencedor, *resto):
        self.vencedores.append(vencedor)


@pytest.fixture
def envido():
    return Envido()


@pytest.fixture
def interface():
    return InterfaceFalsa()


@pytest.fixture
def entradas(monkeypatch):
    def _definir(*valores):
        fila = list(valores)
        monkeypatch.setattr("builtins.input", lambda *_a, **_k: fila.pop(0))

    return _definir


def cantar(envido, interface, tipo, quem, j1, j2):
    return envido.controlador_envido(None, None, tipo, quem, j1, j2, interface)


# testa estado
@pytest.mark.ret
def test_env01_estado_inicial(envido):
    assert envido.valor_envido == 2
    assert envido.estado_atual == 0


# humano vence o envido
@pytest.mark.req
@pytest.mark.msg
def test_env02_humano_vence_envido(envido, interface):
    j1, j2 = JogadorFalso(30), JogadorFalso(20, [1])
    cantar(envido, interface, 6, 1, j1, j2)
    assert (j1.pontos, j2.pontos) == (2, 0)
    assert envido.quem_venceu_envido == 1
    assert interface.vencedores == [1]


# bot vence envido
@pytest.mark.req
def test_env03_bot_vence_envido(envido, interface):
    j1, j2 = JogadorFalso(20), JogadorFalso(28, [1])
    cantar(envido, interface, 6, 1, j1, j2)
    assert (j1.pontos, j2.pontos) == (0, 2)
    assert interface.vencedores == [2]


# empate vence o "mão"
@pytest.mark.req
@pytest.mark.call
@pytest.mark.parametrize(
    "mao",
    [
        1,
        pytest.param(2, marks=pytest.mark.xfail(strict=True, reason="DEF-07: empate sempre favorece o humano")),
    ],
)
def test_env04_empate_vence_o_mao(envido, interface, mao):
    j1, j2 = JogadorFalso(25), JogadorFalso(25, [1])
    cantar(envido, interface, 6, 1, j1, j2)
    assert envido.quem_venceu_envido == mao


# bot recusa, humano ganha 1 ponto
@pytest.mark.ifs
@pytest.mark.ret
def test_env05_bot_recusa(envido, interface):
    j1, j2 = JogadorFalso(30), JogadorFalso(20, [0])
    cantar(envido, interface, 6, 1, j1, j2)
    assert (j1.pontos, j2.pontos) == (1, 0)
    assert envido.quem_fugiu == 2
    assert interface.vencedores == []


# bot canta e o humano recusa
@pytest.mark.input_
def test_env06_humano_recusa_envido_do_bot(envido, interface, entradas):
    entradas("0")
    j1, j2 = JogadorFalso(30), JogadorFalso(20)
    cantar(envido, interface, 6, 2, j1, j2)
    assert (j1.pontos, j2.pontos) == (0, 1)
    assert envido.quem_fugiu == 1


# Real Envido direto aceito vale 3
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-08: Real Envido direto vale 5")
def test_env07_real_envido_direto_vale_tres(envido, interface):
    j1, j2 = JogadorFalso(30), JogadorFalso(20, [1])
    cantar(envido, interface, 7, 1, j1, j2)
    assert j1.pontos == 3


# Falta Envido vale 30 menos os pontos do líder (5 x 3 => 25)
@pytest.mark.req
@pytest.mark.call
@pytest.mark.xfail(strict=True, reason="DEF-09: falta calculada sobre 12 e sobre o adversário")
def test_env11_falta_envido_vale_30_menos_lider(envido, interface):
    j1, j2 = JogadorFalso(30, pontos=5), JogadorFalso(20, [1], pontos=3)
    cantar(envido, interface, 8, 1, j1, j2)
    assert j1.pontos == 5 + 25


# só um canto de envido por mão
@pytest.mark.ifs
@pytest.mark.ret
def test_env13_segundo_canto_ignorado(envido, interface):
    j1, j2 = JogadorFalso(30), JogadorFalso(20, [1])
    cantar(envido, interface, 6, 1, j1, j2)
    pontos = (j1.pontos, j2.pontos)
    assert cantar(envido, interface, 7, 2, j1, j2) is None
    assert (j1.pontos, j2.pontos) == pontos
