# Cenários de Teste — Truco Gaudério com CBR

**Disciplina:** Qualidade de Software 2026/02 — Trabalho “Teste Automatizado de Software”
**Sistema sob teste (SUT):** pacote `truco/` (Python) · **Ferramenta:** `pytest` (+ `pytest-cov` opcional)
**Documento base:** [`requisitos.md`](requisitos.md) (IDs `RF-xx` / `RNF-xx`) · **Versão:** 1.0 · 2026-11-05

> O objetivo do trabalho **não é alterar o jogo**, e sim definir, implementar e executar testes automatizados. Os cenários abaixo tratam o código como entregue; quando ele diverge do requisito, o teste é escrito contra o **requisito** (oráculo) e a divergência vira um **defeito catalogado** (seção 3), marcado no pytest com `xfail(strict=True)`.

---

## 1. Estratégia e ambiente de teste

### 1.1 Princípios
1. **Oráculo = requisitos** (decisão do grupo). Falha esperada ⇒ `@pytest.mark.xfail(strict=True, reason="DEF-nn")`: a suíte fica verde, o relatório mostra `xfailed`, e se alguém corrigir o código o teste vira `XPASS` e quebra a suíte, forçando a remoção da marca.
2. **Sem alterar o código-fonte.** Onde há `input()`/`print()` diretos, usamos `monkeypatch` e `capsys`.
3. **Determinismo:** `random.seed(n)` ou `random.shuffle` substituído por baralho armado; CBR real só em testes de IA; nos demais, um *stub* de CBR.

### 1.2 Estrutura proposta (`<nomes-dos-alunos>testesoftware.zip`)
```
tests/
  conftest.py            # fixtures (abaixo) e registro dos marcadores
  fixtures/base_original.csv   # base separada por vírgula (commit 3b63d88) — ver DEF-01
  test_baralho.py  test_carta.py  test_jogo.py  test_jogador.py
  test_truco.py    test_envido.py test_flor.py  test_bot.py
  test_cbr.py      test_dados.py  test_interface.py
  test_main_entradas.py  test_e2e.py
```
Execução (a partir da **raiz do repositório**, pois o código lê `dbtrucoimitacao_maos.csv` e `modelo_registro.csv` do diretório corrente):
```bash
pytest -v -rxX --tb=short            # execução completa
pytest -m "ia" -v                    # só os testes da IA
pytest --cov=truco --cov-branch --cov-report=term-missing
```

### 1.3 Fixtures e utilitários
| Fixture | Finalidade |
|---|---|
| `cwd_tmp` | Copia os CSV de `tests/fixtures` para um `tmp_path` e faz `chdir` (isola `jogadas.csv` e a leitura da base). |
| `cbr_real` (session) | `Cbr()` com a base original (27.515 casos, ≈3 s). Reutilizada pelos testes de IA. |
| `cbr_sintetico` | `Cbr` construído por `Cbr.__new__` com `dataset`/`nbrs`/`dados` montados à mão (poucas linhas) para **forçar cada ramo** de `truco`, `envido` e `jogar_carta`. |
| `cbr_stub` | Objeto com `truco/envido/jogar_carta/flor` que devolve respostas roteirizadas e registra os argumentos recebidos. |
| `fake_jogador` | Dublê com `avaliar_truco/avaliar_envido` roteirizados, `pontos`, `envido`, `flor`, `pediu_flor`. |
| `entradas(seq)` | `monkeypatch` de `builtins.input` com fila; esgotada ⇒ `EOFError` (detecta *loops* sem fim). |
| `baralho_armado(humano, bot)` | Substitui `random.shuffle` para entregar cartas conhecidas (distribuição: 3 `pop()` do final para o jogador 1, depois 3 para o bot). |
| `rodar_main(seed, entradas, cbr=stub)` | Executa `runpy.run_module('truco', run_name='__main__')` (o módulo roda o jogo ao ser importado) e devolve `(globals, saída, exceção)`. |

### 1.4 Marcadores (um por exigência do enunciado)
`req` (requisito/cenário de uso) · `exc` (exceções) · `msg` (mensagens) · `loop` (início/fim de laço) · `ifs` (combinação de `if`) · `call` (parâmetros variados) · `input_` (entrada do usuário) · `ret` (retorno) · `ia` (CBR/bot) · `e2e`.

### 1.5 Legenda do status previsto
`✔` o código atual deve passar · `✘ DEF-nn` o código atual deve falhar (defeito) · `(c)` confirmado por execução de sondagem · `(p)` previsto por leitura do código (a confirmar ao rodar a suíte).

---

## 2. Cobertura exigida pelo enunciado

| Exigência do professor | Obrig. | Onde está coberta |
|---|:-:|---|
| Validação de requisitos e cenários de uso | ✅ | §4 (marcador `req`) e §5 (casos de uso E2E UC-01…UC-20) |
| Exceções descritas no código | | `exc`: BAR-06, CAR-10/13/16, JGD-04/06, DAD-12/14, CBR-02/04/07/10/11, TRU-12, ENV-16, MAIN-02/03. *(O código não tem `raise`/`try`; as exceções são implícitas — `IndexError`, `KeyError`, `ValueError`, `AttributeError`, `FileNotFoundError`.)* |
| Mensagens de erro | | `msg`: MAIN-02 (“Selecione um valor válido!”), JOG-07, TRU-09/12, ENV-15/21, FLO-03, INT-01…13 |
| Início e fim de *loopings* | | `loop`: BAR-03, TRU-08/12, ENV-16…18, FLO-10, MAIN-02, MAIN-05, JGD-05 (0, 1, 2 e 3 cartas) |
| `if` em encadeamento (cada combinação) | | `ifs`: tabelas de decisão BOT-05, TRU-17, ENV-22, FLO-11, JGD-07, JOG-06, CBR-06, CBR-09, MAIN-02 |
| Chamadas de função com parâmetros variados | ✅ | `call`: `@pytest.mark.parametrize` em CAR-01/07/12, JGD-05, BOT-02/03, ENV-02…12, CBR-05/09/11, INT-12 |
| Entradas do usuário (combinações) | ✅ | `input_`: MAIN-02, TRU-11/12, ENV-16…18, FLO-10, UC-17 |
| Retornos de função | ✅ | `ret`: toda linha com “retorna” (CAR-14, JOG-04, TRU-02…07/13, CBR-05/09/11, BOT-03 …) |
| IA implementada (CBR) | ✅ | §4.10 (CBR-01…22) + BOT-05…13 |
| Outros | | Desempenho (RNF-03), reprodutibilidade por *seed*, regressão de defeitos (`xfail strict`), cobertura de ramos |

---

## 3. Catálogo de defeitos esperados (identificados na análise e em sondagem executada)

