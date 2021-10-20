const bodyParser = require('body-parser');
const express = require('express');
const path = require('path');
const bcrypt = require('bcrypt')
const mongoose = require('mongoose');
const User = require('./public/user');

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

app.listen(port, () =>{
    console.log('Escuchando en el puerto', port);
})

