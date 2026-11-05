# Documento de Requisitos — Truco Gaudério com CBR

**Versão:** 1.0 · **Data:** 2026-11-05 · **Origem:** `README.md` + decisões de regras confirmadas com o autor (seção 9).

## 1. Introdução

### 1.1 Objetivo
Jogo de Truco Gaudério (Rio Grande do Sul) em Python, no qual **um humano joga contra um bot** cujas decisões são tomadas por **Case-Based Reasoning (CBR)**.

### 1.2 Contexto
Trabalho da disciplina *Aplicações em Aprendizado de Máquina* (PPGCC, UFSM). Base de código derivada de [anthonyzutter/Truco-Jogo](https://github.com/anthonyzutter/Truco-Jogo).

### 1.3 Escopo
- **Dentro:** partida 1v1 (humano × bot) em terminal, com Truco, Envido e Flor; bot guiado por CBR sobre `dbtrucoimitacao_maos.csv`.
- **Fora (por ora):** modo 2v2, multiplayer em rede, interface gráfica, sinais/“señas”.

### 1.4 Glossário
| Termo | Significado |
|---|---|
| Mão | Fração da partida; vale 1 ponto base, ampliado por Truco/Envido/Flor. Melhor de 3 rodadas. |
| Rodada | Cada jogador mostra uma carta; vence a maior. |
| “Mão” (jogador) | Quem joga primeiro na mão. |
| Parda | Empate de rodada. |
| Falta | Pontos que faltam ao líder para atingir 30. |
| Esconder | Jogar a carta virada; não vale nada. |
| Ir ao baralho | Abandonar a mão, entregando os pontos em disputa ao adversário. |
| Caso | Registro da base CBR: situação do jogo + ação tomada + resultado. |

## 2. Regras do jogo (fonte de verdade)

### 2.1 Baralho e cartas
- Baralho espanhol de **40 cartas** (sem 8, 9, 10-curinga e coringas); naipes: ouros, copas, espadas, paus (bastos).
- Cada jogador recebe **3 cartas**, distribuídas aleatoriamente pelo sistema.
- **Hierarquia (maior → menor):**
  1. 1 de espadas · 2. 1 de paus · 3. 7 de espadas · 4. 7 de ouros (**manilhas**)
  5. 3 · 6. 2 · 7. 1 (copas e ouros) · 8. 12 · 9. 11 · 10. 10 · 11. 7 (copas e paus) · 12. 6 · 13. 5 · 14. 4
- Valor numérico de cada carta para Envido/Flor: 4–7 valem o próprio número; 10, 11 e 12 valem 0; 1, 2 e 3 valem o próprio número.

### 2.2 Pontuação e fim de partida
- A partida termina quando um jogador atinge **30 pontos** (placar final).
- Início: a “mão” da 1ª mão é sorteada; depois **alterna a cada mão**.

### 2.3 Rodadas e vencedor da mão
- Melhor de 3 rodadas; quem vence uma rodada **joga primeiro** na seguinte.
- **Parda (empate), regra tradicional:**
  - 1ª rodada empata → vence a mão quem ganhar a 2ª.
  - 2ª empata (após 1ª decidida) → vence quem ganhou a 1ª.
  - 3ª empata → vence o jogador “mão”.
  - Todas empatam → vence o jogador “mão”.
- Jogador pode **esconder** carta ou **ir ao baralho**.

### 2.4 Truco
| Canto | Valor da mão | Se recusado, o cantor ganha |
|---|---|---|
| Truco | 2 | 1 |
| Retruco | 3 | 2 |
| Vale 4 | 4 | 3 |

- Pode ser cantado em qualquer rodada.
- **Somente quem recebeu o canto pode aumentá-lo** (quem cantou Truco não canta Retruco; o adversário, ao aceitar, pode subir). Vale 4 não pode ser aumentado.
- Respostas possíveis: **aceitar**, **recusar** (ir ao baralho) ou **aumentar**.

### 2.5 Envido
- Só pode ser cantado **na 1ª rodada**, antes de resolvida a rodada.
- Pontos de envido do jogador: **20 + soma das 2 cartas do mesmo naipe** (figuras valem 0); sem duas do mesmo naipe, vale a maior carta (valor da tabela 2.1). Máximo 33.
- Cantos e valores: **Envido = 2**, **Real Envido = 3**, **Falta Envido = falta do líder** (ver 2.2).
- Podem ser encadeados (ex.: Envido + Envido = 4; Envido + Real Envido = 5; qualquer um pode terminar em Falta Envido).
- **Recusado:** vale 1 ponto (ou a soma dos cantos já aceitos) para quem cantou.
- **Empate** nos pontos: vence o jogador “mão”.
- Se algum jogador tem Flor, Envido não é disputado (a Flor prevalece).

### 2.6 Flor
- Flor = 3 cartas do mesmo naipe. É **obrigatório cantar** quando se tem.
- Pontos da flor: 20 + soma das 3 cartas (figuras = 0).
- **Só um jogador com flor:** ganha **3 pontos** e a Flor encerra a disputa de Envido.
- **Ambos com flor:** podem **Contra-flor** (vale 6) ou **Contra-flor e o resto** (falta do líder + valor da Contra-flor); maior pontuação vence, empate vence o “mão”. **Recusa** entrega os pontos da Flor (3) ao cantor.

## 3. Requisitos funcionais

### 3.1 Partida
| ID | Requisito |
|---|---|
| RF-01 | O sistema deve permitir uma partida 1v1 humano × bot até 30 pontos. |
| RF-02 | O sistema deve criar o baralho de 40 cartas, embaralhar e distribuir 3 cartas a cada jogador a cada mão. |
| RF-03 | O sistema deve sortear a “mão” da primeira mão e alternar nas seguintes. |
| RF-04 | O sistema deve exibir ao humano suas cartas, as cartas jogadas, o placar e o valor corrente da mão. |
| RF-05 | O sistema deve encerrar a partida ao atingir 30 pontos, anunciar o vencedor e oferecer nova partida ou sair. |
| RF-06 | O sistema deve limitar pontos ganhos ao necessário para chegar a 30 (sem ultrapassar o placar final). |

### 3.2 Rodadas
| ID | Requisito |
|---|---|
| RF-10 | Cada jogador, em sua vez, deve poder jogar uma das cartas restantes, virada para cima ou **escondida**. |
| RF-11 | O sistema deve determinar o vencedor da rodada segundo a hierarquia 2.1. |
| RF-12 | O sistema deve tratar **parda** conforme 2.3 (não atribuir vitória automática ao jogador 1). |
| RF-13 | O vencedor da rodada joga primeiro na seguinte; em parda, joga primeiro quem foi “mão” da rodada empatada. |
| RF-14 | O sistema deve encerrar a mão assim que um jogador garantir 2 rodadas (ou pelas regras de parda) e pontuar o vencedor com o valor da mão. |
| RF-15 | O jogador pode **ir ao baralho** a qualquer momento da sua vez, entregando os pontos em disputa. |

### 3.3 Truco
| ID | Requisito |
|---|---|
| RF-20 | O jogador da vez deve poder cantar Truco, Retruco e Vale 4 conforme 2.4. |
| RF-21 | O sistema deve impedir que quem cantou aumente o próprio canto; deve impedir aumento após Vale 4. |
| RF-22 | Ao receber um canto, o jogador deve poder aceitar, recusar ou aumentar; a recusa encerra a mão com os pontos da tabela 2.4. |
| RF-23 | O valor da mão deve refletir o último canto aceito (1, 2, 3 ou 4). |

### 3.4 Envido
| ID | Requisito |
|---|---|
| RF-30 | O sistema deve permitir cantar Envido, Real Envido e Falta Envido apenas na 1ª rodada e antes de ela terminar. |
| RF-31 | O sistema deve permitir o encadeamento de cantos conforme 2.5 e calcular o valor acumulado. |
| RF-32 | O sistema deve calcular os pontos de envido de cada jogador e determinar o vencedor, com desempate pelo “mão”. |
| RF-33 | Em caso de recusa, o sistema deve atribuir ao cantor 1 ponto (ou a soma dos cantos aceitos). |
| RF-34 | O sistema deve calcular Falta Envido como `30 − pontos do líder`. |
| RF-35 | O sistema só revela os pontos dos jogadores ao final da disputa de Envido. |

### 3.5 Flor
| ID | Requisito |
|---|---|
| RF-40 | O sistema deve detectar flor (3 cartas do mesmo naipe) e exigir/forçar seu canto na 1ª rodada. |
| RF-41 | Com flor de um só jogador: atribuir 3 pontos e cancelar Envido. |
| RF-42 | Com flor de ambos: permitir Contra-flor e Contra-flor e o resto, com cálculo e recusas conforme 2.6. |
| RF-43 | O sistema deve calcular os pontos de flor (20 + soma das 3 cartas) e determinar o vencedor, com desempate pelo “mão”. |

### 3.6 Bot (CBR)
| ID | Requisito |
|---|---|
| RF-50 | O bot deve decidir **todas** as suas ações: carta a jogar (incluindo esconder), cantar/aceitar/recusar/aumentar Truco, Envido, Flor e ir ao baralho. |
| RF-51 | As decisões devem se basear no estado do jogo: cartas em mão, cartas já jogadas, placar, rodada atual, cantos em andamento e jogadas do oponente. |
| RF-52 | O CBR deve buscar na base `dbtrucoimitacao_maos.csv` os casos **mais similares** (não só idênticos), por métrica de distância/vizinhança (scikit-learn), e adotar a ação dos casos recuperados. |
| RF-53 | Quando não houver caso suficientemente similar, o bot deve usar uma decisão de contingência (heurística básica) definida e documentada. |
| RF-54 | A base de casos deve poder ser alterada pelo usuário; novos casos devem seguir o formato de `modelo_registro.csv`. |
| RF-55 | O bot **não** pode acessar as cartas do humano nem informação oculta. |
| RF-56 | (Desejável) Registrar as mãos jogadas em formato compatível com a base para futura retroalimentação (fase *Retain* do ciclo CBR). |

## 4. Requisitos não funcionais
| ID | Requisito |
|---|---|
| RNF-01 | Linguagem Python 3; execução por `python -m truco`; dependências em `requirements.txt` (pandas, scikit-learn). |
| RNF-02 | Interface de terminal em **português**, com menus numerados e validação de entrada (entrada inválida não encerra o programa). |
| RNF-03 | Decisão do bot em tempo imperceptível (< 1 s por jogada em hardware comum). |
| RNF-04 | Regras (cartas, Truco, Envido, Flor) isoladas da interface e do bot, para permitir testes unitários. |
| RNF-05 | Cobertura de testes automatizados para: hierarquia de cartas, parda, pontos de envido/flor, pontuação de cantos e recusas, fim de partida. |
| RNF-06 | Base CSV lida com tolerância a erros (arquivo ausente/malformado gera mensagem clara). |

## 5. Arquitetura (módulos existentes)
`baralho`, `carta`, `pontos` (tabelas de valores), `jogador`, `bot`, `cbr`, `dados` (leitura/preparo da base), `jogo` (regras de rodada), `truco`, `envido`, `flor`, `interface`, `__main__` (laço principal).

## 6. Requisitos de dados (CBR)
- Arquivo da base: `dbtrucoimitacao_maos.csv`; modelo de registro: `modelo_registro.csv`.
- Cada caso deve conter: cartas da mão, estado da rodada, cantos ativos, pontuação e a ação/resultado associado.
- Casos podem ter resultado de sucesso ou fracasso; ambos são utilizáveis como referência.

## 7. Critérios de aceitação (resumo)
1. Uma partida completa até 30 pontos é jogável sem erros.
2. Todos os cenários de pontuação das seções 2.4–2.6 produzem os valores especificados.
3. Pardas seguem 2.3 em todas as combinações.
4. O bot executa todas as ações (RF-50) usando CBR e nunca cai em erro por falta de caso similar.
5. A base pode ser editada e o bot reflete a mudança na execução seguinte.

## 8. Lacunas observadas no código atual
Pontos em que a implementação diverge destes requisitos (a corrigir):
- **Parda não implementada:** empate de cartas comuns favorece o jogador 1 (`jogo.py`, `verificar_carta_vencedora`; trechos de empate comentados).
- **Alternância de “mão”** (`quem_inicia_rodada`) e fuga redefinem sempre o jogador 1 como primeiro.
- **Truco:** `pedir_retruco` é reaproveitado também no estado “retruco”; mensagens de aumento dizem “Retruco” em Vale 4; `retornar_quem_fugiu` retorna a própria função.
- **Envido:** encadeamento limitado; recusa e `print(2)` de debug no controlador.
- **Flor:** recusa vale 4 pontos (regra: 3); escolha entre Contra-flor e “resto” é automática por placar em vez de ser decisão do jogador; Contra-flor e o resto não soma falta.
- **Entradas** via `int(input())` sem tratamento de erro.
- **Placar final** fixo em **12 pontos** no `__main__` e na falta (`12 − pontos`); o requisito é 30 e deveria ser parametrizado.
- **Base de casos:** o `dbtrucoimitacao_maos.csv` do *working tree* está separado por TAB, mas `cbr.py`/`dados.py` leem com vírgula, então `Cbr()` não inicia (a base original do commit `3b63d88` funciona).
- Catálogo completo de defeitos e cenários de teste em [`cenarios_de_teste.md`](cenarios_de_teste.md).

## 9. Decisões de regra confirmadas
| Tema | Decisão |
|---|---|
| Placar final | 30 pontos |
| Parda | Regra tradicional (2.3) |
| Envido | Tradicional, encadeável (Envido 2, Real 3, Falta); recusa = 1 ponto |
| Flor | Obrigatória, 3 pontos; Contra-flor 6; Contra-flor e o resto |
| Truco | Só quem recebe o canto pode aumentar |
| Falta Envido | Falta do líder para 30 |
| Mão | Sorteada na 1ª mão e alternada a cada mão |

## 10. Pontos ainda em aberto
- Ordem de precedência entre **Truco e Envido** quando cantados na mesma rodada (padrão: Envido “está primeiro”).
- Valor da recusa de **Contra-flor e o resto** e se existe “Con flor me achico”.
- Formato exato das colunas do CSV de casos e as features usadas na similaridade (a documentar a partir de `dados.py`/`cbr.py`).
- Política de retroalimentação da base (RF-56).
