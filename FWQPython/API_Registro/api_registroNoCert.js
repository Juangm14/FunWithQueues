const express = require('express')
const bodyParser = require("body-parser");
const sqlite3 = require('sqlite3').verbose()
const fs = require('fs')
const crypto = require('crypto');

const app = express()
app.use(bodyParser.json());

const ip = process.argv[2]
const port = parseInt(process.argv[3]);

const logs = '../logs.txt'


//CONEXION CON LA BASE DE DATOS.
const db = new sqlite3.Database('../user.db', sqlite3.OPEN_READWRITE, function(err) {
    if(err) return console.error(err.message)

    console.log('Conectado a la base de datosde usuarios correctamente.')
})

const dbLogs = new sqlite3.Database('../logs.db', function(err) {
    if(err) return console.error(err.message)

    console.log('Conectado a la base de datos de logs correctamente.')
})

//VALIDACION DEL ARCHIVO DE LOGS
fs.access(logs, fs.constants.F_OK, function(err){
    if(err) console.log('Error en el acceso a logs.')
    else console.log('Preparado para guardar logs.');
})

//LLAMADA A LA LECTURA Y ESCRITURA EN EL FICHERO LOF
function fichero(logs, newData){
    fs.readFile(logs, function(err, data){
        if (err) console.log(err);

        if(data != undefined){
            datosLogs = data.toString() + "\n" + JSON.stringify(newData)  

            fs.writeFile(logs, datosLogs, function(err){
                if (err) console.log(err);
            })
        }else{
            datosLogs = JSON.stringify(newData)  

            fs.writeFile(logs, datosLogs, function(err){
                if (err) console.log(err);
            })
        }
    })
}

//Listamos un usuario
app.get('/usuarios/:alias', function(req, res) {
    console.log('Listando un usuario');

    const {alias} = req.params
    sql = `select * from user where alias = '${alias}'`
    
    db.all(sql,[], (err, rows) => {
        if (err){
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Error al listar el usuario. " + err.message,
                "parametros": alias
            };

            sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
            dbLogs.run(sql, function(err) {
                if (err) {
                  return console.log(err.message);
                }
              });
    
            fichero(logs, newData)
            res.status(500).send(err.message)

        }else{
            if (rows.length > 0){
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "Listar un usuario.",
                    "parametros": alias
                };

                sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                dbLogs.run(sql, function(err) {
                    if (err) {
                      return console.log(err.message);
                    }
                  });

                fichero(logs, newData)
                res.json(rows)
            }else{
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "No se han encontrado usuarios con ese alias.",
                    "parametros": alias
                };

                sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                dbLogs.run(sql, function(err) {
                    if (err) {
                      return console.log(err.message);
                    }
                  });
                
                fichero(logs, newData)
                res.status(500).send('No hay resultados');
            }
        }   
    })    
})

//Creacion de un usuario
app.post('/usuarios/signup', function(req, res) {

    const hash = crypto.createHash('sha256');
    const newUser = { 
        alias: req.body.alias,
        nombre: req.body.nombre,
        password: hash.update(req.body.password).digest('hex')
    }

    var rnd = Math.random() * (399 - 0) + 0;
    var sql = `insert into user values('${newUser['alias']}','${newUser['nombre']}','${newUser['password']}', 0, '${Math.round(rnd)}', -1, 'None')`

    db.run(sql, (err) =>{
        if (err) {
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Error en la creacion del usuario. " + err.message,
                "parametros": newUser['alias']
            };

            sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
            dbLogs.run(sql, function(err) {
                if (err) {
                  return console.log(err.message);
                }
            });

            fichero(logs, newData)

            return res.status(500).send("ERROR: " + err.message)
        }else{
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Se ha registrado un nuevo usuario",
                "parametros": newUser['alias']
            };

            var sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
            dbLogs.run(sql, function(err) {
                if (err) {
                  return console.log(err.message);
                }
            });

            fichero(logs, newData)
        }

        res.send('Se ha introducido correctamente un nuevo usuario.')
    })
})

//Modificacion de un usuario
app.put('/usuarios/perfil', function(req, res) {
    const hash = crypto.createHash('sha256');
    const {alias} = req.params
    const changedUser = {
        nombre: req.body.nombre,
        password: hash.update(req.body.password).digest('hex')
    }

    const sql = `update user set nombre = '${changedUser['nombre']}', contraseña = '${changedUser['password']}' where alias = '${alias}'`

    db.run(sql, (err) =>{
        if (err) {
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Error al modificar el usuario " + err.message,
                "parametros": alias
            };

            sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
            dbLogs.run(sql, function(err) {
                if (err) {
                  return console.log(err.message);
                }
            });

            fichero(logs, newData)
            res.status(500).send("ERROR: " + err.message) 
        }else{
            const sql = `select * from user where alias = '${alias}'`
            db.all(sql, function(err, rows) {
                if(err){
                    let newData = {
                        "fecha": new Date(),
                        "ip": req.ip,
                        "accion": "No se ha podido realizar la consulta" + err.message,
                        "parametros": alias
                    };

                    sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                    dbLogs.run(sql, function(err) {
                        if (err) {
                          return console.log(err.message);
                        }
                    });

                    fichero(logs, newData)
                    res.status(500).send("ERROR:" + err.message)
                }

                if(rows.length > 0){
                    let newData = {
                        "fecha": new Date(),
                        "ip": req.ip,
                        "accion": "Usuario modificado correctamente.",
                        "parametros": alias
                    };

                    sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                    dbLogs.run(sql, function(err) {
                        if (err) {
                          return console.log(err.message);
                        }
                    });
                    
                    sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                    dbLogs.run(sql, function(err) {
                        if (err) {
                          return console.log(err.message);
                        }
                    });

                    fichero(logs, newData)
                    return res.send('Usuario ' + alias + ' modificado correctamente.')
                }else{
                    let newData = {
                        "fecha": new Date(),
                        "ip": req.ip,
                        "accion": "No se ha encontrado ningun usuario que coincida con el parametro.",
                        "parametros": alias
                    };

                    sql = `insert into logs values('${newData.ip}', '${newData.fecha}','${newData.accion}','${newData.parametros}')`
                    dbLogs.run(sql, function(err) {
                        if (err) {
                          return console.log(err.message);
                        }
                    });

                    fichero(logs, newData)
                    res.status(500).send('ERROR: No se ha encontrado ningun usuario con el alias: ' + alias)
                }
            })
        }
    })
})

app.get('/logs', function(req, res) {

    sql = `select * from logs`
    
    dbLogs.all(sql,[], (err, rows) => {
        res.send(rows)
    })

})

app.listen(port, ip, () => {
    console.log(`Ejecutando la API Registro en ${ip} con puerto ${port}`);
});

/* MÉTODOS QUE CREO QUE NO DEBERÍAN DE IR AQUÍ 

//Eliminacion de un usuario
app.delete('/usuarios/:alias', function(req, res){

    const {alias} = req.params
    const sql = `delete from user where alias = '${alias}'`
    console.log(alias)
    db.run(sql, (err, rows) =>{
        if (err) return res.send(err.message)

        res.send('Usuario eliminado correctamente.')
    })
})

//Listamos los usuarios
app.get('/usuarios',function (req, res) {
    console.log('Listado de todos los usuarios');

    sql = 'select * from user'
    db.all(sql, [], (err, rows) => {
        if (err) return console.error(err.message)

        if (rows.length > 0){
            res.json(rows)
        }else{
            res.send('No hay resultados');
        }
            
    })    
})
*/