| ID | Defeito | Req. violado | Evidência |
|---|---|---|---|
| DEF-01 | `Cbr()` não inicia: `dbtrucoimitacao_maos.csv` no *working tree* está separado por **TAB** (165 cols), mas `cbr.py`/`dados.py` leem com vírgula ⇒ `ValueError: Usecols do not match columns`. Com a base original (vírgula, 27.515 linhas) funciona. | RNF-01/06, RF-52 | (c) |
| DEF-02 | Partida termina em **12 pontos** (`__main__`: `>= 12`) e a falta usa `12 − pontos`; requisito: 30. | RF-01/05 | (c) |
| DEF-03 | **Parda não existe**: empate de carta devolve uma das cartas (`verificar_carta_vencedora` → 1ª; `Carta.verificar_carta_alta` → 2ª); trechos de “Empate” estão comentados. | RF-12/13 | (c) |
| DEF-04 | **Truco aceito não altera o valor da mão** (continua 1; só Retruco=3 e Vale 4=4 atualizam). | RF-23 | (c) |
| DEF-05 | `estado_atual` nunca vira `"vale_quatro"`; após Vale 4 um novo canto reduz a aposta de 4 para 3. | RF-21 | (c) |
| DEF-06 | `Truco.retornar_quem_fugiu()` retorna o **próprio método**, não um jogador. | RNF-04 | (c) |
| DEF-07 | Empate de Envido sempre favorece o jogador 1 (`>=`), não o “mão”. | RF-32 | (c) |
| DEF-08 | Real Envido cantado direto vale 5 (requisito: 3) e, se recusado, dá 2 (requisito: 1). | RF-31/33 | (c) |
| DEF-09 | Falta Envido = `12 − pontos do adversário do cantor` (requisito: falta do líder p/ 30); recusa fixa em 5 (requisito: acumulado+1). | RF-33/34 | (c) |
| DEF-10 | `calcula_envido` (Jogador e Bot): par do mesmo naipe com figura retorna 0 em vez de `20 + carta`; flor só de figuras dá 0 (esperado 20). Ex.: `12E 5E 4O` ⇒ 5 (esperado 25). | RF-32 | (c) |
| DEF-11 | Recusa de Contra-flor concede 4 pontos (requisito: 3). | RF-42 | (c) |
| DEF-12 | “Contra-flor e o resto” não soma a falta (valor fica 3); vencedor da Flor é decidido por pontos de **envido** (par), não pelos 3 cartas (`7E 6E 5E` ⇒ 33 em vez de 38). | RF-42/43 | (c) |
| DEF-13 | Menu do humano com *off-by-one*: opção igual ao nº de cartas (3 com 3 cartas, 2 com 2) chama `pop()` fora do intervalo ⇒ `IndexError`. | RF-10, RNF-02 | (c) `1,3` ⇒ `IndexError` |
| DEF-14 | `Cbr` não tem `flor()` nem `enriquecer_jogadas_bot()`, mas `Bot` os chama ⇒ `AttributeError` (o ramo da flor do bot também é código morto, pois `criar_mao` já seta `flor=True`). | RF-50 | (c) `hasattr`=False |
| DEF-15 | `Dados` escreve em nomes que não são colunas (`quemEnvido`, `quemRealEnvido`, `quemFaltaEnvido`, `SegundaCartaHumano`, `qualidadeMaoBot`) e sobrescreve `terceiraCartaRobo` várias vezes; `flor()` fixa `quemGanhouFlor = 2`. | RF-54/56 | (c) |
| DEF-16 | `Cbr.truco` retorna 1 (= “aceitar”) mas `Bot.jogar_carta` trata 1 como “pedir Truco”. Além disso `vencidas`(2) `> perdidas`(1) é sempre verdadeiro ⇒ o ramo que retorna 1 é inalcançável. | RF-50/51 | (p) |
| DEF-17 | `Cbr.jogar_carta` retorna `-1`; `Bot.ajustar_indices(-1)` remove silenciosamente a **última** carta e o `__main__` trata `-1` como “valor inválido”. | RF-50 | (p) |
| DEF-18 | Saídas de depuração (`print(1)`, `print(2)`, `print(3)`, `print(4)`) poluem o terminal. | RNF-02 | (c) leitura |
| DEF-19 | `Cbr.truco`/`envido` usam `.index.to_list()[0]` sem proteção ⇒ `IndexError` quando os vizinhos não têm casos de vitória/derrota (sem contingência). | RF-53 | (p) |
| DEF-20 | Em `Cbr.envido`, `real_envido_perdidas` lê a coluna `quemPediuFaltaEnvido` (cópia errada de `…RealEnvido`). | RF-51 | (p) |
| DEF-21 | A **alternância do “mão”** não é aplicada: `Jogo.quem_inicia_rodada` nunca é chamado pelo `__main__`. | RF-03 | (c) busca no código |
| DEF-22 | Filtro de “vitórias do bot” em `Cbr.jogar_carta` exige 3ª rodada jogada: vitórias por 2×0 (3ª = −100) não entram. | RF-51/52 | (p) |
| DEF-23 | `mostrar_vencedor_flor/envido` tratam qualquer vencedor ≠ 1 como “Jogador 2” (inclui 0/ninguém/empate). | RF-04 | (c) |
| DEF-24 | Entradas não numéricas (`'abc'`, `''`, `'0.5'`) em qualquer menu levantam `ValueError` (`int(input())` sem tratamento). | RNF-02 | (c) |
| DEF-25 | Pontos podem ultrapassar o placar final (ex.: envido/flor somam além do limite). | RF-06 | (p) |

---

## 4. Cenários por módulo

Colunas: **ID** · **Cenário / entrada** · **Resultado esperado (oráculo)** · **Tipo** · **Req.** · **Status previsto**.

### 4.1 Baralho (`baralho.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| BAR-01 | `Baralho()` recém-criado | `len(cartas) == 40` | req, ret | RF-02 | ✔ (c) |
| BAR-02 | Conteúdo: 4 naipes × `{1..7,10,11,12}` | 10 cartas por naipe; sem 8 e 9 | req | RF-02 | ✔ (p) |
| BAR-03 | *Loop* de criação: nenhuma carta repetida (40 pares únicos) | `len(set(...)) == 40` | loop | RF-02 | ✔ (p) |
| BAR-04 | `embaralhar()` com `seed` fixa duas vezes | mesma permutação; mesmo conjunto; ordem ≠ original | req, call | RF-02 | ✔ (p) |
| BAR-05 | `retirar_carta()` | devolve a **última** carta e reduz o tamanho em 1 | ret | RF-02 | ✔ (p) |
| BAR-06 | Retirar 40 cartas e pedir a 41ª | `IndexError` (baralho vazio) | exc, loop | RF-02 | ✔ (c) |
| BAR-07 | Distribuir 3 cartas ao humano e 3 ao bot | 6 cartas distintas; 34 restantes | req | RF-02 | ✔ (p) |
| BAR-08 | `resetar()` + `criar_baralho()` / `criar_baralho()` duas vezes seguidas | 40 cartas / 80 cartas (duplica — registrar) | call | RF-02 | ✔ (p) |
| BAR-09 | `printar_baralho()` | 40 linhas no formato `[ ] n de NAIPE` | msg | RNF-02 | ✔ (p) |
| BAR-10 | Dois `Baralho()` independentes | embaralhar um não altera o outro | req | RNF-04 | ✔ (p) |

