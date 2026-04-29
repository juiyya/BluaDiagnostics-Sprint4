```mermaid
    %% Entidades Externas
    U[Usuário / Paciente] --> |Mensagem| App[App Blua]
    M[Médico Care Plus] --> |Aprovação| App
    
    %% Core System
    App --> |State/Context| LG[LangGraph Orchestrator]
    
    %% LangGraph Nodes
    LG --> |Routing| Triagem[Agente de Check-up Digital]
    LG --> |Routing| Copiloto[Agente de Prescrição Remota]
    
    %% Guardrails & Memória
    Triagem --> Guardrails{Red Flag Check}
    Guardrails --> |Sem risco grave| Mem[Session Memory]
    Guardrails --> |Risco Grave Detectado| Escalonamento[Alerta de Emergência / Telemedicina Imediata]
    
    %% Tools & RAG
    Triagem -.-> |Function Call| Tool1[tool: get_wearable_data]
    Copiloto -.-> |Function Call| Tool2[tool: check_drug_interaction]
    Copiloto -.-> |Busca Semântica| RAG[RAG: Base Clínica & Políticas]
    
    %% Banco de Dados
    Tool1 -.-> DB[(Histórico do Paciente / LGPD)]
    RAG -.-> VectorDB[(Vector DB: Protocolos)]
    
    %% Fluxo de Retorno
    Mem --> App
    Copiloto --> |Sugestão de Receita| M

```mermaid