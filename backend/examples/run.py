#ARCHIVO DONDE IMPORTO EL AGENTE DE IA CREADO CON Pydantic_ai Y LO UTILIZO PARA RESPONDER A LAS CONSULTAS DEL USUARIO, ADEMÁS DE MOSTRAR EL HISTORIAL DE MENSAJES EN LA INTERFAZ DE USUARIO HECHA CON STREAMLIT

import streamlit as st #libreria para hacer prototipos UI de forma rapida
from agents import ivan_torres, IvanTorresOutput #importamos el agente de IA creado con pydantic_ai
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    FinalResultEvent,
    
    
    ) 
from pydantic_ai.result import StreamedRunResultSync
from pydantic_ai.agent import AgentRunResult

import logfire

logfire.configure() #configuramos logfire para mostrar logs de depuración


def mostrar_mensajes():
    for message in st.session_state.message_history:
        parts = message.parts
        if isinstance(message, ModelRequest):
                for part in parts:
                    if isinstance(part, UserPromptPart):
                        with st.chat_message("user"):
                            st.write(part.content)
                        
        elif isinstance(message, ModelResponse):
            for part in parts:
                    if part.tool_name == "final_result":
                        with st.chat_message("assistant"):
                            st.write(part.args['title'])
                            st.write(part.args['description'])
                            st.write(f"_Herramientas utilizadas: {', '.join(part.args['tools'])}_")
                            
def event_handler(event):
    pass

if "message_history" not in st.session_state:
    st.session_state.message_history = []

def main():
    st.title("Ivan Torres - Weather Asistant")

    consulta = st.chat_input("Escribe tu consulta aquí", value="", key="consulta")
    placeholder = st.empty() #creamos un placeholder para mostrar la respuesta del agente de IA de forma dinámica mientras se va generando, es decir, a medida que el agente va generando la respuesta, se va actualizando el contenido del placeholder con el texto acumulado hasta ese momento. Esto permite mostrar la respuesta de forma progresiva en lugar de esperar a que se genere toda la respuesta para mostrarla de una vez.
    if consulta:
        texto_acumulado = ""
        with st.spinner("Generando consulta..."):    
                     
             respuesta = ivan_torres.run_stream_sync(consulta, message_history=st.session_state.message_history)
            #  st.write(respuesta.all_messages())
             
             for event in respuesta.stream_text(delta=True): 
                    # st.write(event)
                    texto_acumulado += event
                    placeholder.markdown(texto_acumulado)
                    
             st.session_state.message_history = respuesta.all_messages()
            #  mostrar_mensajes()
        # st.write(respuesta.all_messages())
      
        
        
if __name__ == "__main__":
    main()