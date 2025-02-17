from confluent_kafka import Consumer, KafkaException, KafkaError
import json
import os
from datetime import datetime

# Konfiguracja konsumenta
conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-consumer-group',
    'auto.offset.reset': 'earliest'
}

# Inicjalizacja konsumenta
consumer = Consumer(conf)

# Subskrypcja topicu
consumer.subscribe(['air_quality'])

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())

        # Przetwarzanie wiadomości
        data = json.loads(msg.value().decode('utf-8'))
        print(f"Received message: {data}")

        # Tworzenie pliku z danymi
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{timestamp}_air_quality.json"
        file_path = os.path.join("output", filename)

        if not os.path.exists("output"):
            os.makedirs("output")

        with open(file_path, "a") as f:
            json.dump(data, f)
            f.write("\n")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
