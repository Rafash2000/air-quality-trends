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

# Inicjalizacja modelu generowania odpowiedzi
generator = pipeline("text-generation", model="gpt2")

# Funkcja do wyszukiwania dokumentów w Pinecone
def search_pinecone(query, top_k=5):
    # Kodowanie zapytania na wektor
    query_vector = model.encode([query])[0].tolist()

    # Wyszukiwanie w Pinecone
    result = index.query(vector=query_vector, top_k=top_k, include_metadata=True)

    return result['matches']

# Funkcja do generowania odpowiedzi na podstawie wyników wyszukiwania
def generate_answer(matches):
    if not matches:
        return "Nie znaleziono odpowiednich dokumentów."

    # Przygotowanie tekstu wejściowego na podstawie wyników z Pinecone
    input_text = "Na podstawie danych o zanieczyszczeniach powietrza, widzimy następujące tendencje:\n"
    
    # Filtrujemy tylko dane PM10, PM2.5 i SO2, aby uniknąć błędnych danych
    for match in matches:
        timestamp = match['metadata'].get('timestamp', 'Brak daty')
        pm10 = match['metadata'].get('pm10', None)
        pm2_5 = match['metadata'].get('pm2_5', None)
        so2 = match['metadata'].get('so2', None)

        if pm10 is not None and pm2_5 is not None and so2 is not None:
            input_text += f"Na dzień {timestamp}:\n- PM10: {pm10} µg/m³\n- PM2.5: {pm2_5} µg/m³\n- SO2: {so2} µg/m³\n\n"
        else:
            input_text += f"Na dzień {timestamp}: Dane zanieczyszczenia są niekompletne lub niepoprawne.\n\n"

    # Ograniczamy model do generowania tylko oczekiwanych danych
    response = generator(input_text, max_new_tokens=150, num_return_sequences=1, do_sample=False)
    
    # Zwrócenie wygenerowanej odpowiedzi
    answer = response[0]['generated_text']
    clean_answer = answer.strip()  # Usuwamy zbędne białe znaki

    return clean_answer


# Przykładowe zapytanie o tendencje zmian zanieczyszczeń
query = "What are the trends in PM2.5, PM10, and SO2 pollution levels?"
matches = search_pinecone(query)
answer = generate_answer(matches)
print("Generated Answer:", answer)
