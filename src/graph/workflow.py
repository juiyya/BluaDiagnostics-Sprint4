import sys
import json
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END, MessagesState

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

from src.tools.tools_spec import (
    buscar_dados_wearable,
    buscar_historico_paciente,
    agendar_teleconsulta,
    buscar_diretrizes_careplus
)

llm = ChatOllama(model="llama3.1", temperature=0)

tools_triagem = [buscar_dados_wearable, buscar_historico_paciente, buscar_diretrizes_careplus]
tools_agendamento = [agendar_teleconsulta]

caminho_prompt = BASE_DIR / "src" / "agents" / "system_prompt.md"
with open(caminho_prompt, "r", encoding="utf-8") as f:
    prompt_triagem = f.read()

agente_triagem = create_agent(model=llm, tools=tools_triagem, system_prompt=prompt_triagem)

prompt_agendamento = """Você é o agente de Agendamento da Care Plus. 
Sua única função é usar a ferramenta para agendar teleconsultas. Confirme sempre a data, hora e especialidade com o paciente antes de finalizar."""
agente_agendamento = create_agent(model=llm, tools=tools_agendamento, system_prompt=prompt_agendamento)

import re

def node_triagem(state: MessagesState):
    print("\n[SUPERVISOR] -> Direcionando para o Agente de Triagem")
    resultado = agente_triagem.invoke(state)
    
    # Pega o texto cru gerado pelo Llama
    texto_resposta = resultado["messages"][-1].content
    
    # 1. LIMPEZA DE JSON VAZADO
    # Essa Regex procura e apaga qualquer coisa parecida com {"name": "tool", "parameters": {...}}
    texto_limpo = re.sub(r'\{.*"name":.*"parameters":.*\}', '', texto_resposta, flags=re.DOTALL)
    
    # 2. INTERCEPTAÇÃO DE RED FLAG DE SAÚDE MENTAL
    # Se o modelo nativo bloqueou a resposta ou tentou chamar tool de suicídio, a gente força a nossa resposta.
    if any(palavra in state["messages"][-1].content.lower() for palavra in ["matar", "suicídio", "morrer"]):
         texto_limpo = "Entendo que você está passando por um momento extremamente difícil. Sua segurança é prioridade. Procure ajuda profissional imediatamente e ligue para o CVV pelo telefone 188 (24h). Se estiver em risco imediato, procure a emergência mais próxima."
    
    # 3. INTERCEPTAÇÃO DE REFUSAL NATIVO SOBRE EMERGÊNCIA
    elif "não posso fornecer ajuda ou informações que possam causar dano" in texto_limpo.lower():
        texto_limpo = "Detectamos sinais de alerta crítico. Recomendo avaliação médica imediata no pronto-socorro."

    # Remove quebras de linha em branco extras que a regex pode ter deixado
    texto_limpo = texto_limpo.strip()

    # Sobrescreve a mensagem final com a versão limpa e blindada
    resultado["messages"][-1].content = texto_limpo

    return {"messages": resultado["messages"][-1:]}

def node_agendamento(state: MessagesState):
    print("\n[SUPERVISOR] -> Direcionando para o Agente de Agendamento")
    resultado = agente_agendamento.invoke(state)
    return {"messages": resultado["messages"][-1:]}

supervisor_llm = ChatOllama(model="llama3.2", temperature=0, format="json")

def roteador_supervisor(state: MessagesState) -> str:
    ultima_msg = state["messages"][-1].content
    
    prompt = f"""
    Analise a intenção da mensagem do paciente: "{ultima_msg}"
    
    Se o usuário quiser marcar uma consulta, data ou horário: retorne APENAS {{"destino": "agendamento"}}
    Se o usuário relatar sintomas, quiser saber histórico, receitas ou tiver dúvidas médicas: retorne APENAS {{"destino": "triagem"}}
    """
    
    try:
        resposta = supervisor_llm.invoke([HumanMessage(content=prompt)])
        destino = json.loads(resposta.content).get("destino", "triagem")
        return destino if destino in ["triagem", "agendamento"] else "triagem"
    except Exception:
        return "triagem" 

builder = StateGraph(MessagesState)

builder.add_node("triagem", node_triagem)
builder.add_node("agendamento", node_agendamento)

builder.add_conditional_edges(START, roteador_supervisor)

builder.add_edge("triagem", END)
builder.add_edge("agendamento", END)

app = builder.compile()