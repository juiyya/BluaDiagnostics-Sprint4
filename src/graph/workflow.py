import sys
import json
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END, MessagesState

BASE_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(BASE_DIR))

# Importa as ferramentas que você já criou
from src.tools.tools_spec import (
    buscar_dados_wearable,
    buscar_historico_paciente,
    agendar_teleconsulta,
    buscar_diretrizes_careplus
)

llm = ChatOllama(model="llama3.1", temperature=0)

# --- 1. SEPARANDO AS TOOLS POR ESPECIALIDADE ---
tools_triagem = [buscar_dados_wearable, buscar_historico_paciente, buscar_diretrizes_careplus]
tools_agendamento = [agendar_teleconsulta]

# --- 2. CRIANDO OS SUB-AGENTES ---
prompt_triagem = """Você é o agente de Triagem da Care Plus. 
Responda dúvidas médicas, verifique o histórico do paciente e use as diretrizes. 
Se houver Red Flag (sintomas graves, dores fortes, risco de morte), alerte o paciente para ir ao pronto-socorro imediatamente."""
agente_triagem = create_agent(model=llm, tools=tools_triagem, system_prompt=prompt_triagem)

prompt_agendamento = """Você é o agente de Agendamento da Care Plus. 
Sua única função é usar a ferramenta para agendar teleconsultas. Confirme sempre a data, hora e especialidade."""
agente_agendamento = create_agent(model=llm, tools=tools_agendamento, system_prompt=prompt_agendamento)

# --- 3. CRIANDO OS NÓS DO GRAFO ---
def node_triagem(state: MessagesState):
    print("\n[SUPERVISOR] -> Direcionando para o Agente de Triagem")
    resultado = agente_triagem.invoke(state)
    return {"messages": resultado["messages"][-1:]} # Retorna só a resposta final

def node_agendamento(state: MessagesState):
    print("\n[SUPERVISOR] -> Direcionando para o Agente de Agendamento")
    resultado = agente_agendamento.invoke(state)
    return {"messages": resultado["messages"][-1:]}

# --- 4. FUNÇÃO DO SUPERVISOR (ROTEAMENTO) ---
supervisor_llm = ChatOllama(model="llama3.1", temperature=0, format="json")

def roteador_supervisor(state: MessagesState) -> str:
    ultima_msg = state["messages"][-1].content
    
    # Força o Llama a cuspir um JSON cravado para tomar a decisão
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
        return "triagem" # Se der erro na leitura do JSON, cai na triagem por segurança

# --- 5. MONTANDO A ARQUITETURA MULTI-AGENTE (LangGraph) ---
builder = StateGraph(MessagesState)

# Adiciona os especialistas
builder.add_node("triagem", node_triagem)
builder.add_node("agendamento", node_agendamento)

# O ponto de partida passa pelo supervisor para decidir o caminho
builder.add_conditional_edges(START, roteador_supervisor)

# Depois que o especialista responde, encerra o ciclo
builder.add_edge("triagem", END)
builder.add_edge("agendamento", END)

# Compila o sistema final
app = builder.compile()