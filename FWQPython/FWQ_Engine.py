import socket, sys, re, threading, kafka, json, sqlite3
from time import sleep
from kafka import KafkaConsumer
from kafka import KafkaProducer
from json import dumps
import random
import requests
from Crypto.Cipher import AES
import hashlib



def encrypt(msg):
    print(KEY)
    cipher = AES.new(KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode('ascii'))

    return nonce, ciphertext, tag

def decrypt(nonce, ciphertext, tag):
    cipher = AES.new(KEY, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    try:
        cipher.verify(tag)
        return plaintext.decode('ascii')
    except Exception:
        return False

#Para mostrar los errores
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

class attraction:
    def __init__(self, id, posicion, ciclo, capacidad, cola, disponible) -> None:
        self.id = id
        self.posicion = posicion
        self.tiempoDeCiclo = ciclo
        self.capacidad = capacidad
        self.numVisitantesCola = cola
        self.disponible = disponible

    def getId(self):
        return self.id

    def getPosicion(self):
        return self.posicion

    def getCiclo(self):
        return self.tiempoDeCiclo

    def getCapacidad(self):
        return self.capacidad

    def getCola(self):
        return self.numVisitantesCola
    def getDisponible(self):
        return self.disponible

FORMAT = 'utf-8'
FIN = "FIN"    
HEADER = 64
try:
    IP_BROKER = sys.argv[1]
    PUERTO_BROKER = int(sys.argv[2])
    MAX_VISITANTES = int(sys.argv[3])
    IP_WAITING_SERVER = sys.argv[4]
    PUERTO_WAITING_SERVER = int(sys.argv[5])
except IndexError:
    print(bcolors.FAIL +'FWQ_Engine requiere <IP_BROKER> <PUERTO_BROKER> <MAX_VISITANTES> <IP_FWQ_WAITINGTIMESERVER> <PUERTO_FWQ_WAITINGTIMESERVER>' + bcolors.RESET)

except ValueError:
    print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
        
MAPA = ['-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-',
        '-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-','-']

ATRACCIONES = []

def mostrarMapa(mapa):
    n = 20
    cont = 1

    for i in mapa:
        if cont % n == 0 and cont != 0:
            print(i)
            cont += 1
        else:
            print(i, end = " ")
            cont += 1

#Manejar visitante
def producirKafka(data):
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    c.execute("select * from user where inPark = 1")
    usuariosEnMapa = c.fetchall() #MAS ADELANTE NECESITAREMOS PASARLE LOS USUARIOS TAMBIEN.
    try:
        #Creamos un productor para enviar solo un mensaje.
        producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+ str(PUERTO_BROKER),
                            value_serializer=lambda x:dumps(x).encode('utf-8'))
        
        producer.send('Engine', value=data)
    except kafka.errors.NoBrokersAvailable:
        print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)

def usuarioAlMapa(userSql):
    user = {
        'alias': userSql[0],
        'nombre': userSql[1],
        'contraseña': userSql[2],
        'inPark': userSql[3],
        'posicion': userSql[4],
        'ciudad': userSql[6],
    }

    if user['inPark'] == 1:
        MAPA[int(user['posicion'])] = user['alias']
    elif user['inPark'] == 0:
        MAPA[int(user['posicion'])] = '-'
 
def gestionarEntrada(data):
    #Comprobamos que haya espacio en el parque
    print(data)
    alias = data['session']
    global MAX_VISITANTES
    if MAX_VISITANTES > 0:
        connection = sqlite3.connect('user.db')
        c = connection.cursor()
        #Coger aleatoriamente una atracion.
        if ATRACCIONES != []:
            num = random.randint(0,len(ATRACCIONES)-1)
            c.execute(f"update user set destino = '{ATRACCIONES[num].getPosicion()}' where alias = '{alias}'")
        else:
            c.execute(f"update user set destino = -1 where alias = '{alias}'")
        connection.commit()
        c.execute(f"update user set inPark = '1' where alias = '{alias}'")
        connection.commit()
        c.execute(f"select * from user where alias = '{alias}'")
        user = c.fetchone()
        usuarioAlMapa(user)
        MAX_VISITANTES = MAX_VISITANTES - 1
        print(bcolors.WARNING+"Capacidad de usuarios restante en el parque: " + str(MAX_VISITANTES) +bcolors.RESET)
    else:
        producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+ str(PUERTO_BROKER),
                            value_serializer=lambda x:dumps(x).encode('utf-8'))

        data = f"No se ha permitido la entrada a {alias} porque el parque esta lleno. Espere a que alguien salga del parque."
        
        data = encrypt(data)
        print(data)
        sleep(3)
        producer.send('Engine', value=data)
        print(bcolors.WARNING + f"No se ha permitido la entrada a {alias} porque el parque esta lleno. Espere a que alguien salga del parque." + bcolors.RESET)
    
