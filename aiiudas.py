from inspect import Parameter
import socket
import sys, os, re
import threading, kafka
# producer Kafka
from kafka import KafkaProducer, KafkaConsumer
from json import dumps

class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR

def cleaning():
    if sys.platform.startswith('win'):
        os.system('cls')
    elif sys.platform.startswith('darwin'):
        os.system('clear')
    elif sys.platform.startswith('linux'):
        os.system('clear')

def send(msg): 
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)


def handle_engine(data):
        try:
            consumer = KafkaConsumer('Engine', bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER)
            print(bcolors.KAFKA + f'[LISTENING] Escuchando mensajes de Kafka en el servidor {IP_BROKER}:{PUERTO_BROKER}' + bcolors.RESET)
            if data == "entrarParque":
                for msg in consumer:
                    msg = msg.value.decode(FORMAT)
                    msg = re.split(",", msg)
                    cleaning()
                    mostrarMapa(msg)
            else:
                print('entra')
                consumer.unsubscribe
                consumer.close
        except kafka.errors.NoBrokersAvailable:
            print(bcolors.FAIL +'Actualmente no hay un broker disponible en la dirección ' + IP_BROKER +':'+PUERTO_BROKER + '. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)

def entrarParque():

    #Creamos un productor para enviar solo un mensaje.
    producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                        value_serializer=lambda x:dumps(x).encode('utf-8'))
    arguments = "entrarParque"
    data = {'data': 'entrarParque',
            'session': SESSION}
    producer.send('Visitor', value=data)

    threading.Thread(target=handle_engine, args=(arguments,)).start()

def salirParque():
    producer = KafkaProducer(bootstrap_servers=IP_BROKER+':'+PUERTO_BROKER,
                        value_serializer=lambda x:dumps(x).encode('utf-8'))

    data = {'data': "salirParque",
            'session': SESSION}
    arguments = "salirParque"
    producer.send('Visitor', value=data)

    threading.Thread(target=handle_engine, args=(arguments,)).start()
    producer.close()
