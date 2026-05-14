# BluaDiagnostics - Care Plus Sprint 3 & 4

**Plataforma Inteligente de Cuidado Proativo** - Transformando o app Blua através de IA conversacional, check-ups digitais e orquestração segura de saúde.

---

## Overview

O **BluaDiagnostics** é uma iniciativa de inovação desenvolvida para a Care Plus (grupo Bupa). O objetivo é evoluir o ecossistema do aplicativo Blua de um modelo puramente reativo (agendamentos e consultas) para uma plataforma de cuidado proativo. 

A solução integra modelos de linguagem (LLMs) seguros em ambiente clínico para:

- **Digital Check-up:** Autoavaliação conversacional guiada para coleta de sinais vitais e rastreio de sintomas (*red flags*).
- **Prescrição Remota Inteligente:** Triagem e validação de interações medicamentosas que aceleram a tomada de decisão do médico.

---

## Features

- **Arquitetura:** System Prompts rigorosos com guardrails clínicos contra diagnósticos definitivos.
- **Function Calling:** Integração simulada com sistemas de prontuário eletrônico (EHR) e agendas via chamadas de função.
- **Evals:** Conjunto de testes validando *happy paths*, *red flags* e tentativas de *jailbreak*.
- **Orquestração Multi-Agente:** Preparação de terreno para LangGraph gerenciar roteamento entre triagem, consulta e prescrição.

---

## Decisões Arquiteturais Sprint 3

### 1. Persona Atendida

**Beneficiário final em autoavaliação (Digital Check-up).**

A escolha foca no gargalo de entrada do cuidado proativo. O agente foi desenhado com tom de voz empático e acessível, com a responsabilidade restrita à coleta de sintomas, cruzamento com histórico e acionamento de protocolos de urgência, escalando para o médico humano sem emitir diagnósticos.

---

### 2. Seleção de Modelos (LLMs)

Comparativo para a fundação da arquitetura:

- **Llama (Meta):**
  - Forte desempenho em tarefas de raciocínio e compreensão contextual
  - Boa flexibilidade para customização e fine-tuning
  - Ampla adoção open-source, permitindo maior controle sobre deploy e privacidade
  - Ecossistema maduro com suporte a diferentes infraestruturas (local e cloud)

- **Qwen (Alibaba):**
  - Excelente performance em benchmarks recentes, especialmente em tasks multilíngues
  - Boa capacidade de seguir instruções e gerar respostas estruturadas
  - Forte integração com ferramentas e APIs no ecossistema Alibaba
  - Ainda em crescimento em termos de comunidade e suporte fora do ambiente nativo

**Decisão Técnica:**  
Optou-se pelo **Llama** devido à sua maior maturidade no ecossistema open-source, flexibilidade de implementação e melhor alinhamento com requisitos de privacidade e controle da solução, fatores críticos para aplicações em contexto clínico.

---

### Mapeamento de Riscos Clínicos e Éticos 

| Risco Identificado | Descrição no Contexto de Saúde | Mitigação na Arquitetura | Mitigação no System Prompt |
| :--- | :--- | :--- | :--- |
| **Alucinação Médica** | O LLM inventar protocolos, valores de referência ou diagnósticos inexistentes. | Uso exclusivo de RAG (base de conhecimento validada) e temperatura `0` no Llama 3.1 para respostas determinísticas. | *"Responda estritamente com base no contexto fornecido. Se a resposta não estiver no contexto, diga: 'Não tenho essa informação'."* |
| **Viés (Bias) Algorítmico** | O modelo priorizar ou negligenciar sintomas com base em vieses de treinamento. | Adoção do Protocolo de Manchester estruturado via RAG, padronizando a classificação de gravidade para todos os pacientes. | *"Siga rigorosamente as diretrizes de triagem listadas nos documentos. Não aplique julgamentos externos."* |
| **Privacidade e LGPD** | Vazamento de dados sensíveis de saúde (sinais vitais, prontuários). | Execução do LLM localmente (Ollama) e banco vetorial interno (PGVector). Dados não transitam em APIs de terceiros. | *"Você está lidando com dados sensíveis protegidos pela LGPD. Nunca mencione o nome do paciente em exemplos."* |
| **Responsabilidade de Prescrição** | O chatbot atuar como médico, sugerindo alterações em dosagens ou novos medicamentos. | Limitação de escopo (Out of Scope) definida nas avaliações. O bot atua apenas como interface de monitoramento. | *"Você é um assistente de monitoramento. NUNCA diagnostique ou prescreva medicamentos. Sempre oriente a busca por um médico."* |
| **Human-in-the-Loop (HITL)** | A IA reter informações críticas (ex: SpO2 baixo) sem alertar a equipe médica. | Criação de "gatilhos de transbordo". Se a regra de RAG classificar como "Emergência", o sistema aciona uma API para alertar um médico real. | *"Se o paciente apresentar sinais de alerta vermelho (ex: SpO2 < 92%), instrua-o a ir ao pronto-socorro e informe que a equipe médica foi notificada."* |

