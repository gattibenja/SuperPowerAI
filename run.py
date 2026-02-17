import streamlit as st #libreria para hacer prototipos UI de forma rapida
from src.agent_loop import llamar_agente #importamos la función que llama al agente de IA
from langchain_core.messages import HumanMessage, AIMessage


def mostrar_mensajes():
    for message in st.session_state.message_history:
        if isinstance(message, HumanMessage):
            with st.chat_message("user"):
                st.write(message.content)
        elif isinstance(message, AIMessage):
            with st.chat_message("assistant"):
                st.write(message.content)

if "message_history" not in st.session_state:
    st.session_state.message_history = []

def main():
    st.title("Sol Perez - Weather Asistant")

    consulta = st.text_input("Escribe tu consulta aquí", value="", key="consulta")

    if consulta:
        st.session_state.message_history.append(HumanMessage(content=consulta))

        with st.spinner("Generando consulta..."):
         respuesta = llamar_agente(consulta, message_history=st.session_state.message_history) 
         print("Respuesta del agente:", respuesta)
         data = respuesta["messages"][-1]
         content = data.content
         if isinstance(content, list):
            text = content[0]["text"]
         else:
            text = content
        
        st.session_state.message_history.append(AIMessage(content= text))
        
        mostrar_mensajes()
        
if __name__ == "__main__":
    main()