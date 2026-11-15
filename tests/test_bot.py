import pytest
from unittest.mock import MagicMock
from truco.bot import Bot 
from truco.cbr import Cbr, Dados
import pandas as pd


def criar_carta_mock(naipe, pontos_envido):
    carta = MagicMock()
    carta.retornar_naipe.return_value = naipe
    carta.retornar_pontos_envido.side_effect = lambda c: c._pontos_envido
    carta._pontos_envido = pontos_envido
    return carta

def criar_cbr_com_csv_corrigido(monkeypatch):
    read_csv_original = pd.read_csv
    def read_csv_ajustado(arquivo, *args, **kwargs):
        if "dbtrucoimitacao_maos" in str(arquivo):
            kwargs["sep"] = "\t"
        return read_csv_original(arquivo, *args, **kwargs)
    monkeypatch.setattr(pd, "read_csv", read_csv_ajustado)
    return Cbr()


@pytest.fixture
def bot_com_mao():

    bot = Bot("BotTeste")
    c1 = criar_carta_mock("Espadas", 7)
    c2 = criar_carta_mock("Espadas", 6)
    c3 = criar_carta_mock("Ouros", 1)

    c1.classificar_carta.return_value = ([30, 20, 10], ["Alta", "Media", "Baixa"])

    baralho = MagicMock()
    baralho.retirar_carta.side_effect = [c1, c2, c3]

    bot.criar_mao(baralho)
    return bot

@pytest.fixture
def cbr_real(monkeypatch):
    read_csv_original = pd.read_csv

    def read_csv_ajustado(arquivo, *args, **kwargs):
        if "dbtrucoimitacao_maos" in str(arquivo):
            kwargs["sep"] = "\t"
        return read_csv_original(arquivo, *args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", read_csv_ajustado)

    carta_humano = MagicMock()
    carta_humano.retornar_numero.return_value = 7
    carta_humano.retornar_naipe.return_value = "Espadas"

    ia = Cbr()
    ia.dados.primeira_rodada([30, 20, 10], ["Alta", "Media", "Baixa"], 25.0, carta_humano)
    ia.dados.registro = ia.dados.registro.fillna(0)  # elimina o NaN restante em naipePrimeiraCartaHumano
    ia.dados.registro["qualidadeMaoRobo"] = 25.0
    return ia

# COMEÇO TESTES

# TESTES DE ERROS

# Cbr lê csv de forma errada, pois ele nao esta separado por , padrao
def test_erro_01_leitura_csv_sem_separador_tab():
    ia = Cbr()
    assert not ia.dataset.empty

# grava em 'qualidadeMaoBot' em vez de 'qualidadeMaoRobo', variavel de nome errado sendo chamada
def test_erro_02_primeira_rodada_grava_na_coluna_errada(monkeypatch):

    ia = criar_cbr_com_csv_corrigido(monkeypatch)
    carta_humano = MagicMock()
    carta_humano.retornar_numero.return_value = 7
    carta_humano.retornar_naipe.return_value = "ESPADAS"

    ia.dados.primeira_rodada([30, 20, 10], ["Alta", "Media", "Baixa"], 25.0, carta_humano)

    assert ia.dados.registro["qualidadeMaoRobo"].iloc[0] == 25.0

# Bot joga primeiro, Carta humano foca com None e bot tenta acessar
def test_erro_03_primeira_rodada_quebra_quando_bot_joga_primeiro(monkeypatch):

    ia = criar_cbr_com_csv_corrigido(monkeypatch)
    ia.dados.primeira_rodada([30, 20, 10], ["Alta", "Media", "Baixa"], 25.0, carta_humano=None)
    assert ia.dados.registro["primeiraCartaHumano"].iloc[0] in [0, -100]


# Se os vizinhos forem todos vitorias, o filtro 'perdidas' fica vazio
def test_erro_04_truco_quebra_quando_nao_ha_derrotas_nos_vizinhos(monkeypatch):

    ia = criar_cbr_com_csv_corrigido(monkeypatch)
    ia.dados.registro["qualidadeMaoRobo"] = 25.0
    ia.dataset["quemGanhouTruco"] = 2 

    decisao = ia.truco(tipo="truco", quem_pediu=1, qualidade_mao_bot=25.0)
    assert decisao in [0, 1, 2]

# A classe Bot chama cbr.flor(), mas  Cbr não tem o método flor().
def test_erro_05_cbr_nao_implementa_metodo_flor(monkeypatch):
    """
    Defeito de Contrato: 
    """
    ia = criar_cbr_com_csv_corrigido(monkeypatch)
    assert hasattr(ia, "flor")

# compara rotulos em vez de contagem de casos, mesmo com 1 vitoria em 100 casos ele pede retruco
def test_erro_06_truco_ignora_frequencia_real_de_derrotas(cbr_real):
    _, indices = cbr_real.nbrs.kneighbors(cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1))
    vizinhos_idx = indices[0]

    cbr_real.dataset["quemGanhouTruco"] = 1  # Marca todos como derrota do bot
    cbr_real.dataset.iloc[vizinhos_idx[0], cbr_real.dataset.columns.get_loc("quemGanhouTruco")] = 2  # Apenas 1 vitória

    decisao = cbr_real.truco(tipo="truco", quem_pediu=1, qualidade_mao_bot=35.0)
    assert decisao != 2 

