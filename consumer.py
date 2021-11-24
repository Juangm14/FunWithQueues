from kafka import KafkaConsumer

consumer = KafkaConsumer('SD')

for msg in consumer:
    print (msg.value)