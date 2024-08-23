# Informe del Laboratorio 2

### Integrantes (Grupo 31)

* germanjohn13@outlook.es (Germán John)

### Estructura del Servidor

* En el archivo *server.py* se encuentra la implementación del servidor.
* En el archivo *connection.py* se encuentra la implementación del manejador de conexiones del cliente.
* En el archivo *constants.py* se encuentran las constantes a utilizar (dado por la cátedra y algunas cosas añadidas).
* En el archivo *cliente.py* se encuentra la implementación del cliente HFTP (dado por la cátedra).
* En el archivo *server-test.py* se encuentra un conjunto de tests, que pueden ser divididos en pruebas unitarias (dado por la cátedra).

### Decisiones de Diseño

Algunas decisiones tomadas durante la implementación.

##### server.py

* Se delegan acciones específicas a un objeto que abstrae la conexión.
* El control de nuevas de conexiones se implementa con hilos.
* Se normaliza la ruta del directorio a servir para que una vez que se pase a un objeto de menor nivel, que trate la conexión, ese objeto de menor nivel pueda realizar acciones con respecto a la ruta normalizada y los contenidos del directorio, y para que no se intenten manipular los comandos.

##### connection.py

* Se asegura que sólo los archivos listados y consultados sean los que estén bajo el directorio que se está sirviendo.
* Cada método está modularizado incluso en los chequeos de errores. Esto implica que es posible que devuelvan una respuesta que esté asociada a algún error.
* *handle* chequea la validez en cuanto al número de argumentos dados, y quizás si son válidos los casteos.
* Observar que hay un modelo alternativo respecto a los dos puntos anteriores, que consiste en modularizar aún más los métodos y construir funciones auxiliares que hagan los chequeos. Además el tratamiento de errores podría haberse intentado agregando más excepciones (pero no es buena practica usar excepciones para controlar el flujo de ejecución).
* *handle* podría ser mejorado usando nuevas características de Python, pero se prefiere ir a la vieja usansa por interoperabilidad entre versiones.
* Se toma en cuenta si el comando el input dado se puede clasificar como *fatal*, dentro del método que prepara una respuesta ante un error posible.

### Dificultades encontradas

* Al principio fue complicado leer bien el código.
* Se intenta hacer un código prolijo.
* Se intenta respetar la orientación a objetos.
* Darse una idea de los errores ante algún evento en el (posible) flujo de ejecución.

### Preguntas

1. ¿Qué estrategias existen para poder implementar este mismo servidor pero con
capacidad de atender múltiples clientes simultáneamente? Investigue y responda
brevemente qué cambios serían necesario en el diseño del código.

* La estrategia mas obvia es utilizar la libreria _threading_ para que el servidor maneje cada conexion paralelamente en su propio thread, segun lo dicte el interprete de Python. Para implementarlo hay que definir la funcion serve de server.py para que acepte la conexion y cree el thread con los parametros de la conexion para que ejecute el handler.
* Otra posibilidad es usar forking para que se cree un proceso hijo para cada cliente y sea atendido. De forma similar a la anterior hay que crear el fork en el serve para que ejecute el handler para ese cliente.
* Tambien se puede usar la libreria _asyncio_ para crear corutinas que atiendan multiples clientes. Se puede adaptar al esqueleto del laboratorio pero la forma correcta seria reescribir la mayoria del servidor con las implementaciones que tiene esta libreria.

2. Pruebe ejecutar el servidor en una máquina del laboratorio, mientras utiliza el cliente
desde otra, hacia la ip de la máquina servidor. ¿Qué diferencia hay si se corre el
servidor desde la IP “localhost”, “127.0.0.1” o la ip “0.0.0.0”?

Cuando se corre el servidor desde "127.0.0.1" o "localhost" se establece una conexion solo con la misma maquina que esta siendo utilizada por el usuario, por lo que no recibira conexiones de ningun cliente que se intente conectar desde otra maquina o computadora. Si se corre el servidor en "localhost" o "127.0.0.1" y se intenta conectar al servidor desde otra maquina con la IP del host y el puerto correspondiente al servidor, obtendremos un error de conexion ya que no encontrara a que conectarse.
Cuando se corre el servidor desde la ip "0.0.0.0", significa que se abre en todas las direcciones IPv4, y, por ejemplo, si un host tiene dos direcciones IP, 192.168.1.1 y 172.18.0.124, cuando el servidor escucha en "0.0.0.0" podra ser alcanzado en ambas IPs por maquinas externas. Por lo tanto si se corre el servidor en "0.0.0.0" y se intenta conectar desde otra maquina en, por ejemplo, la IP del host 172.18.0.124 en el puerto correspondiente, deberia iniciar la conexion con el servidor.