def gestionarSalida(data):
    global MAX_VISITANTES
    MAX_VISITANTES += 1
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    alias = data['session']
    c.execute(f"update user set inPark = '0', destino = '-1' where alias = '{alias}'")
    connection.commit()
    c.execute(f"select * from user where alias = '{alias}'")
    user = c.fetchone()
    usuarioAlMapa(user)
    print(bcolors.WARNING+"Capacidad de usuarios restante en el parque: " + str(MAX_VISITANTES) +bcolors.RESET)

def getVecinos(posicion):
    
    vecinos = []

    noroeste = posicion - 21
    norte = posicion - 20
    noreste = posicion - 19
    oeste = posicion - 1
    este = posicion + 1
    suroeste = posicion + 19
    sur = posicion + 20
    sureste = posicion + 21

    if noroeste > 0 and noroeste < 399:
        vecinos.append(noroeste)
    if  norte > 0 and noroeste < 399:
        vecinos.append(norte)
    if noreste > 0 and noroeste < 399:
        vecinos.append(noreste)
    if oeste > 0 and noroeste < 399:
        vecinos.append(oeste)
    if este > 0 and noroeste < 399:
        vecinos.append(este)
    if suroeste > 0 and noroeste < 399:
        vecinos.append(suroeste)
    if sur > 0 and noroeste < 399:
        vecinos.append(sur)
    if sureste > 0 and noroeste < 399:
        vecinos.append(sureste)

    return vecinos

def getMejor(posicion, vecinos, destino):
    mejorVecino = 999
    mejorPos = 999
    
    for vecino in vecinos:
        nuevaPos = abs(destino-vecino)
        if nuevaPos == 0:
            return posicion
        if mejorPos > nuevaPos:
            mejorPos = nuevaPos
            mejorVecino = vecino

    return mejorVecino

def siguienteMovimiento(user):
    alias = user['session']
    connection = sqlite3.connect('user.db')
    c = connection.cursor()
    c.execute(f"select inPark, posicion from user where alias = '{alias}'")

    result = c.fetchone()
    inPark = int(result[0])
    posicion = int(result[1])
    if inPark == 1:
        c.execute(f"select posicion, destino from user where alias = '{alias}'")
        result = c.fetchone()

        posicion = int(result[0])
        destino = int(result[1])
        atraccionActiva = False

        if(destino != "-1"):
            for atraccion in ATRACCIONES:
                if atraccion.getPosicion() == int(destino):
                    atraccionActiva = True
                    break
            if(atraccionActiva):
                vecinos = getVecinos(posicion)
                vecinoMejor = getMejor(posicion, vecinos, destino)

                if vecinoMejor != 999: 
                    c.execute(f"update user set posicion = '{vecinoMejor}' where alias = '{alias}'")
                    connection.commit()
                    connection.close()
                    
                    MAPA[posicion] = '-'
                    MAPA[vecinoMejor] = alias
    else:
        MAPA[posicion] == '-'

def comprobarInicio(data):
    alias = data['alias']
    password = data['password']

    try:
        connection = sqlite3.connect('user.db')

        c = connection.cursor()
        c.execute("select * from user where alias = ? and contraseña = ?", (alias, password))
    except Exception as e:
        return (F"Error al iniciar sesión: {e}")

    result = c.fetchall()
    connection.commit()
    connection.close()

    if len(result) != 0:
        return alias
    else:
        return "Error al iniciar sesión, introduce los datos correctamente."

def handle_visitor():
    fallo = True
    while fallo:
        try:
            consumer = KafkaConsumer('Visitor', bootstrap_servers=IP_BROKER+':'+str(PUERTO_BROKER))
            print(bcolors.KAFKA + f'[LISTENING] Escuchando mensajes de Kafka en el servidor {IP_BROKER}:{PUERTO_BROKER}' + bcolors.RESET)
            fallo = False
            for msg in consumer:
                msg = msg.value.decode(FORMAT)
                if "entrarParque" in msg:
                    gestionarEntrada(json.loads(msg))
                    sleep(5)
                    producirKafka(MAPA)
                elif "salirParque" in msg:
                    gestionarSalida(json.loads(msg))
                elif "mover" in msg:
                    siguienteMovimiento(json.loads(msg))
                    sleep(3)
                    producirKafka(MAPA)
                elif "iniciarSesion" in msg:
                    resultado = comprobarInicio(json.loads(msg))
                    sleep(3)
                    producirKafka(resultado)
        except kafka.errors.NoBrokersAvailable:
            print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+str(PUERTO_BROKER) + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
            sleep(10)

