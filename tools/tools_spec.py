from langchain_core.tools import tool

@tool
def buscar_dados_wearable(patient_id: str) -> str:
    """Busca os últimos dados vitais sincronizados do smartwatch (Apple Health/Google Fit) do paciente. Exemplo de patient_id: 9988"""
    print(f"\n[TOOL EXECUTED: Fetching wearable data for patient ID {patient_id}...]")
    return f"Dados do Wearable para {patient_id}: Frequência Cardíaca em repouso 110 bpm. SpO2: 98%."

@tool
def buscar_historico_paciente(patient_id: str) -> str:
    """Busca o histórico médico e receitas de uso contínuo do paciente."""
    print(f"\n[TOOL EXECUTED: Accessing medical records for patient ID {patient_id}...]")
    return f"Prontuário de {patient_id}. Medicações contínuas: Losartana 50mg. Alergias: Nenhuma."

tools = [buscar_dados_wearable, buscar_historico_paciente]