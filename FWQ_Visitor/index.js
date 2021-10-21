const express = require('express');
const vodyParser = require('body-parser');
const path = require('path');

const portVisitante = 4000;

const port = process.env.port || process.argv[3]
const ip = process.argv[2];

const options = {
    ip,
    port
}

const app = express();

app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req,res) =>{
    
})


app.listen(portVisitante, () =>{
    console.log('Escuchando en el puerto', portVisitante);
})