# REGRAS DE ENVIDO E FLOR

def test_calcula_envido_mesmo_naipe_numericas():
    bot = Bot("BotTeste")
    mao = [
        criar_carta_mock("Copas", 7),
        criar_carta_mock("Copas", 6),
        criar_carta_mock("Bastos", 3),  
    ]
    assert bot.calcula_envido(mao) == 33  # 20 + 7 + 6


def test_calcula_envido_mesmo_naipe_com_figura_valor_limite():

    bot = Bot("BotTeste")
    mao = [
        criar_carta_mock("Espadas", 0),  # Figura (Valete/rei...) força 0
        criar_carta_mock("Espadas", 7),
        criar_carta_mock("Ouros", 4),
    ]
    assert bot.calcula_envido(mao) == 27


def test_checa_flor_tres_cartas_mesmo_naipe():
    bot = Bot("BotTeste")
    bot.mao = [
        criar_carta_mock("Bastos", 1),
        criar_carta_mock("Bastos", 5),
        criar_carta_mock("Bastos", 0),
    ]
    assert bot.checa_flor() is True


# INTERAÇÃO COM MOCK

def test_jogar_carta_fluxo_normal_atualiza_estado(bot_com_mao):
    cbr_mock = MagicMock()
    cbr_mock.jogar_carta.return_value = 0  # Escolhe índice 0

    escolha = bot_com_mao.jogar_carta(cbr_mock, truco=None)

    assert escolha == 0
    assert bot_com_mao.rodada == 2
    assert len(bot_com_mao.indices) == 2
    assert len(bot_com_mao.pontuacao_cartas) == 2
    cbr_mock.jogar_carta.assert_called_once_with(1, [20, 10])


def test_jogar_carta_deve_cantar_flor_quando_tiver_flor():
 
    bot = Bot("BotTeste")
    c1 = criar_carta_mock("Ouros", 7)
    c2 = criar_carta_mock("Ouros", 6)
    c3 = criar_carta_mock("Ouros", 5)
    c1.classificar_carta.return_value = ([25, 20, 15], ["Alta", "Media", "Baixa"])

    baralho = MagicMock()
    baralho.retirar_carta.side_effect = [c1, c2, c3]
    bot.criar_mao(baralho)

    cbr_mock = MagicMock()
    cbr_mock.flor.return_value = True

    acao = bot.jogar_carta(cbr_mock, truco=None)
    assert acao == 5  # Código para Flor


def test_avaliar_envido_define_flag_perdendo_no_limite():
    bot = Bot("BotTeste")
    bot.pontos = 6
    bot.envido = 28
    cbr_mock = MagicMock()

    bot.avaliar_envido(cbr_mock, tipo=6, quem_pediu=1, pontos_totais_adversario=6)
    cbr_mock.envido.assert_called_with(6, 1, 28, True)

    bot.avaliar_envido(cbr_mock, tipo=6, quem_pediu=1, pontos_totais_adversario=4)
    cbr_mock.envido.assert_called_with(6, 1, 28, False)


