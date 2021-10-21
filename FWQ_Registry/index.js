const bodyParser = require('body-parser');
const express = require('express');
const path = require('path');
const bcrypt = require('bcrypt')
const mongoose = require('mongoose');
const User = require('./public/user');
const router = require('express').Router();

const app = express();
const port = process.env.port || process.argv[2]

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }))

app.use(express.static(path.join(__dirname, 'public')));

const mongodb = 'mongodb://localhost/parque'

mongoose.connect(mongodb, function(err){
    if(err){
        throw err;
    }else{
        console.log('Conectado a mongoose correctamente');
    }
})

app.post('/registro', (req, res) =>{
    const {username, nombre, password} = req.body;
    const user = new User({username, nombre, password})

    user.save(err =>{
        if(err){
            res.status(500).send('Error al registrar al usuario')
        }else{
            res.status(200).send('Usuario Registrado')
        }
    })
});


app.get('/modificarPerfil', (req, res) =>{
    res.sendFile(path.join(__dirname, './public/modificar.html'));
})

app.post('/modificar', (req,res) =>{
    const {username, nombre, password} = req.body;
    const user = new User({username, nombre, password})

    User.findOneAndUpdate({username: username}, {$set: req.body}, function(err, info){

        if(err){
            res.json({
                resultado: false,
                msg: "No se pudo modificar el cliente",
                err
            })
        }else{
            res.json({
                resultado: true,
                info: info
            })
        }
    });
})


app.listen(port, () =>{
    console.log('Escuchando en el puerto', port);
})

