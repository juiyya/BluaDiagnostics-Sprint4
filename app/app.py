import sys
import streamlit as st
from pathlib import Path
from langchain_core.messages import HumanMessage, AIMessage

BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR))

from src.graph.workflow import app

st.set_page_config(page_title="Assistente Care Plus", page_icon="🏥", layout="centered")

st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatInputContainer { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🏥 Unidade de Triagem")
    st.info("Pré-análise com IA. Em caso de emergência, ligue 192.")
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()

st.title("Assistente Virtual Care Plus")
st.caption("Tecnologia e Saúde conectadas para o seu bem-estar.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    role = "user" if isinstance(message, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(message.content)

if prompt := st.chat_input("Como posso ajudar hoje?"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            try:
                inputs = {"messages": st.session_state.messages}
                config = {"configurable": {"thread_id": "user_session_1"}} 
                
                result = app.invoke(inputs, config)
                resposta = result["messages"][-1].content
                
                st.markdown(resposta)
                st.session_state.messages.append(AIMessage(content=resposta))
                
            except Exception as e:
                st.error(f"Erro na orquestração: {str(e)}")