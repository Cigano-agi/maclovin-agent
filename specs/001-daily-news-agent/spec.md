# Feature Specification: Daily News Intelligence Agent V1

**Feature Branch**: `001-daily-news-agent`
**Created**: 2026-08-16
**Status**: Draft
**Input**: Criar um agente local que, quando executado após o computador iniciar, pesquise notícias publicadas no dia anterior relacionadas a Inteligência Artificial e outros assuntos configurados pelo usuário, organize os resultados e produza um briefing diário confiável.

## Clarifications

### Session 2026-08-16
- Q: Como o usuário deve gerenciar e configurar os tópicos de interesse e as fontes de notícias na versão V1? → A: Arquivo declarativo em formato YAML (`config/config.yaml`), com seções estruturadas para tópicos, palavras-chave e URLs de feeds/fontes de dados.
- Q: Em qual formato e local o relatório do Briefing Diário deve ser gerado e entregue ao usuário na versão V1? → A: Arquivo Markdown dedicado por data (`briefings/YYYY-MM-DD.md`) contendo eventos agrupados, resumos e links diretos, com exibição síncrona de resumo executivo no console/stdout.
- Q: Qual mecanismo de armazenamento local o sistema deve utilizar para persistir o histórico de notícias, eventos agrupados e logs de execução? → A: Banco de dados relacional embutido SQLite (`data/maclovin.db`), garantindo integridade transacional, constraints de unicidade para idempotência e consultas estruturadas de histórico.
- Q: Como o agente deve se conectar aos provedores de Inteligência Artificial (LLM) para as etapas de classificação, agrupamento e sumarização? → A: Adaptador de IA desacoplado e configurável via `config/config.yaml` e variáveis de ambiente (`.env`), suportando múltiplos provedores (Google Gemini, OpenAI, Anthropic e Ollama local), com chaves nunca expostas no código.
- Q: Como o agente deve disponibilizar a execução manual e o mecanismo de inicialização automática no Windows na versão V1? → A: Comando CLI unificado (`python -m maclovin run` / `maclovin run`) com suporte a execução manual e script auxiliar PowerShell (`scripts/setup_startup.ps1`) para registro opcional no Startup / Agendador de Tarefas do Windows.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Receber as notícias relevantes de ontem (Priority: P1)

Como usuário, quero que o agente identifique notícias publicadas no dia anterior relacionadas aos assuntos que acompanho para que eu possa começar o dia sabendo o que aconteceu sem procurar manualmente em várias fontes.

**Why this priority**: É o valor central da aplicação (MVP mínimo viável). Sem a entrega de notícias filtradas por data e relevância, o produto não cumpre sua função primária.

**Independent Test**: Configurar pelo menos um tópico, executar o agente sobre um conjunto de notícias com datas diversas e verificar se o briefing final contém apenas conteúdos pertencentes ao dia anterior (00:00 às 23:59) e aderentes ao tópico configurado.

**Acceptance Scenarios**:

1. **Given** que existem notícias publicadas ontem relacionadas a um tópico configurado, **When** o agente realizar sua pesquisa diária, **Then** essas notícias devem ser consideradas para o briefing.
2. **Given** que uma notícia foi publicada antes ou depois do período de D-1 (00:00 a 23:59), **When** ela for encontrada na coleta, **Then** ela não deve ser apresentada como notícia válida do período.
3. **Given** que nenhuma notícia relevante seja encontrada para a data analisada, **When** a execução terminar, **Then** o briefing deve informar claramente que nenhum resultado relevante foi encontrado, sem sinalizar erro na execução.

---

### User Story 2 - Configurar assuntos de interesse (Priority: P1)

Como usuário, quero definir os assuntos que desejo acompanhar para que o briefing represente meus interesses atuais e possa evoluir ao longo do tempo.

**Why this priority**: A personalização de temas é indispensável para evitar ruído e atender as necessidades individuais de acompanhamento informativo.

**Independent Test**: Modificar a lista de tópicos configurados, disparar uma nova pesquisa e verificar se os resultados refletem rigorosamente a configuração ativa atualizada.

**Acceptance Scenarios**:

1. **Given** que o usuário possui múltiplos assuntos configurados, **When** o agente processar as notícias, **Then** cada notícia relevante deve ser associada a pelo menos um assunto correspondente.
2. **Given** que um novo assunto seja adicionado, **When** uma execução posterior acontecer, **Then** o novo assunto deve passar a fazer parte da pesquisa e classificação.
3. **Given** que um assunto existente seja removido ou desativado, **When** uma execução posterior acontecer, **Then** ele não deve mais ser considerado para novos briefings.

