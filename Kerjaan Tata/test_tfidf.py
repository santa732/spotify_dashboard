import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 1. Contoh Data Lagu Sederhana
data = {
    "title": [
        "Mantan Terindah",
        "Hati-Hati di Jalan",
        "Selamat Jalan Kekasih",
        "Gelora Asmara",
    ],
    "artist": ["Kahitna", "Tulus", "Kunto Aji", "Groovy Band"],
    "genre": ["Pop", "Pop", "Indie Pop", "Rock"],
    "mood": ["Sad Melancholy", "Sad Galau", "Melancholy Calm", "Energetic Happy"],
}

df = pd.DataFrame(data)

# 2. Gabungkan Teks Genre dan Mood menjadi satu fitur "text_features"
df["text_features"] = df["genre"] + " " + df["mood"]
print("--- Fitur Teks Gabungan ---")
print(df[["title", "text_features"]])
print("\n" + "=" * 40 + "\n")

# 3. Hitung Matriks TF-IDF
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(df["text_features"])

# 4. Hitung Cosine Similarity antar seluruh lagu
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# 5. Simulasi Mencari Lagu yang Mirip dengan "Mantan Terindah" (Indeks 0)
target_index = 0
similarity_scores = list(enumerate(cosine_sim[target_index]))

# Urutkan dari skor tertinggi ke terendah (abaikan lagu itu sendiri)
sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[1:]

print(
    f"Lagu Acuan: '{df.iloc[target_index]['title']}' ({df.iloc[target_index]['text_features']})"
)
print("--- Rekomendasi Lagu Berdasarkan Kemiripan Teks (TF-IDF): ---")

for idx, score in sorted_scores:
  song = df.iloc[idx]
  print(
      f"- {song['title']} oleh {song['artist']} | Skor Kemiripan: {round(score * 100, 1)}%"
  )