### 4.2 Carta e tabelas de valor (`carta.py`, `pontos.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| CAR-01 | Hierarquia completa, 13 pares adjacentes (`1E>1B>7E>7O>3>2>1>12>11>10>7>6>5>4`), nas duas ordens, `verificar_carta_alta`/`baixa` | a maior/menor correta | req, call, ret | RF-11 | ✔ (p) |
| CAR-02 | Manilhas entre si (6 pares) | `1E > 1B > 7E > 7O` | req | RF-11 | ✔ (p) |
| CAR-03 | Manilha × não manilha (`7O` vs `3C`; `1B` vs `3O`) | manilha vence | req | RF-11 | ✔ (p) |
| CAR-04 | `1` de OUROS/COPAS não é manilha: `1C` vs `12E` e `1C` vs `7O` | `1C` vence o 12; perde da manilha | req | RF-11 | ✔ (p) |
| CAR-05 | `7C`/`7B` não são manilha: `7C` vs `10O` | `10O` vence (4 < 6) | req | RF-11 | ✔ (p) |
| CAR-06 | Empate: `3C` vs `3O` (nas 2 ordens) | resultado “parda” (sem vencedor) | req, ret | RF-12 | ✘ DEF-03 (c) |
| CAR-07 | `retornar_pontos_carta` para as 14 cartas-chave (52,50,42,40,24,16,12,8,7,6,4,3,2,1) | valor da tabela | call, ret | RF-11 | ✔ (p) |
| CAR-08 | `classificar_carta([1E,3C,4O])` | `([52,24,1],[Alta,Media,Baixa])` | ret | RF-50 | ✔ (c) |
| CAR-09 | `classificar_carta([3C,3O,4O])` (valores iguais) | exatamente 1 Alta, 1 Média, 1 Baixa | ret | RF-50 | ✔ (c) |
| CAR-10 | `classificar_carta` com lista de 2 e de 0 cartas | `IndexError` | exc | RF-50 | ✔ (p) |
| CAR-11 | `retornar_carta()`, `exibir_carta()` e `exibir_carta(i)` | `"3 de OUROS"`, `"[ ] 3 de OUROS"`, `"[0] 3 de OUROS"` | msg, ret | RNF-02 | ✔ (p) |
| CAR-12 | `retornar_pontos_envido` p/ números {1,2,3,4,5,6,7,10,11,12} | 1,2,3,4,5,6,7,0,0,0 | call, ret | RF-32 | ✔ (p) |
| CAR-13 | `retornar_pontos_envido` com número inexistente (8, 9) | `KeyError` | exc | RF-32 | ✔ (p) |
| CAR-14 | `retornar_naipe_codificado`: ESPADAS, OUROS, BASTOS, COPAS, “PAUS” | 1, 2, 3, 4, `None` | call, ret | RF-54 | ✔ (p) |
| CAR-15 | Getters `retornar_numero`/`retornar_naipe` | valores do construtor | ret | — | ✔ (p) |
| CAR-16 | `retornar_pontos_carta(Carta(9,'OUROS'))` | `KeyError` | exc | — | ✔ (p) |

### 4.3 Regras de rodada (`jogo.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| JOG-01 | `verificar_carta_vencedora` com 6 pares (manilha×manilha, manilha×comum, comum×comum), 2 ordens | carta maior | req, call, ret | RF-11 | ✔ (p) |
| JOG-02 | Empate (3C × 3O; 7C × 7B; 12E × 12O) | “parda” | req, ret | RF-12 | ✘ DEF-03 (c) |
| JOG-03 | `verificar_ganhador` | devolve a vencedora e imprime `Carta ganhadora: …` | ret, msg | RF-04 | ✔ (p) |
| JOG-04 | `adicionar_rodada` com ganhador = carta1 / carta2 / objeto estranho | retorna `1` e `j1.rodadas+1` / `2` e `j2.rodadas+1` / `"Erro"` sem alterar | ifs, ret | RF-14 | ✔ (p) |
| JOG-05 | `quem_joga_primeiro` (ganhou carta1 / carta2) | flags `primeiro` coerentes | ifs | RF-13 | ✔ (p) |
| JOG-06 | `quem_inicia_rodada`: 4 combinações de (`rodadas==0` ambos?) × (`j1.ultimo` / `j2.ultimo`) | alterna quem é “primeiro” só quando ambos têm 0 rodadas | ifs | RF-03 | ✔ (p) |
| JOG-07 | `jogador_fugiu(...)` | imprime `Jogador fugiu!`; “mão” da próxima = quem **não** fugiu | msg, req | RF-15 | ✘ (p) sempre define j1 como primeiro |
| JOG-08 | `criar_jogador`/`criar_bot` com baralho cheio e com 2 cartas | objeto com nome e 3 cartas / `IndexError` | call, exc | RF-02 | ✔ (p) |
| JOG-09 | Estado inicial de `Jogo()` | `rodadas == []`, `trucoPontos == 1` | ret | — | ✔ (p) |
| JOG-10 | O “mão” alterna entre mãos consecutivas | mão da mão 2 ≠ mão da mão 1 (partida real) | req | RF-03 | ✘ DEF-21 (c) — ver UC-18 |

### 4.4 Jogador humano (`jogador.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| JGD-01 | `Jogador('Ana')` | `pontos=0, rodadas=0, mao=[]`, flags `False` | ret | RF-01 | ✔ (p) |
| JGD-02 | `criar_mao(baralho)` | 3 cartas; baralho −3; `envido` calculado | req | RF-02 | ✔ (p) |
| JGD-03 | `jogar_carta(i)` para i = 0, 1, 2 | remove e devolve a carta i; mão reduz | call, ret | RF-10 | ✔ (p) |
| JGD-04 | `jogar_carta(3)` e `jogar_carta(-4)` | `IndexError` (e `-1` retorna a última — registrar) | exc | RF-10 | ✔ (p) |
| JGD-05 | `calcula_envido` (mesma tabela para o Bot, BOT-09): `7E 6E 1O` → **33**; `3O 2C 1B` → **3**; `4O 5C 6B` → **6**; `12O 11C 10B` → **0**; `7E 3E 2O` → **30**; `12E 5E 4O` → **25**; `12E 11E 10E` → **20**; `7E 6E 5E` (flor) → 38 | valores indicados | call, ret, loop | RF-32 | ✔ nos 4 primeiros (c); ✘ DEF-10 nos demais (c) |
| JGD-06 | `checa_flor`: 3 do mesmo naipe / 2+1 / mão vazia / 1 carta | `True` / `False` / `IndexError` / `True` (trivial — registrar) | ifs, exc | RF-40 | ✔ (c: vazia ⇒ IndexError) |
| JGD-07 | `mostrar_opcoes` — tabela: (3 cartas, sem flor), (3, com flor), (2 cartas), (1 carta), (2 cartas e `pediu_truco`) | `[4] Truco` só se ≥2 cartas e não pediu; `[5] Flor` só com 3 e flor; `[6][7][8]` só com 3; `[9]` sempre | ifs, msg | RF-20/30/40 | ✔ (p) |
| JGD-08 | Chamar `mostrar_opcoes` 2× com flor | `[5] Flor` aparece nas 2 chamadas | ifs | RF-40 | ✘ (p) 1ª chamada seta `flor=True` e some na 2ª |
| JGD-09 | `adicionar_pontos(n)`, `adicionar_rodada()` | incrementos corretos (n=0,1,4) | call | RF-05 | ✔ (p) |
| JGD-10 | `resetar()` | zera `rodadas, mao, flor, pediu_truco`; **mantém** `pontos`; deveria zerar `envido`/`pediu_flor` | req | RF-02 | ✘ (p) `envido`/`pediu_flor` residuais |
| JGD-11 | Getters `checa_mao`, `retorna_pontos_envido`, `retorna_pontos_totais` | refletem o estado | ret | — | ✔ (p) |

### 4.5 Truco (`truco.py`)
Notação: o **humano é o jogador 1** (`quem_pediu=1`) e o bot responde via `avaliar_truco` (respostas: 0=recusar, 1=aceitar, 2=aumentar).

| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| TRU-01 | `Truco()` | `valor_aposta=1`, `estado_atual=""`, `jogador_bloqueado=0` | ret | RF-23 | ✔ (p) |
| TRU-02 | Humano canta Truco; bot aceita | retorna `True`; `estado="truco"`; **valor da mão = 2** | req, ret | RF-20/23 | ✘ DEF-04 (c) valor=1 |
| TRU-03 | Humano canta; bot recusa | retorna `False`; humano +1; mão encerra | req, ret | RF-22 | ✔ (c) |
| TRU-04 | Truco → bot aumenta → humano aceita Retruco (`'1'`) | `True`; valor 3; `estado="retruco"` | req | RF-20/23 | ✔ (c) |
| TRU-05 | …Retruco → humano recusa (`'0'`) | `False`; **bot** +2 | req | RF-22 | ✔ (p) |
| TRU-06 | …humano aumenta (`'2'`) → bot aceita Vale 4 | `True`; valor 4; `pediu_truco=True` em ambos | req | RF-20 | ✔ (p) |
| TRU-07 | Vale 4 recusado pelo bot | humano +3; `False` | req | RF-22 | ✔ (p) |
| TRU-08 | Vale 4 com humano digitando `'2'` (aumentar) e depois `'1'` | `'2'` rejeitado, pergunta de novo; `'1'` aceita (início/fim do *loop*) | loop, input_ | RF-21 | ✔ (p) |
| TRU-09 | Após Vale 4 aceito, novo canto de qualquer jogador | retorna `None`; valor permanece 4 | req, ifs | RF-21 | ✘ DEF-05 (c) valor cai p/ 3 |
| TRU-10 | Mesmo jogador canta 2 vezes seguidas | 2ª chamada retorna `None` | ifs, ret | RF-21 | ✔ (c) |
| TRU-11 | Bot canta (`quem_pediu=2`); humano responde `'0'`, `'1'`, `'2'` | `False`+bot +1 / `True` / escala p/ Retruco | input_, ret | RF-22 | ✔ (p) |
| TRU-12 | Entradas do humano: `'9'`, `'-1'`, `'5'`, depois `'1'` / `'abc'` / `''` / `'1.5'` | inválidos numéricos repetem a pergunta e aceitam `'1'`; não numéricos ⇒ mensagem amigável | loop, input_, exc, msg | RF-22, RNF-02 | ✔ laço (c) · ✘ DEF-24 `ValueError` (c) |
| TRU-13 | `retornar_valor_aposta()` após cada etapa; `retornar_quem_fugiu()` | 1,2,3,4 · valor inteiro (jogador) | ret | RF-23 | ✔ valor · ✘ DEF-06 (c) |
| TRU-14 | `resetar()` após Vale 4 | volta ao estado inicial (TRU-01) | req | RF-02 | ✔ (p) |
| TRU-15 | `inverter_jogador_bloqueado` com bloqueado = 0, 1, 2 | 1, 2, 1 | ifs, ret | RF-21 | ✔ (p) |
| TRU-16 | `inicializar_jogador_bloqueado(x)` | `jogador_bloqueado == x` | call | RF-21 | ✔ (p) |
| TRU-17 | **Tabela de decisão** de `controlador_truco`: estado ∈ {`""`,`truco`,`retruco`,`vale_quatro`,`outro`} × (`quem_pediu == bloqueado`: sim/não) = 10 combinações | `None` se `vale_quatro` ou bloqueado; senão canto do próximo nível; `outro` ⇒ `None` | ifs, call | RF-20/21 | ✔ 9 · ✘ DEF-05 na linha `vale_quatro` |
| TRU-18 | Propriedade: a aposta nunca diminui ao longo de qualquer sequência de cantos | `valor_n+1 ≥ valor_n` | req | RF-23 | ✘ DEF-05 |

### 4.6 Envido (`envido.py`)
Parâmetros comuns: pontos de envido humano/bot; `placar`; “mão”. Para o bot, `avaliar_envido` roteirizado (0=recusar, 1=aceitar, 2=Real, 3=Falta).

| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| ENV-01 | `Envido()` | `valor_envido=2`, `estado_atual=0` | ret | RF-31 | ✔ (p) |
| ENV-02 | Humano canta Envido (6), bot aceita; 30 × 20 | humano +2; vencedor 1; caixa “Venceu o envido com 30 pontos” | req, msg | RF-31/32 | ✔ (c) |
| ENV-03 | Idem com 20 × 28 | bot +2; vencedor 2 | req | RF-32 | ✔ (p) |
| ENV-04 | **Empate** 25 × 25, com “mão” = humano e depois “mão” = bot | vence o “mão” | req, call | RF-32 | ✘ DEF-07 (c) humano sempre |
| ENV-05 | Bot recusa Envido | humano +1; `quem_fugiu=2`; **sem** caixa de vencedor | ifs, ret | RF-33 | ✔ (c) |
| ENV-06 | Bot canta (`quem_pediu=2`), humano recusa (`'0'`) | bot +1 | input_ | RF-33 | ✔ (p) |
| ENV-07 | Real Envido direto (7), aceito | valor **3** | req | RF-31 | ✘ DEF-08 (c) vale 5 |
| ENV-08 | Real Envido direto, recusado | cantor +1 | req | RF-33 | ✘ DEF-08 (c) +2 |
| ENV-09 | Envido → bot responde Real (2) → humano aceita | valor acumulado **5** | req | RF-31 | ✔ (c) |
| ENV-10 | Envido → Real → Falta (encadeamento completo) | valor = falta do líder; vencedor correto | req | RF-31/34 | ✘ DEF-09 (p) |
| ENV-11 | Falta Envido direto com placar humano 5 × bot 3, aceito | valor = **30 − 5 = 25** | req, call | RF-34 | ✘ DEF-09 (c) vale 9 |
| ENV-12 | Falta Envido recusado | cantor ganha acumulado + 1 | req | RF-33 | ✘ DEF-09 (c) +5 |
| ENV-13 | 2º canto na mesma mão (estado ≠ 0) | `None`, sem efeito | ifs, ret | RF-30 | ✔ (c) |
| ENV-14 | `quem_pediu == jogador_bloqueado` com `estado=0` | `None` | ifs | RF-30 | ✔ (p) |
| ENV-15 | `tipo` inválido (0, 5, 9, −1) | rejeitado: nenhum ponto e nenhuma caixa de “vencedor” | call, msg | RF-30 | ✘ DEF-23 (c) imprime caixa com vencedor 0 |
| ENV-16 | Humano responde Envido com `'4'`, `'-1'`, `'2'`; e com `'abc'` | `'4'`/`'-1'` repetem; `'2'` ⇒ Real; `'abc'` ⇒ erro tratado | loop, input_, exc | RF-31 | ✔ laço (p) · ✘ DEF-24 (c) |
| ENV-17 | Pergunta de Real Envido: opções {0,1,2}; `'3'` | `'3'` rejeitado | loop, input_ | RF-31 | ✔ (p) |
| ENV-18 | Pergunta de Falta Envido: opções {0,1}; `'2'` | `'2'` rejeitado | loop, input_ | RF-31 | ✔ (p) |
| ENV-19 | `definir_pontos_jogadores` | copia `envido` de cada jogador | call | RF-32 | ✔ (p) |
| ENV-20 | `resetar()` | todos os campos iniciais, incluindo `jogador2_pontos` | req | RF-02 | ✘ (p) `jogador2_pontos` não é zerado |
| ENV-21 | Captura de saída em qualquer canto | sem linhas de depuração (`1`,`2`,`3`,`4`) | msg | RNF-02 | ✘ DEF-18 |
| ENV-22 | **Tabela de decisão** `controlador_envido`: (estado=0/≠0) × (tipo=igual ao estado?) × (bloqueado=quem_pediu?) × tipo∈{6,7,8,outro} | só executa quando estado=0, não bloqueado e tipo válido | ifs, call | RF-30 | ✔ exceto `outro` (DEF-23) |
| ENV-23 | Pontuação não ultrapassa o placar final (jogador com placar−1 ganha Falta) | `pontos == limite` | req | RF-06 | ✘ DEF-25 (p) |