#Manejar servidor de tiempos de espera
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    waitingServer.send(send_length)
    waitingServer.send(message)

def vacio(list):

    for i in list:
        if i != '':
            return False
    return True
        
def calcularTiempo(ciclo, capacidad, cola):
    return ciclo*(cola/capacidad)+ciclo

def buenTiempo(atraccion):
    
    vecinos = getVecinos(atraccion.getPosicion())

    for vecino in vecinos:
        if MAPA[vecino] == 'b' or MAPA[vecino] == 'r' or MAPA[vecino] == 'n':
            return False
    return True

def cambiarMapa(serverResponse):
    
    msg = serverResponse[1:len(serverResponse)-1]

    atraccionAux = ""
    global ATRACCIONES
    ATRACCIONES = []

    for i in msg:
        if i != ")" and i != "(":
            atraccionAux += i  
        else:
            aux = re.split(", ", atraccionAux)
            if not(vacio(aux)):
                nuevaAtraccion = attraction(int(aux[0]), int(aux[1]), int(aux[2]), int(aux[3]), int(aux[4]), int(aux[5]))
                tiempo = calcularTiempo(nuevaAtraccion.getCiclo(), nuevaAtraccion.getCapacidad(), nuevaAtraccion.getCola())
                if nuevaAtraccion.getDisponible() == 1 and buenTiempo(nuevaAtraccion) and int(tiempo) < 60:
                    MAPA[nuevaAtraccion.getPosicion()] = int(tiempo)
                    ATRACCIONES.append(nuevaAtraccion)
                else:
                    MAPA[nuevaAtraccion.getPosicion()] = 'NA'
            atraccionAux = ""
    
    conn = sqlite3.connect('parque.db')
    c1 = conn.cursor()

    sql = 'update parque set parque = ?'
    mapa = str(MAPA)
    
    c1.execute(sql, (mapa,))

    conn.commit()
    conn.close()
    #ver que todas las atracciones de los usuarios en el mapa estan activas, si no es asi, cambiar el destino.
    conection = sqlite3.connect('user.db')
    c = conection.cursor()
    c.execute("select alias from user where inPark = 1")
    usuarios = c.fetchall()

    for user in usuarios:
        #Aqui actualizamos los destinos de los usuarios
        c.execute('select destino from user where alias = ?',(user))
        destino = c.fetchone()
        for dest in destino:
            destino = dest
            break

        esta = False
        for atraccion in ATRACCIONES:
            if atraccion.getPosicion() == destino:
                esta = True
                
        if not(esta) and len(ATRACCIONES) > 0:
            num = random.randint(0,len(ATRACCIONES)-1)

            c.execute(f"update user set destino = '{ATRACCIONES[num].getPosicion()}' where alias = ?", (user))
            conection.commit()

        elif len(ATRACCIONES) == 0:
            dest = -1
            c.execute(f"update user set destino = '{dest}' where alias = ?", (user))
            conection.commit()
    

    conection.close()

def start():
    while(True):
        send("Tiempos")
        serverResponse = waitingServer.recv(2048).decode(FORMAT)
        print('Respuesta del servidor: ' + serverResponse)
        cambiarMapa(serverResponse)
        sleep(3)

