from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()
@tool
def get_temperature(city: str, scale: str) -> float:
    """
    Gets the temperature for a given city and scale.

    """
    # llamaría a una API de clima para obtener la temperatura
    return 20.0

@tool
def get_humidity(city: str) -> int:
    """
    Gets the humidity for a given city.

    
    """
    # llamaría a una API de clima para obtener la humedad
    return 50

@tool
def get_wind_speed(city: str) -> float:
    """
    Gets the wind speed for a given city.

    """
    # llamaría a una API de clima para obtener la velocidad del viento
    return 10.0


tools = [
    get_temperature,
    get_humidity,
    get_wind_speed,
]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
agent = create_agent(llm, tools=tools)


def llamar_agente(consulta: str, message_history: list) :
    mensajes = [HumanMessage(content=consulta)] + message_history
    return agent.invoke(
        {"messages": mensajes}        
    )



