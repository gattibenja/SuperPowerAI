import os
from dotenv import load_dotenv
from typing import TypedDict
from pydantic import BaseModel, Field
from google import genai

alumno = {
     "Name": "Benja",
     "Age": 19,
     "Ciudad": "Argentina"  
}

class Memory: 
    def __init__(self):
        self.tasks = []
        self.short = []
        self.long = []
    def add(self, task):
        self.tasks.append(task)
        
def sumar(a, b):
    return a + b

def restar(a, b):
    return a - b

def think_tool(query):
    return f"Searching {query}"

#Self hace referencia a la instancia y
#Cls hace referencia a la class en este caso cls == Alumno al usar cls llamas a Alumno()
# Las funciones de clase sirven para crear una misma instancia pero desde diferentes fuentes de datos
# por ej un dict, una api, string, etc es decir utilizo el agente y una de las funciones 
# por ej quiero crearlo desde un dict(objeto) y voy a crear una funcion de clase que admita objetos y
# los formatee de esa manera

class Alumno: 
    species = "AI"
    def __init__(self, name, age, country, id):  
        # siemprpe llevan el self porque al inicializar la instancia python internamente hace un Alumno.__init__(a, "Benja") 
        # el a vendria a ser el nombre de la variable o instancia
        # por a = Alumno("Benja") a vendria a ser self, hace referencia a la instancia
        self.name = name
        self.age = age
        self.country = country
        self.id = id # sin _ pasa por el setter y se valida el id, el id es el atributo privado y real
        self.memory = Memory()
        self.tools = {
            "sumar": sumar,
            "restar": restar,
            "think": think_tool
        }
    
    @property
    def id(self):
        return self._id # con  _ pasa por el getter y se devuelve el id
    @id.setter
    def id(self, value): # aca se usa el _ porque asi se accede al atributo privado y real desde dentro de la clase
        try:
            if value <= 0:
                raise ValueError("ID must be positive")
            self._id = value
        except ValueError as e:
            print(e)
        
    def run(self, task):
        return f"{self.name} runs {task}" 
    def think(self):
        self.idea = "New Plan"
        temp = "hola"
        
    @classmethod
    def info(cls):
        print(cls.species)
    
    @classmethod
    def from_dict(cls, dict):
        return cls(
            dict["name"],
            dict["age"],
            dict["country"],
            dict["id"]
        )
    @classmethod 
    def from_string(cls, text):
        name, age, country, id = text.split(",")
        return cls(name, int(age), country, int(id))
    
    def __repr__(self): 
        # metodo para hacer debug al hacer el print de la instancia te devuelve
        # los datos que vos quieras simplemente printenado la instancia
        #sirve para debug
        return f"Agente(name={self.name})"
        
    
    # El f es como las comillas invertidas para agregar variables dentro de un string
    
    #Las variables que esten en __init__ se inicializan siempre al crear la instancia
    #Pero las variables que esten en otras funciones no existiran hasta que se llame 
    #Al metodo con la instancia
    #Ademas existen las variables que no estan con self como temp que se mueren 
    #cuando termina la funcion, al contrario de las self que siguen como memoria de la instancia
    
    #El estado se le dice a todas las variables que estan con self que viven entre llamadas

def main():
    
    # tipo de funcion como en C (ANOTACIONES)

 def foo(x: int, y: int) -> str:
    pass
# -----------------------------------------------------------
# FOR IN 

 persona = {
    "name": "Benja",
    "age": 19
 }
 for clave, valor in persona.items():
    print(clave, valor)
    

# list comprehension
# Se haria asi 
 numeros = [2, 4, 6]
 cuadrados = []

 for n in numeros:
    cuadrados.append(n * n)
    
# pero se puede hacer asi con list comprehension:
 cuadrados = [n * n for n in numeros]
 
# Dict comprehension 

 prueba = {x:x*2 for x in range(20)}
 
 for clave, value in prueba.items():
     print(f"Dict Comprehension - clave: {clave}, valor: {value}")
     
 print(f"Esta es la: {prueba}")

# -----------------------------------------------------------
# LISTA Y GENERADOR -> BASICAMENTE LOS GENERADORES NO OCUPAN CASI MEMORIA Y SE USAN PARA MUCHO FLUJO DE DATOS 


# LISTA TIENE TODO EL TIEMPO TODA LA LISTA GUARDADA EN MEMORIA Y LISTA PARA SER USADA MENOS EFICIENTE
 numeros = [n*n for n in range(5)]