### 4.7 Flor (`flor.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| FLO-01 | Só o bot tem flor | bot +3; vencedor 2; caixa | req, msg | RF-41 | ✔ (c) |
| FLO-02 | Só o humano tem flor | humano +3; vencedor 1 | req | RF-41 | ✔ (c) |
| FLO-03 | Ninguém tem flor, `pedir_flor` chamado | nenhum ponto; **sem** caixa de vencedor | req, msg | RF-40 | ✘ DEF-23 (c) imprime “Jogador 2 venceu a flor” |
| FLO-04 | Ambos com flor, Contra-flor aceita; pontos de flor 38 × 35 | vencedor 38; **+6** | req | RF-42 | ✘ DEF-12 (p) compara pontos de envido |
| FLO-05 | Ambos com flor, recusa da Contra-flor | cantor +3 | req | RF-42 | ✘ DEF-11 (c) +4 |
| FLO-06 | Contra-flor e o resto aceita | valor = resto + 6 | req | RF-42 | ✘ DEF-12 (c) valor 3 |
| FLO-07 | Empate de flor | vence o “mão” | req | RF-43 | ✘ (p) sempre humano |
| FLO-08 | 2º `pedir_flor` na mesma mão | ignorado (nenhum ponto novo) | ifs | RF-41 | ✔ (c) |
| FLO-09 | `resetar_flor()` | `valor_flor=3`, `estado=""`, vencedor 0 | req | RF-02 | ✔ (p) |
| FLO-10 | `decisao_jogador` com entradas `'2'`, `'-1'`, `'1'` / `'x'` | repete até 0/1; `'x'` ⇒ erro tratado | loop, input_, exc | RF-42 | ✔ laço (p) · ✘ DEF-24 |
| FLO-11 | **Fronteira** `bot.pontos < int(humano.pontos/1.5)` → Resto vs Contra-flor: (h,b) = (0,0)→CF; (1,0)→CF; (2,0)→Resto; (3,1)→Resto; (3,2)→CF; (12,7)→Resto; (12,8)→CF | estado indicado | ifs, call | RF-42 | ✔ (c: 0,0 e 12,2) (p) demais |
| FLO-12 | Decisão entre Contra-flor/“resto” é do jogador | o humano escolhe | req | RF-42 | ✘ (p) escolha automática pelo placar |

### 4.8 Bot (`bot.py`)
Usar `cbr_stub` e baralho armado.

| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| BOT-01 | `criar_mao` | 3 cartas; `indices=[0,1,2]`; `pontuacao_cartas` e `mao_rank` com 3 itens; `envido`, `flor` e `qualidade_mao` definidos | req, ret | RF-50 | ✔ (p) |
| BOT-02 | `calcular_qualidade_mao` com pontos (52,24,16)→**40.895**; (52,50,42)→**74.654**; (24,16,12)→**25.8**; (4,3,1)→**4.786**; (24,24,24)→**36.333** (tolerância 1e-3) | valores indicados | call, ia | RF-51 | ✔ (c p/ o 1º) |
| BOT-03 | **Fronteira de `perdendo`** em `avaliar_envido(adv, bot)`: (0,0)→F; (6,0)→V; (7,10)→V; (1,3)→F; (2,3)→F; (3,3)→V; (6,12)→F; (7,12)→V. Verificar via `cbr_stub` o 4º argumento enviado | booleano indicado | ifs, call | RF-51 | ✔ (p) |
| BOT-04 | `avaliar_truco(cbr, tipo, quem)` | delega a `cbr.truco(tipo, quem, qualidade)` e devolve o retorno | call, ret | RF-50 | ✔ (p) |
| BOT-05 | **Árvore de decisão de `jogar_carta`** (stub controla `truco`/`jogar_carta`): ver tabela 4.8.1 | retorno indicado | ifs, ret | RF-50 | ver tabela |
| BOT-06 | `ajustar_indices(i)` para i = 0, 1, 2 e 3 | remove i de `mao_rank/indices/pontuacao_cartas`; i=3 ⇒ `IndexError` | call, exc | RF-50 | ✔ (p) |
| BOT-07 | `enriquecer_bot` com `rodada` = 1, 2, 3, 4, 5 (dublê de `Dados`) | chama `primeira_rodada`/`segunda_rodada`/`terceira_rodada`/`finalizar_rodadas`; 5 ⇒ nada | ifs, call | RF-56 | ✔ (p) |
| BOT-08 | `enriquecer_cartas_bot(cbr_real, carta)` | grava a carta jogada | req | RF-56 | ✘ DEF-14 (c) `AttributeError` |
| BOT-09 | `calcula_envido` do Bot = tabela JGD-05 | idem | call, ret | RF-32 | ✘ DEF-10 |
| BOT-10 | `resetar()` | listas vazias, `rodada=1`, flags `False` | req | RF-02 | ✔ (p) |
| BOT-11 | `avaliar_pedir_envido()` | decisão derivada do CBR (varia com a mão) | ia | RF-50 | ✘ (p) retorna constante 1 |
| BOT-12 | `checa_flor` (mão com flor / sem flor) | `True` / `False` | ifs, ret | RF-40 | ✔ (p) |
| BOT-13 | **Sem informação oculta**: após `enriquecer_bot(rodada=1, carta_humano=X)`, os campos `cartaAlta/Media/BaixaHumano` do registro seguem no valor do modelo; só `primeiraCartaHumano` muda | cartas não jogadas do humano não entram no caso | ia, req | RF-55 | ✔ (p) |
| BOT-14 | `adicionar_pontos` / `adicionar_rodada` / `retorna_pontos_totais` | incrementos | call, ret | RF-05 | ✔ (p) |

**4.8.1 Tabela de decisão — `Bot.jogar_carta`** (combinação de `if`s encadeados)

| # | `len(mao)` | `flor` (flag) | mão é flor? | `pediu_truco` | `cbr.truco` retorna | Esperado | Status |
|---|:-:|:-:|:-:|:-:|:-:|---|---|
| 1 | 3 | False | sim | False | — (`cbr.flor()`→True) | retorna **5** (cantar flor) | ✔ com stub · ✘ DEF-14 com `Cbr` real |
| 2 | 3 | False | sim | False | `cbr.flor()`→False | segue p/ jogar carta | ✔ (p) |
| 3 | 3 | **True** (como `criar_mao` seta) | sim | False | — | flor é cantada pelo bot | ✘ (p) ramo morto: nunca canta |
| 4 | 3 | False | não | False | — | **não** consulta truco; joga carta; `rodada`→2 | ✔ (p) |
| 5 | 2 | — | — | False | 1 | retorna **4**, `pediu_truco=True` | ✔ (p) (mas DEF-16: 1 = aceitar) |
| 6 | 2 | — | — | False | 2 | retorna 4 | ✔ (p) |
| 7 | 2 | — | — | False | 0 | joga carta | ✔ (p) |
| 8 | 2 | — | — | False | `None` | joga carta | ✔ (p) |
| 9 | 2 | — | — | **True** | (não consultado) | joga carta; `cbr.truco` **não** chamado | ✔ (p) |
| 10 | 1 | — | — | False | 1 | retorna 4 | ✔ (p) |
| 11 | 2 | — | — | False | 0, `cbr.jogar_carta` → −1 | índice válido de carta | ✘ DEF-17 (p) |

### 4.9 Bot × entradas de rodada (resumo de integração leve)
Coberto por BOT-07/13 e UC-20.

### 4.10 IA — CBR (`cbr.py`) — **obrigatório**
Duas bases: **real** (`cbr_real`, 27.515 casos) para propriedades gerais e **sintética** (`cbr_sintetico`) para forçar ramos. Colunas relevantes: `ganhador{Primeira,Segunda,Terceira}Rodada`, `quemGanhouTruco`, `quemRetruco`, `qualidadeMaoHumano`, `pontosEnvido{Robo,Humano}`, `quemGanhouEnvido`, `quemPediu{Envido,RealEnvido,FaltaEnvido}`, `{primeira,segunda,terceira}CartaRobo`.

| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| CBR-01 | `Cbr()` com a base original | `dataset.shape == (27515, 52)`; `nbrs` ajustado com 100 vizinhos; < 30 s | req, ia | RF-52, RNF-03 | ✔ (c) 2,9 s |
| CBR-01b | `Cbr()` com a base do *working tree* (TAB) | inicializa sem erro | req | RF-52, RNF-06 | ✘ DEF-01 (c) |
| CBR-02 | Sem `dbtrucoimitacao_maos.csv` / sem `modelo_registro.csv` | `FileNotFoundError` (ou mensagem clara) | exc | RNF-06 | ✔ (p) |
| CBR-03 | `vizinhos_proximos()` e `vizinhos_proximos(df)` | usa `dataset` / usa `df` informado | call, ret | RF-52 | ✔ (p) |
| CBR-04 | **Fronteira da base**: sintética com 99, 100 e 101 linhas, `kneighbors` | 99 ⇒ `ValueError` (vizinhos > amostras); 100 e 101 ok | exc, call | RF-53 | ✔ (p) |
| CBR-05 | `truco(tipo, quem, qualidade)` com qualidade ∈ {0, 1, 10, 40, 100, 1e6}; registro zerado | retorno ∈ {0,1,2}; mesma entrada ⇒ mesma saída (determinismo) | call, ret, ia | RF-50 | ✔ (c: 40→2, 0→0) |
| CBR-06 | **Decisão do truco** com base sintética — combinações (`q_bot > q_humano`?) × (`vencidas > perdidas`?) | aceitar/aumentar conforme regra do projeto: (V,V)→2; (V,F)→1; (F,*)→0 | ifs, ia | RF-50/51 | ✔ (V,V),(F,*) · ✘ DEF-16 (V,F) inalcançável |
| CBR-07 | Truco com vizinhança **sem** casos de vitória (ou de derrota) do bot | resposta de contingência (0/1) sem exceção | exc, ia | RF-53 | ✘ DEF-19 (p) `IndexError` |
| CBR-08 | Qualidade do humano ausente (`dropna` vazio) | contingência sem exceção | exc | RF-53 | ✘ DEF-19 (p) |
| CBR-09 | **Decisão do envido** — tabela por `tipo` × `quem_pediu` × `pontos_envido_robo` (5 e 6+) × `robo_perdendo` (V/F), com base sintética montada para cada predicado (`pontos_jogador<pontos_robo`, `real_g>real_p`, `env_g>env_p`) — 18 casos (ver 4.10.1) | retorno no domínio: abertura {6,7,8}; resposta a Envido {0,1,2,3}; a Real/Falta {0,1} | ifs, call, ret, ia | RF-31/50 | ✔ (p) exceto DEF-20 |
| CBR-10 | Envido com vizinhança sem “ganhas” ou sem “perdidas” | contingência sem exceção | exc | RF-53 | ✘ DEF-19 (p) |
| CBR-11 | `jogar_carta(rodada, pontos)`: rodadas 1, 2, 3 com listas de 3, 2 e 1 pontuações; e rodadas **0** e **4** | índice em `[-1, len-1]`; rodada 0/4 ⇒ erro tratado | call, ret, exc | RF-50 | ✔ 1–3 (c: 2,1,0) · ✘ (p) 0/4 ⇒ `KeyError` |
| CBR-12 | Escolha da carta mais próxima do valor de referência (sintética: referência 24 com `[52,24,16]`; referência 20 com `[24,16]` — empate de distância) | índice 1; empate resolvido de forma estável (1ª ocorrência) | ia, ret | RF-52 | ✔ (p) |
| CBR-13 | Valor de referência ≤ 0 (casos sem jogada registrada) | o bot ainda joga uma carta válida (nunca `-1`) | ia | RF-50 | ✘ DEF-17 |
| CBR-14 | **Só aprende com vitórias do bot**: sintética com casos vencidos pelo humano contendo cartas distintas | referência vem apenas dos casos em que o bot venceu | ia | RF-51 | ✔ (p) |
| CBR-15 | Vitória por **2×0** (3ª rodada ausente) conta como vitória | referência considera esses casos | ia | RF-51 | ✘ DEF-22 (p) |
| CBR-16 | **Similaridade, não igualdade (RF-52):** consultar uma linha da base ⇒ 1º vizinho é ela com distância 0; alterar 1 campo ⇒ continua entre os 5 mais próximos | recuperação por proximidade | ia, req | RF-52 | ✔ (p) |
| CBR-17 | **Base editável (RF-54):** duas bases sintéticas A/B com o mesmo registro | decisões diferentes refletindo a base | ia, req | RF-54 | ✔ (p) |
| CBR-18 | Consulta não altera `dataset` nem o registro (shape/valores iguais antes e depois) | imutável | ia | RNF-04 | ✔ (p) |
| CBR-19 | Desempenho: 20 consultas `truco`/`envido`/`jogar_carta` com `cbr_real` | média < 1 s por consulta | req | RNF-03 | ✔ (p) |
| CBR-20 | Mão fraca (qualidade 0) nunca “aumenta” frente à mão forte do humano; mão forte contra fraca aumenta | monotonicidade básica | ia | RF-51 | ✔ (p) |
| CBR-21 | Efeito colateral global: `warnings.simplefilter('ignore')` dentro das consultas | filtro global do processo não deveria mudar | req | RNF-04 | ✘ (p) altera o filtro global |
| CBR-22 | Integração Bot↔Cbr: bot com `Cbr` real joga 3 rodadas sem exceção (baralho armado, 20 sementes) | nenhuma exceção; cartas jogadas ⊂ mão | ia, e2e | RF-50 | ✘ DEF-19/DEF-17 se algum caso cair em contingência (p) |

**4.10.1 Tabela de decisão — `Cbr.envido`** (base sintética por linha)

| # | `quem_pediu` | `pontos_envido_robo` | A = `pontos_jogador<robo ∧ real_g>real_p ∧ env_g>env_p` | `robo_perdendo` | `env_g ≠ env_p` | Retorno esperado |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | 2 | 6 | V | V | — | 8 |
| 2 | 2 | 6 | V | F | — | 7 |
| 3 | 2 | 6 | F | V | V | 8 |
| 4 | 2 | 6 | F | F | V | 6 |
| 5 | 2 | 5 | (qualquer) | — | — | cai para o ramo por `tipo` |
| 6 | 1 | tipo 6 | V | — | — | 2 (Real) |
| 7 | 1 | tipo 6 | F, `real_g>real_p ∧ env_g>env_p` | V | — | 3 (Falta) |
| 8 | 1 | tipo 6 | F | F | V | 1 |
| 9 | 1 | tipo 6 | F | F | F | 0 |
| 10 | 1 | tipo 7 | `pontos_jogador<robo` | — | — | 1 |
| 11 | 1 | tipo 7 | F e (`env_g>env_p ∧ real_g>real_p`)=V | — | — | 1 |
| 12 | 1 | tipo 7 | F e F | — | — | 0 |
| 13 | 1 | tipo 8 | `pontos_jogador<robo` | — | — | 1 |
| 14 | 1 | tipo 8 | F | — | — | 0 |
| 15–18 | 1 | tipo 6/7/8 com `robo_perdendo=None` (default) | | None | | mesmo resultado que `False` |

