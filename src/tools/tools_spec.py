import json
import os
from langchain_core.tools import tool

from src.rag.chroma_setup import obter_retriever

retriever = obter_retriever()

#mock
def carregar_banco_pacientes():
    filepath = "./data/pacientes_mock.json"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERRO] Arquivo {filepath} não encontrado.")
        return {}

# tools 
@tool
def buscar_dados_wearable(patient_id: str) -> str:
    """Busca os últimos dados vitais sincronizados do smartwatch (Apple Health/Google Fit) do paciente. Exemplo de patient_id: 9988"""
    print(f"\n[TOOL EXECUTED] Buscando wearable para ID {patient_id}...")
    return f"Dados do Wearable para {patient_id}: Frequência Cardíaca em repouso 110 bpm. SpO2: 98%."

@tool
def buscar_historico_paciente(patient_id: str) -> str:
    """Busca o histórico médico e receitas de uso contínuo do paciente."""
    print(f"\n[TOOL EXECUTED] Acessando prontuário do ID {patient_id}...")
    db = carregar_banco_pacientes()
    p = db.get(patient_id)
    if p:
        return f"Paciente {p['nome']}, {p['idade']} anos, histórico de {p['historico']}, última consulta em {p['ultima_consulta']}, uso contínuo de {p['uso_continuo']}. Alergias: {p['alergias']}."
    return f"Paciente {patient_id} não encontrado no sistema."

@tool
def agendar_teleconsulta(patient_id: str, data: str, horario: str, especialidade: str) -> str:
    """Agenda uma teleconsulta na plataforma da Care Plus. Parâmetros esperados: patient_id, data (DD/MM/AAAA), horario (HH:MM), especialidade."""
    print(f"\n[TOOL EXECUTED] Agendando teleconsulta para {patient_id} em {data} às {horario} ({especialidade})...")
    return f"Sucesso: Teleconsulta de {especialidade} agendada para o paciente {patient_id} no dia {data} às {horario}."

@tool
def buscar_diretrizes_careplus(query: str) -> str:
    """Busca informações na base corporativa: protocolos de triagem, bula, cartilhas, telemedicina e LGPD."""
    print(f"\n[TOOL EXECUTED] Buscando RAG por: '{query}'...")
    if not retriever:
        return "Erro: Base de conhecimento não inicializada."
    
    resultados = retriever.invoke(query)
    if not resultados:
        return "Nenhuma informação relevante encontrada nos documentos."
    
    contexto = "\n\n".join([f"Trecho {i+1}:\n{doc.page_content}" for i, doc in enumerate(resultados)])
    return f"Contextos encontrados:\n{contexto}"

tools = [buscar_dados_wearable, buscar_historico_paciente, agendar_teleconsulta, buscar_diretrizes_careplus]