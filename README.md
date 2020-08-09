# Tarea 03: DCCuatro <img src="cliente/sprites/Logo_1.png" height="10%" width="10%">

## Consideraciones generales :warning:
* Se establece un tamaño fijo para cada ventana, el cual es optimo para una pantalla de 1920x1080. 

* Un mensaje enviado por el servidor tiene un id de 4 bytes que da a conocer si es en formato json (id = 0) o bytearray (id = 1). En el caso de ser json, los proximos 4 bytes dan a conocer su longitud. En el caso de los bytearrays, los proximos 4 bytes son el tipo de informacion que se esta mandando (1 = color, 2 = tipo carta, 3 = imagen carta, 4 = imagen reverso).

* Cuando un jugador grita, el perdedor de esa acción puede sacar las cartas cuando el desee (en los turnos de otros jugadores o en el suyo) y el juego continua. Pero el jugador en cuestión no podrá jugar una carta hasta que saque todas las cartas que debe. Si las saca en su turno podrá jugar una carta igualmente, para asi no generar cambios en si las saca en otro turno o en el suyo. Se hizo un parametro para la cantidad de cartas que se saca (4 por default) pero en el texto de la interfaz no esta como parametro, así si se cambia, las reglas del juego cambian pero no se va a postrar graficamente en texto
 
* 2 usuarios pueden tener el mismo nombre intercambiando mayusculas, ya que no se indicaba lo contrario en el enunciado

* En las cartas el borde derecho no manda la señal ya que estan superpuestas, pero es una minima parte de la carta

* Cada persona tiene una vista de la mesa como si se ubicara en una parte de ella. 

* En la prueba del programa no se encontraron caídas de este mismo. 

### Cosas implementadas y no implementadas :heavy_check_mark: :x:

* **Networking**:
    * **Protocolo**: Hecho completo.
    * **Sockets**: Hecho completo.
    * **Conexión**: Hecho completo.
    * **Manejo de clientes**: Hecho completo.
* **Aqruitectura Cliente-Servidor**:
    * **Roles**: Hecho completo.
    * **Consistencia**: Hecho completo
    * **Logs**: Hecho completo.
* **Manejo de Bytes**:
    * **Codificación Cartas**: Hecho completo.
    * **Decodificación Cartas**: Hecho completo.
    * **Integración**: Hecho completo.
* **Interfaz gráfica**:
    * **Modelación**: Hecho completo.
    * **General**: Hecho completo.
    * **Ventana de Incicio**: Hecho completo.
    * **Sala de espera**: Hecho completo.
    * **Sala de Juego**: Hecho completo.
    * **Fin de la Partida**: Hecho completo.
* **Reglas del DCCuatro**:
    * **Repartir cartas**: Hecho completo.
    * **Jugar una carta**: Hecho completo.
    * **Robar una carta**: Hecho completo.
    * **Gritar ¡DCCuatro!**: Hecho completo.
    * **Termino del Juego**: Hecho completo.
* **General**:
    * **Parametros**: Hecho completo.
    * **Generador de mazos**: Hecho completo.
* **Bonus**:
    * **Tiempo límite**: No hecho.
    * **Anonymus**: No hecho.
    * **Relámpago**: No hecho.
    * **Selector de mazos**: No hecho.
    * **Forever alone**: No hecho. 
    * **Chat**: No hecho.  
   
   


## Ejecución :rewind: :arrow_forward: :fast_forward:
El módulo principal de la tarea a ejecutar es  ```main.py``` en ```clientes``` y ```server.py``` en ```server.py``` en ```servidor```. Además se deben tener los siguentes archivos:
1. Carpeta ```sprites```, tal cual fue enviada, en ```servidor```.
2. ```my_sprites``` en ```servidor```.
3. ```generador_de_mazos.py``` en ```servidor```.
4. ```game_window.ui``` en ```cliente```.
5. ```summary.ui``` en ```cliente```.
6. ```sprites``` en ```cliente```.


## Librerías :books:
### Librerías externas utilizadas :closed_book:
Pese a que hay más modulos importados, ya que fueron probados en la creación del código, pero no utilizados finalmente. Pese a esto no afectan en la ejecución del programa. La lista de librerías externas que utilicé finalmente fueron las siguientes:

1. ```socket```: ```close()```, ```socket()```, ```connect()```
2. ```threading```: ```Thread()```, ```Lock()``` .
3. ```sys``` : ```exit()```.
4. ```PyQt5``` : ```uic```.
5. ```PyQt5.QtWidgets``` : ```QLabel```, ```QWidget```, ```QPushButton```, ```QHBoxLayout```, ```QVBoxLayout```, ```QDialog```, ```QSizePolicy```, ```QApplication```
6. ```PyQt5.QtCore``` : ```QThread```, ```QObject```, ```pyqtSignal```, ```Qt```, ```QCoreApplication```, ```QObject```
7. ```PyQt5.QtGui``` : ```QPixmap```, ```QFont```.
8. ```json```: ```send()```, ```sendall()```, ```load()```, ```dump()```,
9. ```math```: ```floor()```.
10. ```base64```: ```encode()```, ```decode()```
11. ```collections```: ```defaultdict```.
12. ```os```: ```path.join()```.
13. ```copy```: ```deepcopy()```.
14. ```random```: ```choice()```.

### Librerías propias :notebook:
Por otro lado, los módulos que fueron creados fueron los siguientes:

* **Sevidor**:

1. ```parametros.json```: Contiene a todos los parámetros utilizados en el código de la carpeta servidor

2. ```server.py```: Es donde corre el servidor (la clase). Al principio tiene el manejo de conexiones. Despues el manejo de comunicación que requiere estar dentro de la clase y después el manejo del juego

3. ```logs.py```: Tiene una función que crea los logs, principalmente según el id que le llega de la acción

4. ```communication_tools.py```: tiene las funciones para preparar las imagenes para mandarlas y la de mandar json.

* **Cliente**:

1. ```client.py```: Es el back-end de cada cliente y es el encargado de la comunicación con el servidor. 

2. ```game_window.py```: Contiene a todo lo que involucre graficamente al juego (la ventana de juego, el pop-up de elección de color y el pop-up cuando alguien entra en modo espectador). 

3. ```login_window.py```: Contiene a la ventana de inicio del juego para logear.

4. ```waiting_room.py```: Contiene la ventana de la sala de espera.

5. ```summary_window.py```: Contiene la ventana del resultado de la partida.

## Supuestos y consideraciones adicionales :memo:
Los supuestos que realicé durante la tarea son los siguientes:

1. Siempre comienza el jugador en la posición 1.

2. El servidor puede tener solo a 8 personas esperando para conectarse, para mantenerlo de baja escala

-------




## Referencias de código externo :link:

Para realizar mi tarea saqué código de:
1. https://stackoverflow.com/questions/33678421/python-tabulate-appending-element-to-current-table: este ordena los logs y está implementado en el archivo ```logs.py```.