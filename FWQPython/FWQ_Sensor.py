from kafka import KafkaProducer
import kafka
from time import sleep
import sys
from json import dumps
import random

#Para mostrar los errores
class bcolors:
    OK = '\033[92m' #GREEN
    WARNING = '\033[93m' #YELLOW
    KAFKA = '\033[94m' #BLUE
    FAIL = '\033[91m' #RED
    RESET = '\033[0m' #RESET COLOR


try:
    IP_BROKER = sys.argv[2]
    PUERTO_BROKER = int(sys.argv[3])

    ID = int(sys.argv[1])
    FORMAT = 'utf-8'

    fallo = True

    while(fallo):
        try:
            producer = KafkaProducer(bootstrap_servers = IP_BROKER + ':' + str(PUERTO_BROKER),
                                    value_serializer=lambda x:dumps(x).encode(FORMAT))
            op = 0
            while op != "1" and op != "2":
                print("Como desea que se envien los datos?")
                print("1. Automaticamente.")
                print("2. Manualmente.")
                op = input()
            
            if op == "1":
                while True:
                    numVisitantes = random.randint(0,60)
                    data = [ID, numVisitantes]
                    producer.send('Sensor', value=data)
                    print(bcolors.OK + f'Se envió {data} correctamente a la dirección {IP_BROKER}:{PUERTO_BROKER}' +bcolors.RESET)
                    sleep(3)
            else:
                while True:
                    numVisitantes = input("Introduce el numero de visitantes que hay en la cola:")
                    data = [ID, int(numVisitantes)]
                    producer.send('Sensor', value=data)
                    print(bcolors.OK + f'Se envió {data} correctamente a la dirección {IP_BROKER}:{PUERTO_BROKER}' +bcolors.RESET)
                    sleep(3)

        except kafka.errors.NoBrokersAvailable:
            print(bcolors.FAIL + f'Actualmente no hay un broker disponible en la dirección {IP_BROKER}:{PUERTO_BROKER}. Espere a que se inicie el broker si la direccion es correcta o vuelva a intentarlo con otra dirección.' + bcolors.RESET)
        sleep(30)
except IndexError:
    print(bcolors.FAIL +'FWQ_Sensor requiere <ID> <IP_BROKER> <PUERTO_BROKER>' + bcolors.RESET)
except ValueError:
    print(bcolors.FAIL + 'No se puede convertir una palabra a un int. Por favor, introduce los datos correctamente.' + bcolors.RESET)
except KeyboardInterrupt:
    producer = KafkaProducer(bootstrap_servers = IP_BROKER + ':' + str(PUERTO_BROKER), value_serializer=lambda x:dumps(x).encode('utf-8'))
    data = f"Sensor:{ID}:ha sido desconectado."
    producer.send('Sensor', data)
    sleep(2)