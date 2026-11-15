import runpy

import pytest

NAIPES = {"E": "ESPADAS", "O": "OUROS", "C": "COPAS", "B": "BASTOS"}


class CbrFalso:
    def __init__(self, truco=(), envido=()):
        self._truco = list(truco)
        self._envido = list(envido)

    def flor(self):
        return False

    def truco(self, tipo, quem_pediu, qualidade):
        return self._truco.pop(0) if self._truco else None

    def envido(self, tipo, quem_pediu, pontos, perdendo):
        return self._envido.pop(0) if self._envido else 0

    def jogar_carta(self, rodada, pontuacao_cartas):
        return 0


class DadosFalso:
    def __getattr__(self, nome):
        return lambda *a, **k: None


@pytest.fixture
def rodar_main(monkeypatch):
    def _rodar(deck, entradas, truco=(), envido=()):
        fila = list(entradas)

        def entrada(*_a, **_k):
            if not fila:
                raise EOFError
            return fila.pop(0)

        def embaralhar(lista):
            desejadas = []
            for codigo in deck:
                for c in lista:
                    if (c.numero, c.naipe) == (int(codigo[:-1]), NAIPES[codigo[-1]]):
                        desejadas.append(c)
            resto = [c for c in lista if c not in desejadas]
            lista[:] = resto + desejadas[::-1]  # pop() tira na ordem

        from truco.jogo import Jogo

        criados = []
        for nome in ("criar_jogador", "criar_bot"):
            original = getattr(Jogo, nome)

            def embrulho(self, *a, _o=original, **k):
                j = _o(self, *a, **k)
                criados.append(j)
                return j

            monkeypatch.setattr(Jogo, nome, embrulho)

        monkeypatch.setattr("builtins.input", entrada)
        monkeypatch.setattr("random.shuffle", embaralhar)
        monkeypatch.setattr("truco.cbr.Cbr", lambda: CbrFalso(truco, envido))
        monkeypatch.setattr("truco.dados.Dados", DadosFalso)
        with pytest.raises(EOFError):
            runpy.run_module("truco.__main__", run_name="__main__")
        humano, bot = criados
        return humano, bot

    return _rodar


NOMES = ["Ana", "Bot"]


# humano vence
@pytest.mark.e2e
@pytest.mark.req
def test_uc02_humano_vence_a_mao(rodar_main):
    humano, bot = rodar_main(["1E", "7E", "3C", "4O", "5C", "6B"], NOMES + ["0", "0"])
    assert (humano.pontos, bot.pontos) == (1, 0)


# humano perde 
@pytest.mark.e2e
@pytest.mark.req
def test_uc03_humano_perde_a_mao(rodar_main):
    humano, bot = rodar_main(["4O", "5C", "6B", "1E", "7E", "3C"], NOMES + ["0", "0"])
    assert (humano.pontos, bot.pontos) == (0, 1)


# bot vence a mão. Hoje o empate vira vitória do humano e a 3ª rodada o favorece.
@pytest.mark.e2e
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-03: empate de cartas não vira parda")
def test_uc05_parda_na_primeira_rodada(rodar_main):
    humano, bot = rodar_main(["3C", "4O", "7E", "3O", "5B", "6B"], NOMES + ["0", "0", "0"])
    assert (humano.pontos, bot.pontos) == (0, 1)


# humano vai ao baralho na 1 rodada
@pytest.mark.e2e
@pytest.mark.req
def test_uc09_humano_vai_ao_baralho(rodar_main):
    humano, bot = rodar_main(["1E", "7E", "3C", "4O", "5C", "6B"], NOMES + ["9"])
    assert (humano.pontos, bot.pontos) == (0, 1)


# truco recusado pelo bot dá 1 ponto
@pytest.mark.e2e
@pytest.mark.req
def test_uc10_truco_recusado(rodar_main):
    humano, bot = rodar_main(["4O", "5C", "6B", "1E", "7E", "3C"], NOMES + ["4"], truco=[0])
    assert (humano.pontos, bot.pontos) == (1, 0)


# truco aceito e humano vence
@pytest.mark.e2e
@pytest.mark.req
@pytest.mark.xfail(strict=True, reason="DEF-04: valor da mão não sobe para 2")
def test_uc11_truco_aceito_vale_dois(rodar_main):
    humano, bot = rodar_main(
        ["1E", "7E", "3C", "4O", "5C", "6B"], NOMES + ["4", "0", "0"], truco=[1]
    )
    assert (humano.pontos, bot.pontos) == (2, 0)


# envido humano vence
@pytest.mark.e2e
@pytest.mark.req
def test_uc13_envido_do_humano_vence(rodar_main):
    humano, bot = rodar_main(
        ["7E", "6E", "4O", "5C", "4B", "3O"], NOMES + ["6", "0", "0"], envido=[0, 1]
    )
    assert (humano.pontos, bot.pontos) == (2 + 1, 0)
