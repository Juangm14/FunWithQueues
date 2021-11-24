#CREACION DE LA TABLA
"""
import sqlite3
connection = sqlite3.connect('atraccion.db')

c = connection.cursor()

c.execute('Create table atraccion(
    id number(3) primary key,
    tiempoCiclo number(4) not null,
    capacidad number(2) not null,
    numVisitantes number(3) not null)')


c.execute("CREATE TABLE user(
    alias text primary key,
    nombre text not null,
    contraseña text not null
)")

connection.commit()
connection.close()


connection = sqlite3.connect('atraccion.db')
c = connection.cursor()
c.execute('insert into atraccion values(1,30,10)')
connection.commit()
connection.close()
"""

import sqlite3

connection = sqlite3.connect('user.db')

c = connection.cursor()

c.execute("update user set posicion = '240' where alias = 'admin'")

connection.commit()

connection.close()