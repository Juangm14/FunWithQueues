const express = require('express');
const vodyParser = require('body-parser');
const path = require('path');
const { dirname } = require('path');

const portVisitante = 4000;

const port = process.env.port || process.argv[3]
const ip = process.argv[2];


//IP y puerto de FWQ_Registry
const options = {
    ip,
    port
}

const app = express();

app.use(express.static(path.join(__dirname, 'public')));

app.get('/modificarPerfil', (req, res) => {
    res.sendFile(path.join(__dirname, './public/modificarPerfil.html'));
})

app.get('/inicioSesion', (req,res) =>{
    res.sendFile(path.join(__dirname, './public/inicioSesion.html'));
})

app.post('/iniciarSesion', (req, res) => {
    
})

app.listen(portVisitante, () =>{
    console.log('Escuchando en el puerto', portVisitante);
})