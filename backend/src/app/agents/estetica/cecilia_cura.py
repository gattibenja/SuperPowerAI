#ARCHIVO DONDE CONFIGURO EL AGENTE DE IA CON Pydantic_ai, DEFINO LAS HERRAMIENTAS QUE VA A UTILIZAR Y EL PROMPT DEL SISTEMA

from pydantic_ai import format_as_xml, Agent
from dotenv import load_dotenv

from app.agents.estetica.prompts import prompt  
from .tools import pacienteTools

load_dotenv()


cecilia_cura = Agent("google-gla:gemini-2.5-flash",
                    toolsets=[pacienteTools],
)
cecilia_cura.instrument_all() #instrument_all() es un método que se encarga de registrar todas las funciones decoradas con @cecilia_cura.tool_plain como herramientas disponibles para el agente, es decir, las funciones que el agente puede llamar durante su ejecución para obtener información o realizar acciones específicas.

@cecilia_cura.system_prompt
def system_prompt():
    return format_as_xml(prompt)