---

### User Story 3 - Identificar a origem e proveniência das informações (Priority: P1)

Como usuário, quero saber com precisão de onde cada informação veio para poder auditar e verificar o conteúdo original na fonte quando necessário.

**Why this priority**: Garante a confiabilidade das informações e conformidade com os princípios de transparência da constituição.

**Independent Test**: Selecionar qualquer notícia apresentada no briefing e validar se o nome da fonte original, a URL canônica e a data de publicação estão claramente expostos e acessíveis.

**Acceptance Scenarios**:

1. **Given** que uma notícia seja incluída no briefing, **Then** ela deve obrigatoriamente possuir fonte identificável e link para a publicação original.
2. **Given** que a origem ou autoria de determinado conteúdo não possa ser determinada, **Then** essa informação não deve ser apresentada como fato confiável.

---

### User Story 4 - Evitar notícias duplicadas e agrupar coberturas (Priority: P1)

Como usuário, quero que diferentes matérias ou republicações sobre o mesmo acontecimento sejam agrupadas em um único evento para não perder tempo lendo sobre o mesmo fato repetidamente.

**Why this priority**: Reduz drasticamente a fadiga de leitura e consolida perspectivas de múltiplas fontes sobre o mesmo acontecimento.

**Independent Test**: Injetar múltiplos itens de notícias de diferentes fontes cobrindo o mesmo evento e validar se o briefing consolida esses itens sob um único evento estruturado.

**Acceptance Scenarios**:

1. **Given** que duas ou mais fontes cubram essencialmente o mesmo acontecimento, **When** as notícias forem organizadas, **Then** elas devem ser agrupadas como um mesmo evento sempre que houver confiança de que representam o mesmo fato.
2. **Given** que duas notícias tenham termos ou temas semelhantes, mas descrevam acontecimentos distintos, **Then** elas devem permanecer separadas.

---

### User Story 5 - Priorizar acontecimentos por relevância (Priority: P1)

Como usuário, quero que as notícias sejam ordenadas por grau de importância e aderência aos tópicos para que eu possa focar primeiro no que é mais relevante.

**Why this priority**: Permite leitura dinâmica e assimilação rápida dos eventos mais impactantes do dia anterior.

**Independent Test**: Processar um conjunto de notícias com diferentes graus de relevância em relação aos tópicos e verificar se o briefing lista no topo as matérias com maior pontuação/prioridade.

**Acceptance Scenarios**:

1. **Given** várias notícias válidas do período, **When** o briefing for produzido, **Then** elas devem ser organizadas em ordem decrescente de relevância para os assuntos configurados.
2. **Given** conteúdo apenas superficialmente ou tangencialmente relacionado aos tópicos, **Then** ele deve possuir prioridade estritamente inferior a conteúdos centrais.

---

### User Story 6 - Obter resumos objetivos e factuais (Priority: P1)

Como usuário, quero receber um resumo curto e 100% fundamentado no texto coletado de cada notícia para entender o fato sem ler matérias inteiras e sem risco de alucinações.

**Why this priority**: Cumpre a exigência constitucional de zero alucinação (Strict Grounding) e economiza tempo do usuário.

**Independent Test**: Comparar o resumo gerado com o texto original da fonte e validar que todos os fatos citados estão presentes no material original, sem inserção de dados externos.

**Acceptance Scenarios**:

1. **Given** conteúdo textual suficiente sobre uma notícia, **When** ela for resumida, **Then** o resumo deve conter somente informações extraídas e sustentadas pelo material coletado.
2. **Given** conteúdo insuficiente ou truncado, **Then** o sistema deve registrar a limitação e indicar explicitamente que não há dados suficientes para um resumo completo.
3. **Given** que uma contextualização seja gerada, **Then** ela deve ser explicitamente distinguível dos fatos declarados na matéria.

---

### User Story 7 - Entender o motivo de importância de cada notícia (Priority: P2)

Como usuário, quero uma breve explicação de por que cada acontecimento é relevante no contexto dos meus tópicos de interesse para distinguir acontecimentos transformadores de ruídos passageiros.

**Why this priority**: Adiciona inteligência de contexto à leitura sem comprometer a objetividade factual.

**Independent Test**: Verificar se itens com alta relevância trazem uma seção clara de 'Por que importa' vinculada ao tópico monitorado.

**Acceptance Scenarios**:

1. **Given** uma notícia de alta relevância, **Then** o briefing pode apresentar um campo explicativo contextualizando o impacto potencial do fato.
2. **Given** que a justificativa é uma análise interpretativa, **Then** ela deve ser visualmente e semanticamente separada dos fatos apurados.

