import json
import sys
from pathlib import Path
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

BASE_DIR = Path(__file__).parent.parent
print("[Evals] Caminho BASE:", BASE_DIR)
sys.path.append(str(BASE_DIR))

from src.graph.workflow import app 

judge_llm = ChatOllama(model="llama3.1", temperature=0, format="json")

def load_eval_set():
    caminho_entrada = BASE_DIR / "evals" / "sprint1_eval_set.json"
    with open(caminho_entrada, "r", encoding="utf-8") as f:
        return json.load(f)

def avaliar_resposta(pergunta, resposta_agente, esperado, criterios):
    prompt = f"""
    Você é um avaliador técnico.
    Entrada do usuário: {pergunta}
    Resposta ideal: {esperado}
    Critérios: {criterios}
    Resposta do Agente: {resposta_agente}
    
    Avalie a resposta do agente com base nos critérios. Retorne APENAS um JSON válido neste formato exato:
    {{"avaliacao": "adequada" ou "parcial" ou "inadequada", "score": <nota de 0 a 10>}}
    """
    resultado = judge_llm.invoke([HumanMessage(content=prompt)])
    try:
        return json.loads(resultado.content)
    except Exception as e:
        print(f"Erro no JSON: {e}")
        return {"avaliacao": "erro", "score": 0}

def rodar_evals():
    eval_set = load_eval_set()
    resultados = []

    print(f"Iniciando avaliação de {len(eval_set)} casos com Llama 3.1...\n")

    for index, caso in enumerate(eval_set):
        id_caso = caso.get("id", f"eval_{index}")
        categoria = caso.get("categoria", "")
        pergunta = caso.get("entrada_usuario", "")
        esperado = caso.get("resposta_ideal", "")
        criterios = caso.get("criterios_avaliacao", "")
        
        print(f"Testando [{index+1}/{len(eval_set)}]: {id_caso} | {categoria}")
        
        inputs = {"messages": [("user", pergunta)]}
        estado_final = app.invoke(inputs, {"configurable": {"thread_id": id_caso}})
        mensagens = estado_final["messages"]
        
        resposta_final = mensagens[-1].content
        
        tools_chamadas = []
        documentos = []
        trajetoria = []

        for msg in mensagens:
            trajetoria.append(msg.type)
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    tools_chamadas.append(tc["name"])
            if isinstance(msg, ToolMessage) and msg.name == "buscar_diretrizes_careplus":
                documentos.append(msg.content)

        nota = avaliar_resposta(pergunta, resposta_final, esperado, criterios)

        resultados.append({
            "id": id_caso,
            "categoria": categoria,
            "entrada_usuario": pergunta,
            "resposta_obtida": resposta_final,
            "trajetoria": trajetoria,
            "tools_chamadas": list(set(tools_chamadas)),
            "documentos_recuperados": documentos,
            "avaliacao_qualitativa": nota.get("avaliacao"),
            "score": nota.get("score")
        })

    caminho_saida = BASE_DIR / "evals" / "sprint2_results.json"
    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultados salvos em: {caminho_saida}")

if __name__ == "__main__":
    rodar_evals()