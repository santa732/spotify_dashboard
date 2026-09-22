import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# 1. Simulasi Data Pemutaran Lagu oleh Beberapa Pengguna (User vs Song)
# Angka menunjukkan berapa kali seorang user memutar lagu tersebut
data = {
    "Lagu A (Pop)": [5, 4, 0, 1, 0],
    "Lagu B (Pop)": [4, 5, 1, 0, 0],
    "Lagu C (Rock)": [0, 0, 5, 4, 5],
    "Lagu D (Rock)": [1, 0, 4, 5, 4],
    "Lagu E (Indie)": [2, 3, 3, 0, 1],
}

# 5 baris mewakili 5 Pengguna yang berbeda
df_matrix = pd.DataFrame(
    data, index=["User 1", "User 2", "User 3", "User 4", "User 5"]
)

print("--- User-Item Matrix (Frekuensi Pemutaran) ---")
print(df_matrix)
print("\n" + "=" * 50 + "\n")

# 2. Hitung Kemiripan Antar Lagu Berdasarkan Perilaku Pengguna (Item-Based Collaborative Filtering)
# Kita transpose matriksnya agar lagu jadi baris
song_similarity = cosine_similarity(df_matrix.T)
df_sim = pd.DataFrame(
    song_similarity, index=df_matrix.columns, columns=df_matrix.columns
)

print("--- Matriks Kemiripan Antar Lagu (Collaborative Filtering) ---")
print(df_sim.round(2))
print("\n" + "=" * 50 + "\n")

# 3. Simulasi Rekomendasi untuk User 1
# User 1 sangat suka Lagu A (diputar 5x). Lagu apa yang paling mirip berdasarkan kebiasaan pendengar lain?
target_song = "Lagu A (Pop)"
recom = df_sim[target_song].sort_values(ascending=False)[1:]

print(f"Rekomendasi untuk pendengar '{target_song}':")
for song_name, score in recom.items():
  print(f"- {song_name} | Skor Kemiripan Pendengar: {round(score * 100, 1)}%")