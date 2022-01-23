const express = require('express')
const bodyParser = require("body-parser");
const sqlite3 = require('sqlite3').verbose()
const fs = require('fs')
const crypto = require('crypto');
const https = require('https')

const app = express()
app.use(bodyParser.json());

const port = 3000;
const logs = '../logs.txt'

const OPTIONS_HTTPS = {
    key: fs.readFileSync('./cert/key.pem'),
    cert: fs.readFileSync('./cert/cert.pem')
};

//CONEXION CON LA BASE DE DATOS.
const db = new sqlite3.Database('../user.db', sqlite3.OPEN_READWRITE, function(err) {
    if(err) return console.error(err.message)

    console.log('Conectado a la base de datos correctamente.')
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
    
            fichero(logs, newData)
            return console.error(err.message)

        }else{
            if (rows.length > 0){
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "Listar un usuario.",
                    "parametros": alias
                };

                fichero(logs, newData)
                res.json(rows)
            }else{
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "No se han encontrado usuarios con ese alias.",
                    "parametros": alias
                };
                fichero(logs, newData)
                res.send('No hay resultados');
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
    const sql = `insert into user values('${newUser['alias']}','${newUser['nombre']}','${newUser['password']}', 0, '${Math.round(rnd)}', -1, 'None')`

    db.run(sql, (err) =>{
        if (err) {
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Error en la creacion del usuario. " + err.message,
                "parametros": newUser['alias']
            };

            fichero(logs, newData)

            return res.send("ERROR: " + err.message)
        }else{
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "Error en la creacion del usuario.",
                "parametros": newUser['alias']
            };

            fichero(logs, newData)
        }

        res.send('Se ha introducido correctamente un nuevo usuario.')
    })
})

//Modificacion de un usuario
app.put('/usuarios/:alias', function(req, res) {
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

            fichero(logs, newData)
            return res.send("ERROR: " + err.message) 
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

                    fichero(logs, newData)
                    return res.send("ERROR:" + err.message)
                }

                if(rows.length > 0){
                    let newData = {
                        "fecha": new Date(),
                        "ip": req.ip,
                        "accion": "Usuario modificado correctamente.",
                        "parametros": alias
                    };

                    fichero(logs, newData)
                    return res.send('Usuario ' + alias + ' modificado correctamente.')
                }else{
                    let newData = {
                        "fecha": new Date(),
                        "ip": req.ip,
                        "accion": "No se ha encontrado ningun usuario que coincida con el parametro.",
                        "parametros": alias
                    };

                    fichero(logs, newData)
                    return res.send('ERROR: No se ha encontrado ningun usuario con el alias: ' + alias)
                }
            })
        }
    })
})

https.createServer(OPTIONS_HTTPS, app).listen(port, () => {
    console.log(`Ejecutando la API Registro en el puerto ${port}`);
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



/* ASIMETRICO CON LLAVES GENERADAS
//Llave privada de la api
let private_key = fs.readFileSync('private_key.txt', 'utf-8')
let key_private = new nodeRSA(private_key, 'private')
//Llave publica del visitante
let public_key = fs.readFileSync('../public_key.txt', 'utf-8')
let key_public = new nodeRSA(public_key, 'public')
*/