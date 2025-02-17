import os
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import json

# Inicjalizacja Pinecone
api_key = "pcsk_3mGEcH_UX7qiAM9Kepe3K7Lq9ucftY61ZhCQ1u7Cm1mQYdUZCSF2bXdEqv43gRJ32LtaFF"
pc = Pinecone(api_key=api_key, environment="us-east-1-gcp")
index_name = "air-quality-index"
index = pc.Index(index_name)

# Inicjalizacja modelu do kodowania zapytań
model = SentenceTransformer('all-MiniLM-L6-v2')

# Inicjalizacja modelu generowania odpowiedzi (np. distilgpt2)
generator = pipeline("text-generation", model="distilgpt2")

# Funkcja do wyszukiwania dokumentów w Pinecone
def search_pinecone(query, top_k=3):
    # Kodowanie zapytania na wektor
    query_vector = model.encode([query])[0].tolist()  # Konwertujemy na listę

    # Wyszukiwanie w Pinecone
    result = index.query(vector=query_vector, top_k=top_k, include_metadata=True)

    return result['matches']

# Funkcja do generowania odpowiedzi na podstawie wyników wyszukiwania
def generate_answer(matches):
    if not matches:
        return "No relevant documents found."

    # Przygotowanie tekstu wejściowego na podstawie wyników z Pinecone
    input_text = " ".join([match['metadata']['timestamp'] + ": PM10=" + str(match['metadata']['pm10']) +
                           ", PM2.5=" + str(match['metadata']['pm2_5']) + ", SO2=" + str(match['metadata']['so2'])
                           for match in matches])

    # Generowanie odpowiedzi za pomocą modelu językowego
    response = generator(input_text, max_new_tokens=100, num_return_sequences=1)  # Użycie max_new_tokens

    # Zwrócenie wygenerowanej odpowiedzi
    return response[0]['generated_text']

# Przykładowe zapytanie o tendencje zmian zanieczyszczeń
query = "What are the trends in PM2.5, PM10, and SO2 pollution levels?"
matches = search_pinecone(query)
answer = generate_answer(matches)
print("Generated Answer:", answer)
