import streamlit as st
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message="Accessing `__path__` from*")
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

# Ajuste de path para enxergar a 'src'
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

# Importação Lazy para evitar conflitos de inicialização
from src.graph.workflow import app

# Configuração da página (deve ser a primeira linha Streamlit)
st.set_page_config(page_title="Care Plus AI", page_icon="🏥", layout="centered")

# CSS para deixar o chat com cara de app moderno
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 Assistente Virtual Care Plus")
st.caption("Tecnologia e Saúde conectadas para o seu bem-estar.")

# Inicializa o histórico na sessão se não existir
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message("user" if isinstance(message, HumanMessage) else "assistant"):
        st.markdown(message.content)

# Input do usuário
if prompt := st.chat_input("Como posso ajudar hoje?"):
    # Adiciona e exibe mensagem do usuário
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user"):
        st.markdown(prompt)

    # Gera a resposta do Agente
    with st.chat_message("assistant"):
        with st.spinner("Analisando dados clínicos..."):
            try:
                # Prepara o input para o LangGraph
                inputs = {"messages": st.session_state.messages}
                config = {"configurable": {"thread_id": "user_session_1"}} # ID fixo para teste
                
                # Chama o grafo de forma síncrona (Streamlit lida bem com isso)
                result = app.invoke(inputs, config)
                
                resposta = result["messages"][-1].content
                st.markdown(resposta)
                
                # Salva a resposta no histórico
                st.session_state.messages.append(AIMessage(content=resposta))
            except Exception as e:
                st.error(f"Erro na orquestração: {str(e)}")