### 4.11 Registro de casos (`dados.py`)
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| DAD-01 | `Dados()` na base original | `registro` com 1 linha (modelo zerado); `casos` 27.515 linhas | req, ret | RF-54 | ✔ (c) |
| DAD-02 | `tratamento_inicial_df` | sem `NaN`; colunas numéricas `int16`; `-100`/`-66` nos nulos | req, ret | RF-52 | ✔ (p) |
| DAD-03 | `primeira_rodada(pts, rank, q, carta)` | `cartaAlta/Media/BaixaRobo`, `jogadorMao=1`, `primeiraCartaHumano`, naipe codificado; **`qualidadeMaoRobo` = q** | call, req | RF-56 | ✘ DEF-15 (c) grava `qualidadeMaoBot` (não é coluna) |
| DAD-04 | `segunda_rodada(c_h, c_r, g)` | `ganhadorPrimeiraRodada=g`; `primeiraCartaHumano`; **não** altera `terceiraCartaRobo` | call | RF-56 | ✘ DEF-15 (c) |
| DAD-05 | `terceira_rodada(c_h, c_r, g)` | grava `segundaCartaHumano` (coluna) | call | RF-56 | ✘ DEF-15 (c) grava `SegundaCartaHumano` |
| DAD-06 | `finalizar_rodadas(c_h, c_r, g)` | `ganhadorTerceiraRodada`, `terceiraCartaHumano`; `terceiraCartaRobo` = carta do **robô** | call | RF-56 | ✘ DEF-15 (p) |
| DAD-07 | `envido(qe, qr, qf, qg)` | atualiza `quemPediuEnvido`, `quemPediuRealEnvido`, `quemPediuFaltaEnvido`, `quemGanhouEnvido` | call | RF-56 | ✘ DEF-15 (c) só `quemGanhouEnvido`… e nome de atributo errado |
| DAD-08 | `truco(...)` com 5 valores | 5 colunas atualizadas | call | RF-56 | ✔ (c) |
| DAD-09 | `flor(qf, qcf, qcfr, pts)` com `quemGanhouFlor` esperado variando | respeita o vencedor real | call | RF-56 | ✘ DEF-15 (p) fixo em 2 |
| DAD-10 | `vencedor_envido`, `vencedor_truco`, `vencedor_flor` | colunas `quemGanhou*`/`quemNegou*` | call | RF-56 | ✔ (p) |
| DAD-11 | `cartas_jogadas_pelo_bot('primeira'/'segunda'/'terceira'/'quarta')` | grava a rodada correspondente; `'quarta'` não grava | ifs, call | RF-56 | ✔ (p) |
| DAD-12 | `finalizar_partida()` 1× e 2× em dir. limpo; e em dir. somente-leitura | 1ª cria `jogadas.csv` com cabeçalho; 2ª anexa sem cabeçalho (3 linhas); somente-leitura ⇒ `PermissionError` | req, exc | RF-56 | ✔ (c) 3 linhas |
| DAD-13 | `resetar()` depois de alterar o registro | registro volta ao modelo zerado | req | RF-02 | ✔ (p) |
| DAD-14 | Sem a base / sem o modelo | `FileNotFoundError` | exc | RNF-06 | ✔ (p) |
| DAD-15 | `retornar_registro()` / `retornar_casos()` | `DataFrame` com 1 linha / com 27.515 linhas | ret | — | ✔ (p) |

### 4.12 Interface (`interface.py`) — captura com `capsys`
| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| INT-01 | `mostrar_carta_jogada('Ana', 3 de OUROS)` | `Ana jogou a carta: 3 de OUROS` | msg | RF-04 | ✔ (c) |
| INT-02 | `mostrar_carta_ganhadora` / `mostrar_ganhador_rodada` | textos esperados | msg | RF-04 | ✔ (p) |
| INT-03 | `mostrar_ganhador_jogo('Ana')` | `Ana ganhou o jogo` | msg | RF-05 | ✔ (c) |
| INT-04 | `mostrar_placar_total` | caixa com título “Pontuação Total”, 2 linhas “N Pontos Acumulados” | msg | RF-04 | ✔ (c) |
| INT-05 | `mostrar_placar_rodadas` | caixa “Rodadas da Partida Atual” | msg | RF-04 | ✔ (p) |
| INT-06 | `mostrar_vencedor_flor(1…)` / `(2…)` | cada jogador na linha certa | msg | RF-41 | ✔ (c p/ 1) |
| INT-07 | `mostrar_vencedor_flor(0…)` | não apresenta vencedor | msg | RF-41 | ✘ DEF-23 (c) |
| INT-08 | `mostrar_vencedor_envido(1/2…)` | vencedor/perdedor corretos com pontos | msg | RF-32 | ✔ (c p/ 2) |
| INT-09 | `mostrar_vencedor_envido(0…)` (empate/sem vencedor) | mensagem neutra | msg | RF-32 | ✘ DEF-23 (c) |
| INT-10 | `mostrar_placar_total_jogador_fugiu(j,…)` | `Jogador <nome> fugiu!` | msg | RF-15 | ✔ (p) |
| INT-11 | `mostrar_jogador_opcoes(nome)` | informa **quem** é mão | msg | RF-03 | ✘ (p) texto fixo “Jogador 1 é mão” |
| INT-12 | `border_msg` com variações: 1 linha, 3 linhas, linha vazia, `indent` 0/1/3, `width` menor que a linha, `title` | caixa alinhada (linhas de mesmo comprimento) | call, ret | RNF-02 | ✔ (p) exceto `width` < linha (p) quebra o alinhamento |
| INT-13 | `desenhar_cartas('3 de OUROS')` por naipe; `exibir_cartas([])`; `exibir_cartas([c1,c2,c3])` | símbolo ♦/♣/♥/♠ certo; lista vazia sem erro; 9 linhas por carta lado a lado | call, msg | RF-04 | ✔ (p) |
| INT-14 | `limpar_tela` (com `os.system` substituído) | chama `clear` | call | RNF-02 | ✔ (p) |

### 4.13 Fluxo principal e entradas do usuário (`__main__.py`)
Via `rodar_main` (nomes + roteiro de entradas, *seed* fixa, CBR stub). Valores do menu do humano com 3 cartas: **0–2** jogar carta, **4** Truco, **5** Flor, **6/7/8** Envido/Real/Falta, **9** ir ao baralho.

| ID | Cenário / entrada | Resultado esperado | Tipo | Req. | Status |
|---|---|---|---|---|---|
| MAIN-01 | Nomes: `''`, `'Ana'`, `'José'`, `'A'*200`, com emoji | aceita; caixas de placar não quebram; `''` ⇒ nome padrão ou recusa | input_ | RNF-02 | ✘ (p) `''` aceito e exibido vazio |
| MAIN-02 | **Tabela de entradas do menu (3 cartas)**: `0`,`1`,`2`,`3`,`4`,`5` (sem flor),`6`,`9`,`10`,`-1`,`' 1 '`,`''`,`'abc'`,`'0.5'`,`'1,3'` | `0–2` jogam; `4,6–9` ações; `5` sem flor, `10`, `-1` ⇒ “Selecione um valor válido!”; `3` ⇒ inválido; não numéricos ⇒ mensagem sem encerrar | input_, msg, ifs, loop | RF-10, RNF-02 | `0,1,2,4,6–9,' 1 '` ✔ (p) · `3` ✘ DEF-13 (c) · `''`,`'abc'`,`'0.5'` ✘ DEF-24 (c) |
| MAIN-03 | Menu com **2 cartas** (2ª rodada): `0`,`1`,`2`,`4`,`5`,`6`,`7`,`8`,`9` | `0,1` jogam; `4,9` ações; `2` inválido; `5–8` não disponíveis (só 1ª rodada) ⇒ “Selecione um valor válido!” | input_, ifs | RF-30 | `2` ✘ DEF-13 (p); `6–8` ✔ (p) |
| MAIN-04 | Menu com **1 carta** (3ª rodada): `0`,`1`,`4`,`9` | `0` joga; `1` inválido; **Truco indisponível** (menu só mostra com ≥2 cartas) | input_, ifs | RF-20 | ✘ (p) o loop aceita `4` mesmo sem aparecer no menu |
| MAIN-05 | Fim da partida: entradas `0` sempre, 5 sementes | a partida termina; vencedor com **≥ 30** e perdedor < 30; mensagem “ganhou o jogo” | loop, req | RF-01/05 | ✘ DEF-02 (c) termina em 12 |
| MAIN-06 | Após a vitória, pontos do vencedor | exatamente 30 (sem ultrapassar) | req | RF-06 | ✘ DEF-25 (p) |
| MAIN-07 | Reinício de mão (`reiniciarJogo`) via estado final: baralho restante = 34; mãos novas de 3 cartas; `rodadas=0`; pontos preservados; `truco/envido` resetados | conforme descrito | req | RF-02 | ✔ (p) |
| MAIN-08 | Entradas esgotadas (EOF) no meio da partida | encerra com erro controlado | exc, loop | RNF-02 | ✘ (p) `EOFError` não tratado |
| MAIN-09 | Menu: **Truco** na 1ª rodada, depois escolher `0` | Truco processado e o jogo volta ao menu da mesma rodada | input_, ifs | RF-20 | ✔ (p) |
| MAIN-10 | Humano escolhe Envido (`6`) quando o bot tem flor | “Bloqueou o envido com a flor”; Flor é disputada | ifs, msg | RF-40/41 | ✔ (p) |
| MAIN-11 | Combinação de `if` do turno do humano: (3 cartas?) × (flor do humano?) × (bot pediu flor?) × opção∈{5,6,7,8} | caminho coerente (cantar flor / bloquear envido / envido normal / inválido) | ifs | RF-40/41 | ✔ (p) |

