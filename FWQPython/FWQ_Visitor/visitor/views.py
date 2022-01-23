from os import curdir
from django.shortcuts import render
from django.contrib import messages
from django.template.defaulttags import VerbatimNode, register
from datetime import datetime
import requests

MAPA = []
VECES = 0

@register.filter
def isDigit(e):
    try:
        e = int(e)
        return True
    except ValueError:
        return False

@register.filter
def elemento(pos, array):
    return array[pos]


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def map(request):
    global MAPA
    global VECES

    context = {
        'mapa' : [],
        'posiciones' : [],
        'mapaTemp': [],
        'rango': [],
        'mensaje': 'Se ha producido un error al conectarse a la API Engine. Intentalo de nuevo más tarde.'
    }

    try:
        mapa = requests.get(f'http://192.168.56.1:3001/parque').json()
        users = requests.get('http://192.168.56.1:3001/usuarios/inPark').json()
        temperaturas = requests.get('http://192.168.56.1:3001/temperaturas').json()

        if mapa == MAPA:
            VECES += 1
        else:
            VECES = 0

        MAPA = mapa

        allUsers = []

        for user in users:

            auxiliar = {'avatar': 1,
                        'alias': user['alias'],
                        'nombre': user['nombre'],
                        'password': user['contraseña'],
                        'inPark': user['inPark'],
                        'posicion': divmod(int(user['posicion']), 20),
                        'destino': divmod(int(user['destino']), 20),
                        'ciudad': user['ciudad']}

            allUsers.append(auxiliar)

        temperaturas = temperaturas['temperaturas'].split(":")

        mapaTemp = []
        pos = []
        for i in range(400):
            mapaTemp.append(0)
            pos.append(i)

        for j in range(10):
            for k in range(10):
                mapaTemp[20*j+k] = temperaturas[0] 
            
        for j in range(10):
            for k in range(10, 20):
                mapaTemp[20*j+k] = temperaturas[1]

        for j in range(10, 20):
            for k in range(10):
                mapaTemp[20*j+k] = temperaturas[2] 

        for j in range(10, 20):
            for k in range(10, 20):
                mapaTemp[20*j+k] = temperaturas[3]
        
        if VECES > 5:
            context = {
                'mapa' : [],
                'posiciones' : [],
                'mapaTemp': [],
                'rango': [],
                'mensaje': 'Parece que el componente Engine esta desconectado. Intentalo de nuevo mas tarde'
            }
        else:
            context = {
                'mapa' : mapa,
                'posiciones' : allUsers,
                'mapaTemp': mapaTemp,
                'rango': pos,
                'mensaje': 'Todo funciona correctamente'
        }


    except Exception:
        messages.error(request, (''))

    return render(request, 'visitor/map.html', context)

def usuarios(request):
    allUsers = []
    context = {
            'allUsers' : allUsers
    }

    try:
        result = requests.get('http://localhost:3001/usuarios').json()

        for user in result:

            auxiliar = {'avatar': 1,
                        'alias': user['alias'],
                        'nombre': user['nombre'],
                        'password': user['contraseña'],
                        'inPark': user['inPark'],
                        'posicion': divmod(int(user['posicion']), 20),
                        'destino': divmod(int(user['destino']), 20),
                        'ciudad': user['ciudad']}

            allUsers.append(auxiliar)

        context = {
                'allUsers' : allUsers
        }

    except Exception as e:
        f = open ("../logs.txt", "a")
        newData = {
            "fecha": datetime.today(),
            "ip": get_client_ip(request),
            "accion": e,
            "parametros": ""
        }
        f.write(str(newData)+"\n")
        f.close()

    return render(request, 'visitor/usuarios.html', context)

def usuario(request, alias):

    allUsers = []
    context = {
        'allUsers' : allUsers
    }

    try:
        result = requests.get(f'http://localhost:3001/usuario/{alias}').json()
        
        for user in result:
            allUsers.append({'avatar': 1,
                            'alias': user['alias'],
                            'nombre': user['nombre'],
                            'password': user['contraseña'],
                            'inPark': user['inPark'],
                            'posicion': divmod(int(user['posicion']), 20),
                            'destino': divmod(int(user['destino']), 20),
                            'ciudad': user['ciudad']})
        context = {
                'allUsers' : allUsers
        }

    
    except Exception as e:
        newData = {
            "fecha": datetime.today(),
            "ip": get_client_ip(request),
            "accion": e,
            "parametros": ""
        }


    return render(request, 'visitor/usuarios.html', context)

        
