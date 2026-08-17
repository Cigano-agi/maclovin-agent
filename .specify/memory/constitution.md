<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.1.0
- List of modified principles:
  - PRINCIPLE_1 to PRINCIPLE_9: Preserved intact (Temporal Window, Idempotency, Schema Integrity, Strict Grounding, Ethical Scraping, Deterministic vs AI, Fault Tolerance, Observability, Output Optimization)
- Added principles:
  - PRINCIPLE_10: Ciclo TDD Mandatório e Desacoplamento (Test-First & Red-Green-Refactor)
  - PRINCIPLE_11: Isolamento Seguro e Mocking de Dependências (Mocking & Dependency Isolation)
  - PRINCIPLE_12: Defesa em Profundidade e Prevenção de Falhas Lógicas (Security-First & Logic Hardening)
  - PRINCIPLE_13: Validação Ativa e Portões de Aceitação (Active Validation & Acceptance Gates)
- Added sections:
  - Diretrizes de Engenharia e Segurança de Código (Engineering & Security Standards)
  - Critérios de Qualidade e Portões de Testes (Quality Gates & Test Discipline)
- Removed sections: None
- Follow-up TODOs: None
-->

# maclovin Constitution

## Core Principles

### I. Janela Temporal e Fuso Horário (Configurable Window & Timezone)
O período padrão de coleta e processamento abrange estritamente o intervalo de 00:00:00 até 23:59:59 do dia anterior (D-1). O fuso horário de referência DEVE ser explicitamente configurável no ambiente/projeto para evitar inconsistências temporais.

### II. Idempotência e Desduplicação (Idempotency & Deduplication)
O pipeline DEVE ser totalmente idempotente: reexecuções consecutivas para a mesma janela temporal não podem gerar registros duplicados ou processamento redundante. Notícias republicadas, espelhadas ou com cobertura do mesmo fato entre fontes distintas DEVEM ser agrupadas em uma única entidade de cobertura.

### III. Integridade e Esquema Obrigatório de Dados (Mandatory Metadata Schema)
Nenhum item pode ser persistido ou processado sem conter obrigatoriamente os seguintes campos:
- **Fonte** (nome/identificador da origem)
- **Título** (título original publicado)
- **URL** (link canônico da matéria)
- **Data de publicação** (timestamp original normalizado)
- **Data de coleta** (timestamp do momento da captura)

### IV. Fidelidade Factual e Anti-Alucinação (Strict Grounding & Zero Hallucination)
O sistema e qualquer modelo de IA utilizado NUNCA devem inferir, extrapolar ou inventar informações ausentes no texto original da matéria. Resumos, classificações e análises DEVEM estar 100% fundamentados no material coletado.

### V. Priorização de Ingestão e Coleta Ética (API/RSS First & Ethical Scraping)
Fontes estruturadas (feeds RSS, Atom e APIs oficiais) DEVEM ser priorizadas sempre que disponíveis. Coleta via HTML (scraping) é utilizada unicamente como mecanismo de fallback secundário. É terminantemente PROIBIDO tentar burlar paywalls, autenticações (login), CAPTCHAs ou contornar bloqueios/mecanismos de proteção dos veículos de imprensa.

### VI. Separação entre Coleta Determinística e IA (Deterministic Ingestion vs. AI Logic)
A etapa de coleta, parsing inicial e persistência bruta DEVE operar de forma 100% determinística e independente de LLMs. Modelos de IA são acionados exclusivamente em etapas posteriores para classificação temático-semântica, agrupamento por relevância/tópico e sumarização executiva.

### VII. Resiliência a Falhas de Fontes (Fault Tolerance & Source Isolation)
O pipeline DEVE ser tolerante a falhas pontuais: indisponibilidade, timeout, mudanças de layout ou erros de conexão em uma ou mais fontes individuais NÃO DEVEM interromper a execução do fluxo para as demais fontes. O erro da fonte afetada deve ser isolado e registrado.

### VIII. Observabilidade e Auditoria Contínua (Structured Logging & Observability)
Toda execução do agente DEVE obrigatoriamente gerar logs detalhados e estruturados, registrando o início/término da execução, fontes consultadas, volume de itens capturados, itens ignorados por duplicidade e eventuais advertências/falhas parciais.

