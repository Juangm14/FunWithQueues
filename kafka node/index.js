const kafka = require('kafka-node');

const client = new kafka.KafkaClient({ kafkaHost: '127.0.0.1:9092'})


/* Consumidor */
var consumer = new kafka.Consumer(client, [{topic: 'SD'}]);

consumer.on('message', function(message) {
    console.log(message);
})


/* Productor */
var producer = new kafka.Producer(client);

producer.on('ready', function() {

    setInterval(function(){
        producer.send([{ topic: 'SD', messages: 'Mensaje automatico cada 5 seg.'}], function(err, data) {});
    }, 5000)

});