---

### User Story 8 - Preservar histórico e assegurar idempotência (Priority: P2)

Como usuário, quero que execuções anteriores fiquem salvas e que reexecuções no mesmo dia não gerem registros duplicados para garantir consistência e rastreabilidade.

**Why this priority**: Atende o princípio constitucional de idempotência e possibilita consultas retroativas a briefings anteriores.

**Independent Test**: Executar o agente duas vezes no mesmo dia para a mesma janela temporal e verificar se o número de itens armazenados e os briefings gerados permanecem consistentes sem duplicações.

**Acceptance Scenarios**:

1. **Given** uma notícia já coletada e armazenada em execução anterior, **When** uma nova execução a encontrar novamente, **Then** o sistema deve reconhecer o item existente e evitar duplicação.
2. **Given** um briefing gerado e concluído, **Then** ele deve permanecer acessível e inalterado para consultas futuras.

---

### User Story 9 - Acompanhar a integridade e status de cada execução (Priority: P2)

Como usuário, quero saber com clareza se a execução diária concluiu com êxito total, falhas parciais ou erro impeditivo para não confiar cegamente em um relatório que possa estar incompleto.

**Why this priority**: Garante observabilidade operacional e transparência sobre fontes indisponíveis.

**Independent Test**: Simular falha de conexão em uma fonte específica e verificar se o relatório final indica status 'concluído com falhas parciais' listando a fonte afetada e mantendo os resultados das fontes operacionais.

**Acceptance Scenarios**:

1. **Given** que uma das fontes configuradas retorne erro ou timeout, **When** as demais fontes operarem normalmente, **Then** o agente deve concluir o briefing indicando a falha pontual daquela fonte.
2. **Given** que todas as fontes falhem ou não haja conectividade, **Then** a execução deve ser registrada com status de falha com log correspondente.

---

### Edge Cases

- **EC-001 (Múltiplas execuções no mesmo dia)**: Execuções subsequentes na mesma data devem operar de forma estritamente idempotente, reutilizando registros conhecidos sem duplicações.
- **EC-002 (Ausência total de notícias)**: Quando nenhum item atender aos filtros de data ou relevância, o sistema deve emitir briefing válido com aviso de que nenhuma notícia foi encontrada, com status de sucesso.
- **EC-003 (Indisponibilidade de fonte individual)**: Timeout ou erro 4xx/5xx em uma fonte deve ser isolado via fallback/circuit breaker, registrando warning no log e prosseguindo com as fontes restantes.
- **EC-004 (Data de publicação ausente ou inconsistente)**: Se a data não puder ser confirmada como pertencente a D-1 com alto grau de confiança, o item é descartado do período analisado.
- **EC-005 (Data de modificação divergente)**: A data de publicação original prevalece sobre datas de atualização editorial na determinação da janela temporal de D-1.
- **EC-006 (Mesma notícia em múltiplas fontes)**: Itens com cobertura simultânea devem ser correlacionados em um único evento, listando todas as fontes que reportaram o fato.
- **EC-007 (Notícia vinculada a múltiplos tópicos)**: O item é associado a todos os tópicos pertinentes sem gerar duplicação física no armazenamento de notícias.
- **EC-008 (Matéria com conteúdo textual insuficiente ou bloqueado)**: Preserva-se o título, metadados e URL, sinalizando que o resumo integral foi inviabilizado pela brevidade do conteúdo.
- **EC-009 (Interrupção inesperada de execução)**: Execuções abortadas no meio do processamento devem ser registradas com status 'interrompida/falha' para permitir retomada segura.
- **EC-010 (Conteúdo republicado ou espelhado)**: Republicações de agências de notícias com o mesmo corpo de texto devem ser consolidadas sob o mesmo evento original.

## Requirements *(mandatory)*

### Functional Requirements

#### Configuração e Escopo
- **FR-001**: O sistema MUST permitir a configuração e manutenção de tópicos, palavras-chave e fontes de dados através de arquivo declarativo YAML (`config/config.yaml`).
- **FR-002**: O sistema MUST permitir múltiplos tópicos simultaneamente ativos.
- **FR-003**: O sistema MUST permitir a inclusão, edição e desativação de tópicos sem alterar o comportamento global do pipeline.
- **FR-004**: O sistema MUST validar a integridade do schema YAML e persistir as preferências e configurações de forma duradoura entre execuções.

#### Janela Temporal e Fuso Horário
- **FR-005**: O sistema MUST calcular a janela temporal padrão como o intervalo de 00:00:00 até 23:59:59 do dia anterior (D-1), utilizando fuso horário configurável.
- **FR-006**: O sistema MUST exigir que cada notícia possua data de publicação validada antes de considerá-la pertencente à janela de D-1.
- **FR-007**: Notícias com data de publicação indeterminada ou não confiável MUST NOT ser aceitas como notícias válidas do dia anterior.