# GENERADOR TE GENERA EL NUMERO RECIEN CUANDO USAS LA LISTA O CADA VEZ QUE LA USAS Y NO GUARDA EN MEMORIA OSEA SE TERMINA DE USAR Y QUEDA VACIO
# para usar el generador lo normal es iterarlo con un for algo asi el te genera valores vos los iteras: 
#  Generator Comprehension

 generator = (n * n for n in range(10)) 
 
 for x in generator: 
     print(f"Generador de numeros: {x}")
 

# EJEMPLO REALISTA DE GENERADOR CON YIELD PARA ARCHIVOS ENORMES 
# El archivo se abre en cada iteracion se lee la primera linea con yield queda en pausa la funcion, y

 def leer_archivo():
    # Obtener la ruta del directorio donde está este archivo
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    print(directorio_actual)
    ruta_logs = os.path.join(directorio_actual, 'logs.txt')
    with open(ruta_logs, "r") as f:
        for linea in f:
            yield linea # El yield hace que la funcion se pause y que no guarda 3 millones de linea, solo la de la primera iteracion y al llamarla luego pasa a la siguiente eliminando la anterior
 
 lista = range(20)
 
 for linea in leer_archivo():
    print(linea)
    
 # Generador con condicion IMPORTANTISIMO 
 
 resultado = (
    n * 2 # lo que devuelve si se cumple la condicion
    for n in lista # iteracion 
    if n % 3 == 0 # condicion 
)
 
 for n in resultado:
     print(f"Generador con condicion: {n}")
    
    
# IMPORTANTISIMO AL USAR UN GENERADOR NADA LO VUELVE AL INICIO O LO RESETEA POR LO QUE NO SE PUEDE USAR MAS DEBIDO A QUE YA ESTA EN EL FINAL 

# -----------------------------------------------------------
# LAMDAS -> Funciones cortitas 

#Funcion normal 

 def cuadrado(x):
    return x * x

#Funcion Lambda 

 cuadrado = lambda x: x * x

# -----------------------------------------------------------
# Se usan muy poco Metodos de listas -> map(funcion, lista), filter(condicion, lista), sort.... -> map transforma y filter selecciona

 numeros = [1, 2, 3, 4]

 resultado = map(lambda x: x * 2, range(10)) 
 
 for n in resultado:
     print(n)
     print("Uso de lamba con generadores")
     
# Ej uso de map con filter para un generador y lambda, las lambda suelen ir dentro de los metodos de lista 

# Clasico mucho codigo

 numbers = range(21)

 generator = map(lambda x: x*2, filter(lambda x: x % 2 == 0, numbers))

 for n in generator:
     print(f"Generador de map y filter para pares clasico: {n}")
     
# Moderno poco codigo
 
 generator = (n*2 for n in range(21) if n % 2 == 0)
 
 for n in generator:
    print(f"Generador de map y filter para pares moderno: {n}")

     
# -----------------------------------------------------------

# Pipelines -> procesos donde salida de uno es la entrada del otro

# Clasico y lento  

 numeros = [1, 2, 3, 4, 5]

 dobles = []
 for n in numeros:
    dobles.append(n * 2)

 pares = []
 for n in dobles:
    if n % 2 == 0:
        pares.append(n)

 print(pares)

 
 #Moderno y Rapido

 resultado = filter(
    lambda x: x % 2 == 0,
    map(lambda x: x * 2, numeros)
)

 for n in resultado:
    print(n)




# -----------------------------------------------------------



    
 data = {
    "name": "Agostina",
    "age": 22,
    "country": "Argentina",
    "id": 10
 }

 alumno = Alumno("Benja", 19, "Argentina", 10) #Creo un alumno desde la propia clase
 alumno2 = Alumno.from_dict(data) #creo un alumno desde un dict/objeto
 alumno3 = Alumno.from_string("Pablo,50,Argentina,10")
 
 print(alumno.name)
 print(alumno._id)
 #print(alumno2.id)
 #alumno.id = -20
 #print(alumno.id)
 #print(alumno)
 #print(alumno2.name)
 #print(alumno3.name)

if __name__ == "__main__": 
    main()
    # Cada archivo en python tiene la variable __name__ y esa variable tiene el valor __main__ para cada  archivo
    # pero si a tal archivo lo importamos desde otro archivo esa variable sera solo el nombre del archivo entonces 
    # se usa este bloqueo para que no se ejecute codigo si lo importamos desde otro lado
    # si quisieramos que se ejecutara cierto codigo al importarlo deberiamos hacer:
    # if __name__ == "nombre_archivo":
    #       codigo a Ejecutar

    