#Manejar tiempo actual
def current_weather():
    ultimoArchivo = []
    ultimosWeathers = []
    ultimasTemperaturas = ""
    
    while True:
        weathers = []

        temp = ""

        file = open('cityWeather.txt', 'r')
        archivo = file.read()
        urls = re.split("\n", archivo)

        if ultimoArchivo != archivo:
            ultimoArchivo = archivo

            for i in range (4):
                try:
                    response = requests.get(urls[i]).json()
                    temperatura = response['main']['temp']
                    temperatura = round(temperatura - 273,2)
                    if i < 3:
                        temp += str(temperatura)  + ':'
                        ultimasTemperaturas += str(temperatura)  + ':'
                    else:
                        temp += str(temperatura)
                        ultimasTemperaturas += str(temperatura)  + ':'
                    weathers.append({'name': response['name'],
                                    'temp': temperatura})
                    ultimosWeathers.append({'name': response['name'],
                                    'temp': temperatura})
                    print('La temperatura en ' +  response['name'] + ' es de ', temperatura)
                except KeyError:
                    weathers.append({'name': 'NA',
                                    'temp': 'NA'})
                    ultimosWeathers.append({'name': 'NA',
                                    'temp': 'NA'})
                    print(bcolors.WARNING + "Código de error:", response['cod'], " Mensaje: " + response['message'], bcolors.RESET)
            file.close()
            contador = 0
        else:
            file.close()
            contador = 0

            global MAPATEMP

            for weather in ultimosWeathers:
                if weather['name'] == 'NA':
                    if contador == 0:
                        for i in range(10):
                            for j in range(10):
                                if  MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'n' or MAPA[20*i+j] == '-':
                                    MAPA[20*i+j] = 'r'
                            
                    elif contador == 1:
                        for i in range(10):
                            for j in range(10, 20):
                                if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'n' or MAPA[20*i+j] == '-':
                                    MAPA[20*i+j] = 'r'
                    elif contador == 2:
                        for i in range(10,20):
                            for j in range(10):
                                if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'n' or MAPA[20*i+j] == '-':
                                    MAPA[20*i+j] = 'r'
                    elif contador == 3:
                        for i in range(10, 20):
                            for j in range(10, 20):
                                if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'n' or MAPA[20*i+j] == '-':
                                    MAPA[20*i+j] = 'r'
                else:
                    mapa = str(MAPA)

                    if weather['temp'] < 20:
                        if contador == 0:
                            for i in range(10):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'n' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'b'
                        elif contador == 1:
                            for i in range(10):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'n' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'b'
                        elif contador == 2:
                            for i in range(10,20):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'n' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':    
                                        MAPA[20*i+j] = 'b'
                        elif contador == 3:
                            for i in range(10, 20):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'n' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'b'

                    elif weather['temp'] > 30:
                        if contador == 0:
                            for i in range(10):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'n'
                        elif contador == 1:
                            for i in range(0, 10):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'n'
                        elif contador == 2:
                            for i in range(10,20):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'n'
                        elif contador == 3:
                            for i in range(10, 20):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == '-':
                                        MAPA[20*i+j] = 'n'
                    else:
                        if contador == 0:
                            for i in range(10):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == 'n':
                                        MAPA[20*i+j] = '-'

                        elif contador == 1:
                            for i in range(10):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == 'n':
                                        MAPA[20*i+j] = '-'

                        elif contador == 2:
                            for i in range(10,20):
                                for j in range(10):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == 'n':
                                        MAPA[20*i+j] = '-'

                        elif contador == 3:
                            for i in range(10, 20):
                                for j in range(10, 20):
                                    if MAPA[20*i+j] == 'b' or MAPA[20*i+j] == 'r' or MAPA[20*i+j] == 'n':
                                        MAPA[20*i+j] = '-'

                contador += 1

        conn = sqlite3.connect('user.db')
        c1 = conn.cursor()

        sql = 'select alias, posicion from user'
        c1.execute(sql)

        for user in c1.fetchall():
            ciudad = sacarCiudad(int(user[1]))
            c1.execute(f"update user set ciudad = '{ultimosWeathers[ciudad]['name']}' where alias = '{user[0]}'")
            conn.commit()
        
        conn.close()

        connection = sqlite3.connect('parque.db')
        c = connection.cursor()

        sql = 'update parque set parque = ?'
        mapa = str(MAPA)
        c.execute(sql, (mapa,))
        connection.commit()

        sql = 'update mapaTemp set temperaturas = ?'
        c.execute(sql, (ultimasTemperaturas,))
        connection.commit()

        connection.close()
        sleep(1)
    
def sacarCiudad(posUser):

    posUser = [posUser/20, posUser%20]

    if posUser[0] <= 9 and posUser[1] <= 9:
        return 0
    elif posUser[0] <= 9 and posUser[1] > 9:
        return 1
    elif posUser[0] > 9 and posUser[1] <= 9:
        return 2
    elif posUser[0] > 9 and posUser[1] > 9:
        return 3

########## MAIN ##########
try:

    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (IP_WAITING_SERVER, PUERTO_WAITING_SERVER)

    waitingServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fallo = True

    threading.Thread(target=handle_visitor).start()
    threading.Thread(target=current_weather).start()

    while fallo:
        try:
            waitingServer.connect(ADDR)
            fallo = False
        except socket.error:
            print(bcolors.FAIL + f"No se ha podido establecer la conexion con [{ADDR}], intentando reconectar..." + bcolors.RESET)
            fallo = True
            sleep(10)
        if not(fallo):
            print (bcolors.OK + f"Establecida conexión en [{ADDR}]" + bcolors.RESET)
            threading.Thread(target=start).start()

except IndexError:
    print(bcolors.FAIL +'FWQ_Engine requiere <IP_BROKER> <PUERTO_BROKER> <MAX_VISITANTES> <IP_FWQ_WAITINGTIMESERVER> <PUERTO_FWQ_WAITINGTIMESERVER>' + bcolors.RESET)

except ValueError:
    print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
        