---

## 5. Casos de uso ponta a ponta (cenários de uso — obrigatórios)

Executados com baralho armado e CBR *stub* (exceto UC-19/20). Distribuição: humano = 3 primeiras `pop()`; bot = 3 seguintes. Sigla de carta: `1E` = 1 de ESPADAS, `1B` = 1 de BASTOS, `7E`, `7O`, `3C`, …

| ID | Caso de uso | Pré-condição / roteiro | Resultado esperado | Req. | Status |
|---|---|---|---|---|---|
| UC-01 | Partida completa | semente fixa, humano sempre joga `0` | termina; um jogador chega ao placar final (30); mensagem de vitória | RF-01/05 | ✘ DEF-02 |
| UC-02 | Humano vence a mão 2×0 | humano `1E,7E,3C` vs bot `4O,5C,6B`; joga `0,0` | +1 ponto ao humano; placar “Pontuação Total” | RF-14 | ✔ (p) |
| UC-03 | Humano perde 0×2 | invertido | bot +1 | RF-14 | ✔ (p) |
| UC-04 | 1×1 e a 3ª decide | rodadas V, D, V | vencedor da 3ª leva a mão | RF-14 | ✔ (p) |
| UC-05 | 1ª rodada empata (parda), 2ª decide | cartas de mesmo valor na 1ª | vence quem ganhar a 2ª | RF-12 | ✘ DEF-03 |
| UC-06 | 2ª rodada empata após 1ª decidida | | vence quem ganhou a 1ª | RF-12 | ✘ DEF-03 |
| UC-07 | 3ª rodada empata | 1×1 e 3ª empatada | vence o “mão” | RF-12 | ✘ DEF-03 |
| UC-08 | Todas as rodadas empatam | | vence o “mão” | RF-12 | ✘ DEF-03 |
| UC-09 | Humano vai ao baralho (`9`) na 1ª rodada | | bot +1 (valor corrente); nova mão; humano sem pontos | RF-15 | ✔ (p) |
| UC-10 | Humano canta Truco, bot recusa | stub `truco→0` | humano +1; nova mão | RF-20/22 | ✔ (p) |
| UC-11 | Truco aceito e humano vence a mão | stub `truco→1`; humano ganha 2×0 | humano ganha **2** pontos | RF-23 | ✘ DEF-04 |
| UC-12 | Escalada completa Truco→Retruco→Vale 4 e humano vence | stub aumenta; humano `'2'`, bot aceita | humano ganha **4** pontos | RF-20/23 | ✔ (p) |
| UC-13 | Envido na 1ª rodada, humano ganha | humano `7E 6E` (33) vs bot 20; `6` | humano +2 e depois pontos da mão | RF-31/32 | ✔ (p) |
| UC-14 | Envido empatado | 27 × 27 | vence o “mão” | RF-32 | ✘ DEF-07 |
| UC-15 | Envido tentado na 2ª rodada | menu com 2 cartas, entrada `6` | recusado: “Selecione um valor válido!” | RF-30 | ✔ (p) |
| UC-16 | Falta Envido com placar 5×3 | `8`, bot aceita | valor = 30 − líder | RF-34 | ✘ DEF-09 |
| UC-17 | Entradas inválidas em sequência | `abc`, `''`, `99`, `-1`, `3`, depois `0` | jogo continua e aceita `0` sem encerrar | RNF-02 | ✘ DEF-24, DEF-13 |
| UC-18 | Alternância do “mão” em 3 mãos seguidas | humano é mão na 1ª | 2ª mão: bot é mão; 3ª: humano | RF-03 | ✘ DEF-21 |
| UC-19 | Bot com flor (e humano sem) | baralho armado: bot `7O 4O 5O` | bot canta flor e ganha **3** antes da 1ª jogada | RF-41 | ✘ DEF-14 (p) (ramo morto) |
| UC-20 | Humano com flor canta `5`; bot sem flor | humano `1E 7E 5E` ⇒ mesmo naipe | humano +3; envido anulado | RF-41 | ✔ (p) |
| UC-21 | Ambos com flor ⇒ Contra-flor | `5` do humano; bot aceita | vencedor pelos pontos de flor; +6 | RF-42/43 | ✘ DEF-12 |
| UC-22 | Humano recusa Contra-flor | | bot +3 | RF-42 | ✘ DEF-11 |
| UC-23 | Partida com `Cbr` real (5 sementes, humano joga `0`) | | nenhuma exceção em toda a partida | RF-50 | ✘ DEF-19/17 (p) depende da semente |

---

## 6. Rastreabilidade (requisito → cenários)

| Requisito | Cenários |
|---|---|
| RF-01/05/06 (partida, fim, limite) | UC-01, MAIN-05/06, ENV-23 |
| RF-02 (baralho/distribuição) | BAR-01…10, JGD-02, JOG-08, MAIN-07 |
| RF-03 (alternância do “mão”) | JOG-06/10, UC-18, INT-11 |
| RF-04 (exibição) | INT-01…14, JOG-03 |
| RF-10…15 (rodadas, parda, baralho) | CAR-01…07, JOG-01…07, JGD-03/04, UC-02…09, MAIN-02…04 |
| RF-20…23 (Truco) | TRU-01…18, UC-10…12 |
| RF-30…35 (Envido) | ENV-01…23, JGD-05, UC-13…16 |
| RF-40…43 (Flor) | FLO-01…12, JGD-06/07/08, UC-19…22, MAIN-10/11 |
| RF-50…56 (Bot/CBR) | BOT-01…14, CBR-01…22, DAD-01…15, UC-23 |
| RNF-01…06 | CBR-01b/02/19/21, DAD-14, MAIN-01/08, INT-12/14 |

---

## 7. Plano de implementação e vídeo

**Ordem sugerida** (prioriza o que o enunciado marca como obrigatório):
1. `conftest.py` + fixtures + `base_original.csv` → 2. Carta/Baralho/Jogo/Jogador (rápidos, determinísticos) → 3. Truco/Envido/Flor (com `fake_jogador` e `entradas`) → 4. Bot + CBR (stub e sintético) → 5. Dados/Interface → 6. `__main__` e E2E → 7. Cobertura (`--cov-branch`) e ajuste de `xfail`.

**Roteiro do vídeo (≈10 min):** (1) estrutura de `tests/` e marcadores (1 min) · (2) 1 teste de cada categoria exigida: requisito (CAR-01), exceção (BAR-06), mensagem (INT-01), laço (TRU-08), tabela de `if` (BOT-05), parâmetros (JGD-05), entrada de usuário (MAIN-02), retorno (CAR-08), IA (CBR-06/12/16) (5 min) · (3) execução completa e leitura do relatório: passes, `xfailed` e o catálogo DEF (3 min) · (4) cobertura de ramos e conclusões — o que os testes revelaram (1 min).

**Metas de aceite da suíte:** ≥ 150 cenários executáveis; todos os marcadores obrigatórios presentes; 0 falhas inesperadas (toda divergência registrada como `xfail strict` com DEF-nn); cobertura de ramos relatada por módulo.