---

## Function Calling

A PoC inclui os seguintes contratos de ferramentas (Tools) disponíveis para a IA acionar durante o diálogo:

### `consultar_historico_paciente`

- **Descrição:** Busca o histórico médico básico do paciente (alergias, cirurgias, condições crônicas).
- **Parâmetros:** `id_paciente`

---

### `verificar_interacoes_medicamentosas`

- **Descrição:** Cruza uma medicação sugerida com o histórico de alergias e prescrições ativas do usuário.
- **Parâmetros:**
  - `medicamento_sugerido` (string)
  - `id_paciente` (string)

---

### `agendar_teleconsulta`
(sprint 4)
- **Descrição:** Aciona o fluxo de agendamento ou entrada em fila de urgência com base no nível de prioridade da triagem.
- **Parâmetros:**
  - `id_paciente` (string)
  - `prioridade` (enum: alta, media, baixa)
  - `sintoma_principal` (string)

---

## RAG 
vamos transfomar o RAG em uma tool. 
Para essa implementação, escolhi ChromaDB (fácil de rodar localmente sem subir containers) e HuggingFaceEmbeddings (modelo leve e gratuito, ótimo para testes).

## Evals

A consistência da IA é medida contra o dataset `sprint1_eval_set.json`, que testa:

- **Happy Path:** Fluxos normais de relato de sintomas leves
- **Red Flags:** Relatos críticos (ex: dor no peito) que exigem escalada imediata e abandono do fluxo padrão
- **Jailbreak:** Tentativas do usuário de forçar a IA a fornecer receitas ou laudos definitivos

## Prerequisites

- Python 3.10+
- Conta no Google Colab (para rodar o notebook da PoC)

---

## Project Structure

```
bluadiagnostics/
├── docs/
│   └── arquitetura.md          # Fluxograma
│   └── arquitetura.png  
├── evals/
│   └── sprint1_eval_set.json   # Suite de avaliação automatizada (evals) para medir qualidade das respostas.
├── knowledge_base/
    └── bula_simplificada_losartana.md 
    └── cartilha_beneficiario_pos_operatorio.md
    └── diretriz_privacidade_lgpd_careplus.md
    └── politica_careplus_telemedicina.md
    └── protocolo_triagem_manchester_vital.md 
├── notebooks/
│   └── sprint1_poc.ipynb        # PoC 
├── prompts/
│   └── system_prompt.md         # Diretrizes, papel, restrições e regras do agente
├── tools/
│   └── tools_spec.json          # JSON Schema das funções mockadas
    └── tools_spec.py
├── .gitignore                   
└── grupo.txt                    # Integrantes do grupo
│── LICENSE                      
└── README.md                    
```

---

## Quick Start

### 1. Clone o Repositório

```bash
git clone https://github.com/sua-org/bluadiagnostics.git

```

### 2. Configure o Ambiente

```bash
pip install -U -r requirements.txt
```
OR
```bash
%pip install -qU langchain langchain-ollama langgraph pydantic
```
```bash
ollama run llama3.1
```

### 3. Execução da Prova de Conceito (PoC)

Abra o arquivo localizado em *notebooks/sprint1_poc.ipynb* utilizando o Google Colab ou o Jupyter Notebook local para testar a memória conversacional, o system prompt e o function calling.

---

## Grupo 

- **RM568438** Julia Yamazaki
- **RM568081** Bryan de Almeida 
- **RM566746** Guilherme Blanco
- **RM**
- **RM**

