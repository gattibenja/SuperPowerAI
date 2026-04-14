import os
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import  (FunctionDeclaration, Tool, GenerateContentConfig, Part, Content, GenerateContentResponse)
import time
from pydantic_ai import format_as_xml
from src.my_api.agents.prompts import prompt
import json

from schemas.paciente import Paciente

load_dotenv()

API_KEY = os.getenv("API_KEY")

client = Client(api_key=API_KEY) # se crea el cliente de la api


def get_patient_params(args: dict):
  
    nombre = args.get("Nombre")
    apellido = args.get("Apellido")
    enfermedades = args.get("Enfermedades")
    alergias = args.get("Alergias")
    
    # print(f"Nombre: {nombre}")
    # print(f"Apellido: {apellido}")
    # print(f"Enfermedades: {enfermedades}")
    # print(f"Alergias: {alergias}")
    
    return nombre, apellido, enfermedades, alergias

def create_patient(params: tuple):
    nombre, apellido, enfermedades, alergias = params
    paciente = Paciente(
        Nombre=nombre,
        Apellido=apellido,
        Enfermedades=enfermedades,
        Alergias=alergias
    )
    return paciente

def get_temperature(city: str, scale: str) -> float:
    """
    Gets the temperature for a given city and scale.

    Args:
        city (str): The name of the city to get the temperature for.
        scale (str): The temperature scale to use ('Celsius', 'Fahrenheit', etc).

    Returns:
        float: The temperature in the requested scale.
    """
    # llamaría a una API de clima para obtener la temperatura
    return 20.0


def get_humidity(city: str) -> int:
    """
    Gets the humidity for a given city.

    Args:
        city (str): The name of the city to get the humidity for.

    Returns:
        int: The humidity in %.
    """
    # llamaría a una API de clima para obtener la humedad
    return 50


def get_wind_speed(city: str) -> float:
    """
    Gets the wind speed for a given city.

    Args:
        city (str): The name of the city to get the wind speed for.

    Returns:
        float: The wind speed in km/h.
    """
    # llamaría a una API de clima para obtener la velocidad del viento
    return 10.0


# Esto es un ejemplo de como se podria estructurar la función para tool calling, pero no es necesario para el funcionamiento del código, ya que se puede enviar la función directamente en el config de generate_content. De hecho, es mas sencillo y directo enviar la función directamente en el config, ya que no es necesario crear una estructura adicional para la función.
# create_patient_function = { #Estructura para tool calling 
#         "name": "create_patient",
#         "description": "Crea un paciente medico con datos reales que inventes",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "Nombre": {
#                     "type": "string",
#                     "description": "El nombre del paciente a crear"
#                 },
#                 "Apellido": {
#                     "type": "string",
#                     "description": "El apellido del paciente a crear"
#                 },
#                 "Enfermedades": {
#                     "type": "array",
#                     "description": "Enfermedades del paciente a crear",
#                     "items":{
#                         "type": "string"
#                     }
#                 },
#                 "Alergias": {
#                     "type": "array",
#                     "description": "Alergias del paciente a crear",
#                     "items": {
#                         "type": "string"
#                     }
#                 },
#             },
#             "required": ["Nombre", "Apellido", "Enfermedades", "Alergias"]
#         }
#     }
tools = [
    Tool(function_declarations=[FunctionDeclaration.from_callable(client=client, callable=get_temperature)]),
    Tool(function_declarations=[FunctionDeclaration.from_callable(client=client, callable=get_humidity)]),
    Tool(function_declarations=[FunctionDeclaration.from_callable(client=client, callable=get_wind_speed)]),
]

# Función para procesar la respuesta de la función llamada por el modelo, esta función se encarga de extraer el contenido de la respuesta de la función y devolverlo en un formato que se pueda enviar al modelo para que lo utilice en su respuesta final. En este caso, se extrae el resultado de la función y se crea un nuevo Part con el contenido de la respuesta de la función, que luego se añade a una lista de contenidos que se devuelve al final.
def tool_processing(response: GenerateContentResponse) -> list[Part]:
    function_response_parts = []
    for part in response.candidates[0].content.parts:
        if part.function_call:
            print("intentó ejecutar", part.function_call.name)
            print("con los parametros:", part.function_call.args)
            result = None

            if part.function_call.name == "get_temperature":
                city = part.function_call.args["city"]
                scale = part.function_call.args["scale"]
                result = get_temperature(city, scale)

            if part.function_call.name == "get_humidity":
                city = part.function_call.args["city"]
                result = get_humidity(city)

            if part.function_call.name == "get_wind_speed":
                city = part.function_call.args["city"]
                result = get_wind_speed(city)

            # El contenido de la respuesta de la función tipo Part que es el resultado de la función
            function_response_part = Part.from_function_response(
                name=part.function_call.name,
                response={"result": result},
            )
            # Añadimos el contenido de la respuesta de la función a la lista de contenidos
            function_response_parts.append(function_response_part)

        else:
            print(part.text)
    return function_response_parts
    
def main(): 
    try:
        print("Cliente de la api creado correctamente")
        
        #Configuracion para generar contenido con tool calling, se envia el prompt del sistema y la función a llamar en caso de que el user prompt lo requiera. En este caso, se envia la función create_patient, que es la función que se va a llamar cuando el user prompt pida crear un paciente medico con datos reales que inventes.
        config = GenerateContentConfig(
            system_instruction=format_as_xml(prompt),
            temperature=0.6,
            tools=tools  
        )
        
        user_content = Content(
            role="user",
            parts=[Part(text="Cuantos grados hacen en cordoba Argentina")]) # User Prompt
        
        #Envio la tool con el user propmt
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_content, # User Prompt
            config=config  
        )
        print("Respuesta del modelo con tool calling:", response)
        
    #     #Procesamos la respuesta de la función llamada por el modelo
    #     function_response_parts = tool_processing(response)
        
        
    #     # Agregamos el contenido de la respuesta de la función a la lista de contenidos tipo Content que es el mensaje completo con role y parts
    #     contents = [
    #         user_content,
    #         Content(role="model", parts=response.candidates[0].content.parts),
    #         Content(role="user", parts=function_response_parts),
    #   ]
        
    #     #Enviamos de vuelta al chat la request con el contenido de la respuesta de la función para que el modelo pueda utilizarlo en su respuesta final
    #     response2 = client.models.generate_content(
    #         model="gemini-2.5-flash",
    #         contents=contents, # Enviamos el contenido de la respuesta de la función al modelo para que lo utilice en su respuesta final
    #         config=config  
    #     )
        
    #     function_response_parts2 = tool_processing(response2)
        
    #     contents = [
    #         user_content,
    #         Content(role="model", parts=response.candidates[0].content.parts),
    #         Content(role="user", parts=function_response_parts),
    #         Content(role="model", parts=response2.candidates[0].content.parts),
    #         Content(role="user", parts=function_response_parts2),
    #   ]
        
      
    except Exception as e:
        print(f"Error al crear el cliente de la api: {e}")
        print("Rate limit... esperando")
        time.sleep(10)
    
    
    
if __name__ == "__main__":
    main()

    