### IX. Síntese e Otimização de Saída (Concise Output & Summary Focus)
O relatório e artefatos de saída gerados para o usuário NÃO devem incluir o texto integral da matéria. O foco da entrega é o agrupamento inteligente, classificação, sínteses objetivas e ponteiros (URLs) diretos para as matérias originais.

### X. Ciclo TDD Mandatório e Desacoplamento (Test-First & Red-Green-Refactor)
O desenvolvimento DEVE seguir rigorosamente o ciclo TDD: testes automatizados são escritos antes do código funcional. Inicie sempre pelo teste que falha (Red), implemente o código mínimo estritamente necessário para passar (Green) e execute refatoração focada em otimização, legibilidade e manutenibilidade (Refactor). Componentes devem ser desacoplados por design, e os testes unitários devem ser independentes com alta cobertura contra regressões.

### XI. Isolamento Seguro e Mocking de Dependências (Mocking & Dependency Isolation)
Ao testar ou integrar dependências complexas, externas ou de I/O de rede (APIs remotas, feeds RSS externos, provedores de LLM), DEVE-SE utilizar objetos simulados (mocks/stubs) para isolar o ambiente de testes, garantindo rapidez, determinismo e confiabilidade das suítes de teste sem chamadas desnecessárias a serviços externos.

### XII. Defesa em Profundidade e Prevenção de Falhas Lógicas (Security-First & Logic Hardening)
Todas as soluções geradas devem adotar uma perspectiva de segurança proativa e defesa em profundidade. Atenção redobrada DEVE ser dada à consistência da lógica de negócios e às etapas de empacotamento/implantação (deployment), prevenindo vulnerabilidades lógicas, falhas silenciosas e vazamentos de credenciais.

### XIII. Validação Ativa e Portões de Aceitação (Active Validation & Acceptance Gates)
Critérios de aceitação objetivos DEVEM ser definidos previamente para que cada etapa de implementação possua metas concretas e verificáveis de validação antes de ser aprovada.

## Restrições Técnicas e Políticas de Ingestão

- **Consistência de Tipos e Formatos**: Timestamps normalizados em formato ISO 8601 UTC com conversão para a timezone configurada no relatório final.
- **Tratamento de Exceções**: Circuit breakers ou fallbacks por fonte para evitar travamentos de pipeline e exaustão de conexões de rede.
- **Armazenamento Seguro**: Isolamento de dados brutos e dados processados para facilitar auditoria e reprocessamento determinístico de etapas específicas se necessário.

## Diretrizes de Engenharia e Segurança de Código

- **Defesa em Profundidade**: Validação rigorosa de entradas (schemas, URLs, tipos de dados) na borda do sistema antes de qualquer processamento interno.
- **Isolamento de Segredos e Configurações**: Credenciais (chaves de API, tokens) nunca devem ser hardcoded em código-fonte, utilizando variáveis de ambiente ou arquivos locais protegidos/ignorados no controle de versão.
- **Robustez de Deployment**: Scripts de execução e agendamento local devem possuir verificações de integridade de ambiente pré-voo.

## Governança e Controle de Conformidade

- **Supremacia da Constituição**: Os princípios descritos neste documento são a autoridade máxima de arquitetura e implementação do projeto. Qualquer pull request, refatoração ou prompt de IA deve cumprir integralmente estas diretrizes.
- **Procedimento de Emendas**: Alterações nestas regras exigem revisão justificada, atualização do número de versão deste documento e adaptação dos fluxos afetados.
- **Versionamento Semântico da Constituição**:
  - **MAJOR**: Alteração estrutural ou revogação de princípios imutáveis.
  - **MINOR**: Inclusão de novos princípios ou ampliação substancial de diretrizes operacionais.
  - **PATCH**: Correções de texto, ajustes de clareza ou pequenos refinamentos semânticos.

**Version**: 1.1.0 | **Ratified**: 2026-08-16 | **Last Amended**: 2026-08-16