#### Coleta Determinística e Ética
- **FR-008**: O sistema MUST consultar as fontes configuradas (feeds RSS/Atom e APIs estruturadas prioritariamente; HTML scraping como fallback secundário).
- **FR-009**: O sistema MUST coletar e registrar a origem exata de cada item encontrado.
- **FR-010**: O sistema MUST isolar falhas individuais de fontes, impedindo que a queda de uma fonte interrompa a execução das demais.
- **FR-011**: O sistema MUST NOT tentar contornar ou violar mecanismos de bloqueio, autenticação obrigatória, paywalls ou CAPTCHAs.
- **FR-012**: A etapa de coleta e extração de metadados brutos MUST funcionar de maneira 100% determinística sem dependência de modelos de IA; o processamento de IA (classificação, agrupamento e resumos) MUST utilizar adaptador desacoplado e configurável (Google Gemini, OpenAI, Anthropic ou Ollama local) com credenciais carregadas via `.env`.

#### Normalização e Integridade de Metadados
- **FR-013**: Para cada notícia coletada, o sistema MUST persistir obrigatoriamente: `fonte`, `titulo`, `url_canonica`, `data_publicacao_utc` (normalizada em UTC) e `data_coleta_utc`.
- **FR-014**: Conteúdos sem URL canônica ou sem fonte identificável MUST NOT ser persistidos como itens confiáveis.

#### Relevância, Classificação e Agrupamento
- **FR-015**: O sistema MUST avaliar a aderência semântica de cada notícia aos tópicos configurados.
- **FR-016**: Notícias consideradas sem aderência relevante aos tópicos MUST ser excluídas do briefing principal.
- **FR-017**: O sistema MUST atribuir pontuação ou nível de relevância aos itens aceitos.
- **FR-018**: O sistema MUST detectar e agrupar notícias republicadas ou matérias de fontes distintas que cobrem o mesmo acontecimento sob uma única entidade de Evento.

#### Resumos e Anti-Alucinação
- **FR-019**: O sistema MUST gerar resumos objetivos e concisos para as notícias principais através do adaptador de IA configurado.
- **FR-020**: Os resumos MUST NOT inventar, extrapolar ou alucinar fatos não comprovados pelo conteúdo coletado (Strict Grounding).
- **FR-021**: Quando o conteúdo for insuficiente para gerar um resumo fiel, o sistema MUST sinalizar essa limitação explicitamente.
- **FR-022**: O briefing MUST distinguir claramente declarações factuais provenientes das fontes de eventuais análises de contexto ('Por que importa').

#### Geração de Briefing Diário
- **FR-023**: O sistema MUST gerar um relatório de briefing diário em formato Markdown persistido em `briefings/YYYY-MM-DD.md` e exibir simultaneamente uma síntese executiva no console/stdout ao final da execução.
- **FR-024**: O briefing MUST exibir explicitamente a data de referência analisada e o timestamp de geração.
- **FR-025**: O briefing MUST ordenar as notícias/eventos por ordem de relevância.
- **FR-026**: Cada item do briefing MUST conter título, fonte(s), link direto, resumo conciso e justificativa de relevância.
- **FR-027**: O briefing MUST NOT exibir o texto integral das matérias originais.

#### Histórico, Idempotência e Auditoria
- **FR-028**: O sistema MUST persistir o histórico de itens coletados, entidades de eventos e logs de execução em banco relacional embutido SQLite (`data/maclovin.db`), com constraints de unicidade para garantia estrita de idempotência.
- **FR-029**: Múltiplas execuções sobre o mesmo período MUST NOT gerar registros de notícias ou briefings duplicados.
- **FR-030**: O sistema MUST disponibilizar interface CLI unificada (`python -m maclovin run` / `maclovin run`) para acionamento manual sob demanda, acompanhada de script PowerShell de setup (`scripts/setup_startup.ps1`) para registro opcional na inicialização automática do Windows.
- **FR-031**: Toda execução MUST gerar registros de log estruturados detalhando fontes consultadas, contagem de itens, itens ignorados e eventuais falhas.
- **FR-032**: Cada execução MUST registrar seu estado final: `Concluída com Sucesso`, `Concluída com Falhas Parciais` ou `Falhou`.

### Key Entities

