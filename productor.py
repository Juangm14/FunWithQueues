# producer.py
from time import sleep
from kafka import KafkaProducer
from json import dumps

producer = KafkaProducer(bootstrap_servers='192.168.0.173:9092',
                        value_serializer=lambda x:dumps(x).encode('utf-8'))

for e in range(1000):
    data = {'number': e }
    producer.send('SD', value=data)
    sleep(5)

