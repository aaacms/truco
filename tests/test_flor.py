import pytest

from truco.flor import Flor
from truco.jogador import Jogador


class InterfaceFalsa:
    def __init__(self):
        self.vencedores = []

    def mostrar_vencedor_flor(self, vencedor, *resto):
        self.vencedores.append(vencedor)


def jogador(mk, nome, codigos, flor):
    j = Jogador(nome)
    j.mao = [mk(c) for c in codigos]
    j.envido = j.calcula_envido(j.mao)
    j.flor = flor
    return j


@pytest.fixture
def flor():
    return Flor()


@pytest.fixture
def interface():
    return InterfaceFalsa()


@pytest.fixture
def entradas(monkeypatch):
    def _definir(*valores):
        fila = list(valores)
        monkeypatch.setattr("builtins.input", lambda *_a, **_k: fila.pop(0))

    return _definir


@pytest.fixture
def com_flor(mk):
    return jogador(mk, "Flor", ["7E", "6E", "5E"], True)


@pytest.fixture
def sem_flor(mk):
    return jogador(mk, "Sem", ["1C", "4O", "3B"], False)


# só o bot tem flor
@pytest.mark.req
@pytest.mark.msg
def test_flo01_so_o_bot_tem_flor(flor, interface, sem_flor, com_flor):
    flor.pedir_flor(2, sem_flor, com_flor, interface)
    assert com_flor.pontos == 3 and sem_flor.pontos == 0
    assert flor.quem_venceu_flor == 2
    assert interface.vencedores == [2]


# só o humano tem flor
@pytest.mark.req
def test_flo02_so_o_humano_tem_flor(flor, interface, com_flor, sem_flor):
    flor.pedir_flor(1, com_flor, sem_flor, interface)
    assert com_flor.pontos == 3 and sem_flor.pontos == 0
    assert flor.quem_venceu_flor == 1


# ninguém tem flor
@pytest.mark.req
@pytest.mark.msg
@pytest.mark.xfail(strict=True, reason="DEF-23: imprime vencedor mesmo sem flor")
def test_flo03_ninguem_tem_flor(flor, interface, sem_flor, mk):
    outro = jogador(mk, "Outro", ["2C", "5O", "7B"], False)
    flor.pedir_flor(1, sem_flor, outro, interface)
    assert (sem_flor.pontos, outro.pontos) == (0, 0)
    assert interface.vencedores == []


# contra-flor vence pelos pontos de FLOR 
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-12: compara pontos de envido, não de flor")
def test_flo04_contraflor_vence_maior_flor(flor, interface, entradas, mk):
    entradas("1")
    humano = jogador(mk, "H", ["7E", "6E", "12E"], True)
    bot = jogador(mk, "B", ["7O", "5O", "3O"], True)
    flor.pedir_flor(1, humano, bot, interface)
    assert bot.pontos == 6 and humano.pontos == 0


# recusa da contra-flor dá 3 pontos a quem cantou
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-11: recusa dá 4 pontos ao bot")
def test_flo05_recusa_da_contraflor(flor, interface, entradas, mk):
    entradas("0")
    humano = jogador(mk, "H", ["7E", "6E", "5E"], True)
    bot = jogador(mk, "B", ["7O", "5O", "3O"], True)
    flor.pedir_flor(1, humano, bot, interface)
    assert humano.pontos == 3 and bot.pontos == 0


# segundo pedido de flor na mesma mão é ignorado
@pytest.mark.ifs
def test_flo08_segundo_pedido_ignorado(flor, interface, com_flor, sem_flor):
    flor.pedir_flor(1, com_flor, sem_flor, interface)
    flor.pedir_flor(1, com_flor, sem_flor, interface)
    assert com_flor.pontos == 3
    assert interface.vencedores == [1]
