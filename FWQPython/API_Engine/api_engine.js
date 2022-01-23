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


//Conexion con la base de datos de los usuarios
const dbUser = new sqlite3.Database('../user.db', sqlite3.OPEN_READWRITE, function(err) {
    if(err) return console.error(err.message)

    console.log('Conectado a la base de datos de los usuarios correctamente.')
})

//Conexion con la base de datos del parque
const dbParque = new sqlite3.Database('../parque.db', sqlite3.OPEN_READWRITE, function(err) {
    if(err) return console.error(err.message)

    console.log('Conectado a la base de datos del parque correctamente.')
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

//Listamos los usuarios
app.get('/usuarios',function (req, res) {
    console.log('Listado de todos los usuarios');

    sql = 'select * from user'
    dbUser.all(sql, [], (err, rows) => {
        if (err) {
            return console.error(err.message)
        }else{
            if (rows.length > 0){
                res.json(rows)
            }else{
                res.send('No hay resultados');
            }
        }
            
    })    
})

//Listamos los usuarios que estan en el mapa
app.get('/usuarios/inPark',function (req, res) {
    console.log('Listado de todos los usuarios que estan en el parque');

    sql = 'select * from user where inPark = 1'
    dbUser.all(sql, [], (err, rows) => {
        if (err) {
            return console.error(err.message)
        }else{
            if (rows.length > 0){
                res.json(rows)
            }else{
                res.send([]);
            }
        }
            
    })    
})

//Listamos un usuario
app.get('/usuario/:alias', function(req, res) {
    console.log('Listando un usuario');

    const {alias} = req.params
    sql = `select * from user where alias = '${alias}'`
    
    dbUser.all(sql,[], (err, rows) => {
        if (err) {
            let newData = {
                "fecha": new Date(),
                "ip": req.ip,
                "accion": "LISTANDO USUARIO: Error no se ha podido seleccionar al usuario. " + err.message,
                "parametros": alias
            };
    
            fichero(logs, newData)
            return console.error(err.message)
        }else{
            if (rows.length > 0){
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "LISTANDO USUARIO: Listando usuario correctamente",
                    "parametros": alias 
                };
        
                fichero(logs, newData)
                res.json(rows)
            }else{
                let newData = {
                    "fecha": new Date(),
                    "ip": req.ip,
                    "accion": "LISTANDO USUARIO: No existe ese usuario en la base de datos.",
                    "parametros": alias
                };
        
                fichero(logs, newData)
                res.send('No hay resultados.');
            }
        }      
    })    
})

//Eliminacion de un usuario
app.delete('/usuarios/:alias', function(req, res){

    const {alias} = req.params
    const select = `select * from user where alias ='${alias}'`
    const sql = `delete from user where alias = '${alias}'`

    dbUser.all(select, (err, rows) => {
        if (err){
            
        }else{
            if(rows.length > 0){
                dbUser.run(sql, (err) =>{

                    if (err){ 
                        return res.send(err.message)
                    }else{
                        res.send('Usuario eliminado correctamente.')
                    }
                })
            }else{
                return res.send("No existe un usuario con ese alias.")
            }
        }
    })

})

//Cogemos el parque
app.get('/parque', function (req, res) {
    console.log('Mostrando mapa.');

    sql = 'select * from parque'
    dbParque.all(sql, [], (err, rows) => {
        if (err){
            return console.error(err.message)
        }else{
            if (rows.length > 0){
                rows = rows['0']
                rows = rows['parque']
                mapa = rows.split(",")

                for(i = 0; i < mapa.length; i++){
                    if(mapa[i] == " 'b'" || mapa[i] == "['b'" || mapa[i] == " 'b']"){
                        mapa[i] = 'b'
                    }else if(mapa[i] == " 'n'" || mapa[i] == "['n'" || mapa[i] == " 'n']"){
                        mapa[i] = 'n'
                    }else if(mapa[i] == " 'r'" || mapa[i] == "['r'" || mapa[i] == " 'r']"){
                        mapa[i] = 'r'
                    }else if(mapa[i] == " '-'" || mapa[i] == "['-'" || mapa[i] == " '-']"){
                        mapa[i] = '-'
                    }else if(mapa[i] == " 'NA'" || mapa[i] == "['NA'" || mapa[i] == " 'NA']"){
                        mapa[i] = 'NA'
                    }
                }
                res.send(mapa)
            }else{
                res.send('No hay resultados');
            }
        }    
    })    
})

//No hace ace falta pero lo mostramos
app.post('/usuarios/signin', function(req, res){
    const hash = crypto.createHash('sha256');
    const alias = req.body.alias
    const password = req.body.password

    console.log(alias, password)
    sql = `select contraseña from user where alias = '${alias}'`

    dbUser.all(sql,[], (err, rows) => {
        if (err) {
            res.send('Error: No se ha podido conectar con la base de datos.')
        }else{
            var contraseña = rows[0].contraseña

            var password1 = hash.update(password).digest('hex')

            if(password1 == contraseña){
                res.send('Se ha iniciado sesión correctamente.')
            }else{
                res.send('Error: Alguna de las credenciales es errónea, intentalo de nuevo.')
            }
        }
    })


})

//Mostramos las temperaturas del mapa
app.get('/temperaturas', function(req, res){

    console.log('Mostrando temperaturas del mapa.');

    sql = 'select * from mapaTemp'
    dbParque.all(sql, [], (err, rows) => {
        if (err){
            return console.error(err.message)
        }else{
            if (rows.length > 0){
                rows = rows['0']
                res.send(rows)
            }else{
                res.send('No hay resultados');
            }
        }    
    })    
})

app.listen(port, ip, () => {
    console.log(`Ejecutando la aplicación API REST de Engine en ${ip} con el puerto ${port}`);
})


/* METODOS QUE CREO QUE NO DEBERIAN DE IR AQUÍ
//Creacion de un usuario
app.post('/usuarios', function(req, res) {

    const newUser = { 
        alias: req.body.alias,
        nombre: req.body.nombre,
        password: req.body.password
    }

    var rnd = Math.random() * (399 - 0) + 0;
    const sql = `insert into user values('${newUser['alias']}','${newUser['nombre']}','${newUser['password']}', 0, '${Math.round(rnd)}', -1)`

    dbUser.run(sql, (err, rows) =>{
        if (err) return res.send(err.message)

        res.send('Se ha introducido correctamente un nuevo usuario.')
    })
})

//Modificacion de un usuario
app.put('/usuarios/:alias', function(req, res) {
    const {alias} = req.params
    const changedUser = {
        nombre: req.body.nombre,
        password: req.body.password
    }

    const sql = `update user set nombre = '${changedUser['nombre']}', contraseña = '${changedUser['password']}' where alias = '${alias}'`

    dbUser.run(sql, (err, rows) =>{
        if (err) return res.send(err.message)
        
        res.send('Se ha modificado correctamente el usuario.')
    })
})

*/ 