- **Topic**: Representa um assunto ou área de interesse monitorada. Atributos: `id`, `nome`, `palavras_chave`, `ativo`, `prioridade`.
- **Source**: Representa uma fonte de informação (RSS feed, API ou página). Atributos: `id`, `nome`, `tipo_ingestao` (rss/api/html), `url`, `ativo`, `status_ultima_coleta`.
- **NewsItem**: Representa um artigo ou matéria individual coletada. Atributos: `id`, `fonte_id`, `titulo`, `url_canonica`, `data_publicacao_utc`, `data_coleta_utc`, `conteudo_bruto`, `topicos_associados`, `score_relevancia`, `resumo`, `porque_importa`.
- **Event**: Representa um fato ou acontecimento coberto por uma ou mais notícias. Atributos: `id`, `titulo_consolidado`, `topico_principal`, `news_item_ids`, `score_relevancia`, `resumo_consolidado`.
- **Briefing**: Representa o relatório diário entregue ao usuário. Atributos: `id`, `data_referencia_d_minus_1`, `data_geracao_utc`, `eventos_principais`, `estatisticas_execucao`, `alertas_e_falhas`.
- **ExecutionLog**: Representa o registro de uma execução do pipeline. Atributos: `id`, `data_referencia`, `timestamp_inicio`, `timestamp_fim`, `status` (sucesso/parcial/falha), `fontes_consultadas`, `itens_coletados`, `itens_duplicados_ignorados`, `erros`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Em 100% das execuções válidas, todas as notícias apresentadas no briefing pertencem estritamente à janela temporal de D-1 (00:00 a 23:59).
- **SC-002**: 100% dos itens incluídos no briefing possuem fonte identificável, link canônico válido e data de publicação comprovada.
- **SC-003**: A reexecução do pipeline no mesmo dia resulta em 0% de itens de notícia duplicados no repositório de dados.
- **SC-004**: O pipeline conclui o processamento com sucesso mesmo quando até 50% das fontes individuais apresentarem indisponibilidade temporária.
- **SC-005**: 100% dos resumos gerados contêm apenas fatos verificáveis a partir do material textual coletado, com zero inferências externas alucinadas.
- **SC-006**: O tempo total de leitura e assimilação do briefing diário é inferior a 5 minutos para o usuário final.
- **SC-007**: A execução completa diária ocorre de forma 100% autônoma, sem solicitar intervenções ou decisões manuais do usuário após o disparo.
- **SC-008**: Em cenários onde nenhuma notícia relevante é encontrada, o usuário é notificado em até 30 segundos com mensagem conclusiva explícita (distinta de estado de erro).
- **SC-009**: Novos tópicos de interesse são adicionados e refletidos no próximo ciclo de coleta sem necessidade de alteração de código ou reinicialização complexa.
- **SC-010**: Histórico completo de execuções, fontes e briefings anteriores permanece acessível para consulta imediata.

## Assumptions

- **A-001**: O agente é projetado para operação local em ambiente monousuário na versão V1.
- **A-002**: A máquina do usuário possui conexão com a internet durante a janela de execução do agente.
- **A-003**: O fuso horário padrão é configurado pelo usuário (default: fuso local da máquina).
- **A-004**: Caso a máquina fique desligada por múltiplos dias consecutivos, a execução padrão analisa unicamente o dia anterior (D-1) à data atual de inicialização; reprocessamento em lote de múltiplos dias anteriores fica fora do escopo da V1.
- **A-005**: As fontes configuradas são públicas e acessíveis sem necessidade de autenticação privada ou invasão de controles de acesso.
- **A-006**: Um item de notícia pode pertencer a múltiplos tópicos monitorados simultaneamente.
- **A-007**: O briefing atua como sintetizador executivo e curador de links de alta relevância, não como arquivador de textos integrais de imprensa.

## Out of Scope — V1

- Interface gráfica web ou aplicativo mobile.
- Dashboard analítico complexo ou painéis em tempo real.
- Multi-inquilino (multi-tenant) ou sistema de autenticação de múltiplos usuários.
- Publicação ou compartilhamento automático em redes sociais (X/Twitter, LinkedIn, etc.).
- Envio automatizado por mensageiros (WhatsApp, Telegram, Discord) ou servidores de e-mail externos na V1.
- Monitoramento contínuo ininterrupto 24/7 (o foco da V1 é o disparo diário/on-demand).
- Recuperação retroativa automática em massa de múltiplos dias perdidos.
- Sistema de perguntas e respostas livre sobre todo o histórico (RAG corporativo completo).
- Bancos de dados vetoriais distribuídos ou arquiteturas multiagente complexas.
- Ações automatizadas no mundo real baseadas nas notícias (ex: ordens de compra, investimentos, etc.).
