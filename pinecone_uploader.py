import pinecone
from sentence_transformers import SentenceTransformer
import json
import os
from pinecone import Pinecone, ServerlessSpec

# Inicjalizacja Pinecone
pc = Pinecone(api_key="pcsk_3mGEcH_UX7qiAM9Kepe3K7Lq9ucftY61ZhCQ1u7Cm1mQYdUZCSF2bXdEqv43gRJ32LtaFF")

index_name = "air-quality-index"

# Sprawdzanie dostępności indeksu
if index_name not in pc.list_indexes().names():
    # Tworzenie indeksu z określoną specyfikacją
    pc.create_index(
        name=index_name,
        dimension=384,  # Długość wektora (dla modelu 'all-MiniLM-L6-v2')
        metric="cosine",
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )

index = pc.Index(index_name)

# Wczytanie modelu do generowania wektorów
model = SentenceTransformer('all-MiniLM-L6-v2')

# Ładowanie dokumentów z plików
documents = []
for filename in os.listdir("output"):
    if filename.endswith(".json"):
        with open(os.path.join("output", filename), "r") as f:
            for line in f:
                document = json.loads(line)
                documents.append(document)

# Generowanie wektorów dla dokumentów
vectors = []
for doc in documents:
    vector = model.encode([doc["timestamp"] + f" pm2_5: {doc['pm2_5']} pm10: {doc['pm10']} so2: {doc['so2']}"])[0]
    vectors.append({
        "id": doc["timestamp"],
        "values": vector,
        "metadata": doc
    })

# Wstawienie wektorów do Pinecone
index.upsert(vectors=vectors)
print("Documents have been uploaded to Pinecone")