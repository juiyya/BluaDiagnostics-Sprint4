# BluaDiagnostics - Care Plus Sprint 1

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
- **RAG:** Respostas fundamentadas em protocolos de triagem, políticas Care Plus e bulas.
- **Function Calling:** Integração simulada com sistemas de prontuário eletrônico (EHR) e agendas via chamadas de função.
- **Evals:** Conjunto de testes validando *happy paths*, *red flags* e tentativas de *jailbreak*.
- **Orquestração Multi-Agente:** Preparação de terreno para LangGraph gerenciar roteamento entre triagem, consulta e prescrição.

---

## Decisões Arquiteturais Sprint 1

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

### 3. Gestão de Riscos Clínicos

- **Alucinação Clínica:** Mitigada pelo confinamento do RAG a documentos oficiais aprovados e restrições absolutas no prompt.
- **Privacidade (LGPD):** Anonimização de PII no front-end; o LLM processa apenas identificadores criptografados ao usar tools.
- **Responsabilidade:** Implementação de *Human-in-the-loop (HITL)* obrigatório para aprovação de prescrições geradas pelas tools.

---

## Prerequisites

- Python 3.10+
- Conta no Google Colab (para rodar o notebook da PoC)
- Chaves de API do modelo de IA escolhido (ex: OpenAI, Anthropic ou Google)

---

## Project Structure

```
bluadiagnostics/
├── docs/
│   └── arquitetura.md           # Fluxograma completo (roteamento, RAG, tools)
├── evals/
│   └── sprint1_eval_set.json    # Dataset de validação (10+ casos de teste)
├── prompts/
│   └── system_prompt.md         # Diretrizes, papel, restrições e regras do agente
├── tools/
│   └── tools_spec.json          # Contratos JSON Schema das funções mockadas
├── notebooks/
│   └── sprint1_poc.py           # PoC em Python (Executável no Colab)
├── .gitignore                   # Arquivo de exclusão do git
└── README.md                    # Documentação principal
```

---

## Quick Start

### 1. Clone o Repositório

```bash
git clone https://github.com/sua-org/bluadiagnostics.git

```

### 2. Configure o Ambiente

```bash
%pip install -qU langchain langchain-ollama langgraph pydantic
import os
from langchain_core.tools import tool
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage
```
### 3. Execução da Prova de Conceito (PoC)

Abra o arquivo localizado em *notebooks/sprint1_poc.ipynb* utilizando o Google Colab ou o Jupyter Notebook local para testar a memória conversacional, o system prompt e o function calling.

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

- **Descrição:** Aciona o fluxo de agendamento ou entrada em fila de urgência com base no nível de prioridade da triagem.
- **Parâmetros:**
  - `id_paciente` (string)
  - `prioridade` (enum: alta, media, baixa)
  - `sintoma_principal` (string)

---

## RAG

Na Sprint 1, foram simulados 5 documentos que ancoram o conhecimento da IA:

- Protocolo de Triagem de Dor (Simplificado)
- Protocolo de Monitoramento de Sinais Vitais Pós-Operatórios
- Política Interna de Telemedicina Care Plus
- Bula resumida (ex: Dipirona, Paracetamol)
- Cartilha de prevenção de saúde primária do aplicativo Blua

---

## EVALS

A consistência da IA é medida contra o dataset `sprint1_eval_set.json`, que testa:

- **Happy Path:** Fluxos normais de relato de sintomas leves
- **Red Flags:** Relatos críticos (ex: dor no peito) que exigem escalada imediata e abandono do fluxo padrão
- **Jailbreak:** Tentativas do usuário de forçar a IA a fornecer receitas ou laudos definitivos

## Grupo 

- **RM568438** Julia Yamazaki
- **RM** 
- **RM** 