# TRANSIÇÃO DE ESTADO E RESET 

def test_enriquecer_bot_roteia_para_metodo_correto_por_rodada(bot_com_mao):
    dados_mock = MagicMock()

    bot_com_mao.rodada = 1
    bot_com_mao.enriquecer_bot(dados=dados_mock, carta_jogador_01="7_espadas")
    dados_mock.primeira_rodada.assert_called_once()

    bot_com_mao.rodada = 2
    bot_com_mao.enriquecer_bot(dados=dados_mock, carta_jogador_01="3_ouros", carta_jogador_02="1_espadas", ganhador=2)
    dados_mock.segunda_rodada.assert_called_once_with("3_ouros", "1_espadas", 2)


def test_resetar_restaura_estado_inicial(bot_com_mao):
    bot_com_mao.pediu_truco = True
    bot_com_mao.rodada = 3
    bot_com_mao.adicionar_pontos(5)

    bot_com_mao.resetar()

    assert bot_com_mao.mao == []
    assert bot_com_mao.rodada == 1
    assert bot_com_mao.pediu_truco is False
    # Pontos sem zerar
    assert bot_com_mao.retorna_pontos_totais() == 5


# Test numeros variaveis de qualidade

def test_fronteira_decisao_sem_oscilacao_absurda(cbr_real):
    decisoes = []
    for q in range(1, 36):
        cbr_real.dados.registro["qualidadeMaoRobo"] = float(q)
        decisoes.append(cbr_real.truco(tipo="truco", quem_pediu=1, qualidade_mao_bot=float(q)))

    # Nas 5 faixas mais fortes do jogo, a IA deve aceitar 1 ou aumentar 2
    assert all(d in [1, 2] for d in decisoes[-5:])

# Testes do Funcionamento do CBR

# com o mesmo estado, deve ter a mesam decisão
def test_ia_determinismo_mesmo_estado_gera_mesma_decisao(cbr_real):
 
    decisao_truco_1 = cbr_real.truco("truco", 1, 28.0)
    decisao_truco_2 = cbr_real.truco("truco", 1, 28.0)

    decisao_envido_1 = cbr_real.envido(6, 1, 29, False)
    decisao_envido_2 = cbr_real.envido(6, 1, 29, False)

    assert decisao_truco_1 == decisao_truco_2
    assert decisao_envido_1 == decisao_envido_2


# trocar de estado, vizinhos do KNN devem mudar
def test_ia_recuperacao_casos_muda_vizinhos_conforme_contexto_partida(cbr_real):

    registro_inicial = cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1)
    _, vizinhos_antes = cbr_real.nbrs.kneighbors(registro_inicial)

    # bot venceu a 1 rodada
    cbr_real.dados.registro["ganhadorPrimeiraRodada"] = 2
    cbr_real.dados.registro["cartaAltaRobo"] = 52
    cbr_real.dados.registro["qualidadeMaoRobo"] = 34.0

    registro_atualizado = cbr_real.dados.retornar_registro().to_numpy().reshape(1, -1)
    _, vizinhos_depois = cbr_real.nbrs.kneighbors(registro_atualizado)

    assert list(vizinhos_antes[0]) != list(vizinhos_depois[0])

# Se tiver cartas fortes, nao foge
def test_ia_truco_mao_dominante_nas_tres_instancias_aposta(cbr_real):

    cbr_real.dados.registro["cartaAltaRobo"] = 52
    cbr_real.dados.registro["cartaMediaRobo"] = 50
    cbr_real.dados.registro["cartaBaixaRobo"] = 42
    cbr_real.dados.registro["qualidadeMaoRobo"] = 35.0

    for instancia in ["truco", "retruco", "vale_quatro"]:
        decisao = cbr_real.truco(instancia, 1, 35.0)
        assert decisao in [1, 2]