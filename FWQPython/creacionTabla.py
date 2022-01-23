import sqlite3, hashlib

connection = sqlite3.connect('atraccion.db')
c = connection.cursor()

passw = hashlib.sha256("usuario1".encode()).hexdigest()

#sql = f"update user set contraseña='{passw}' where alias = 'usuario1'"

#sql = "delete from user where alias = 'jose'"

sql = "update atraccion set posicion = 284 where id = 2"

c.execute(sql)

connection.commit()
connection.close()