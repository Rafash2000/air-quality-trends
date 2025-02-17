import json
import requests
from confluent_kafka import Producer
from datetime import datetime
import time

# Konfiguracja API OpenWeatherMap
API_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
API_PARAMS = {
    "lat": 54.3521,
    "lon": 18.6466,
    "appid": "eea06064812440076595c2978ddda550"
}

# Konfiguracja Kafka
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "air_quality"

# Funkcja do pobierania danych z API
def fetch_air_quality():
    response = requests.get(API_URL, params=API_PARAMS)
    if response.status_code == 200:
        data = response.json()
        components = data.get("list", [{}])[0].get("components", {})
        return {
            "pm2_5": components.get("pm2_5", None),
            "pm10": components.get("pm10", None),
            "so2": components.get("so2", None),
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise Exception(f"API Error: {response.status_code} - {response.text}")

# Funkcja do wysyłania danych do Kafki
def publish_to_kafka(producer, topic, message):
    producer.produce(topic, value=json.dumps(message))
    producer.flush()
    print(f"Published to Kafka: {message}")

# Główna funkcja
def main():
    # Tworzenie instancji KafkaProducer
    producer = Producer({"bootstrap.servers": KAFKA_BROKER})
    try:
        while True:
            air_quality_data = fetch_air_quality()
            print(f"Fetched Data: {air_quality_data}")

            publish_to_kafka(producer, TOPIC_NAME, air_quality_data)

            time.sleep(86400)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
