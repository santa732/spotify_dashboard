import os
import sqlite3
import pandas as pd

# 1. Koneksi ke database tata.db
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'tata.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Re-create tabel dengan struktur baru (duration_sec & mood)
cursor.executescript('''
DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    genre TEXT,
    duration_sec INTEGER,
    mood TEXT
);

INSERT INTO songs (title, artist, genre, duration_sec, mood) VALUES 
('Ghost', 'Justin Bieber', 'Pop', 153, 'Chill'),
('Peaches', 'Justin Bieber', 'Pop', 198, 'Energetic'),
('vampire', 'Olivia Rodrigo', 'Pop', 219, 'Sad'),
('drivers license', 'Olivia Rodrigo', 'Pop', 242, 'Sad'),

('ILYSB', 'LANY', 'Indie Pop', 253, 'Chill'),
('dna', 'LANY', 'Indie Pop', 177, 'Chill'),
('High School in Jakarta', 'NIKI', 'Indie Pop', 219, 'Energetic'),
('Every Summertime', 'NIKI', 'Indie Pop', 215, 'Energetic'),

('To the Bone', 'Pamungkas', 'Indie Pop', 344, 'Chill'),
('Evaluasi', 'Hindia', 'Indie Pop', 202, 'Sad'),
('Rumah Ke Rumah', 'Hindia', 'Indie Pop', 287, 'Sad'),
('Biarkan Tumbal Berganti', 'Perunggu', 'Rock', 261, 'Energetic');
''')
conn.commit()


# 3. Logika Rekomendasi Berdasarkan Genre, Mood, & Durasi
def recommend_smart_radio(main_artist, target_mood=None, max_duration_sec=None):
  cursor.execute(
      "SELECT genre FROM songs WHERE artist = ? LIMIT 1;", (main_artist,)
  )
  genre_res = cursor.fetchone()

  if not genre_res:
    print(f"Artis '{main_artist}' tidak ditemukan.\n")
    return

  main_genre = genre_res[0]

  query = """
        SELECT title, artist, duration_sec, mood 
        FROM songs 
        WHERE genre = ? AND artist != ?
    """
  params = [main_genre, main_artist]

  if target_mood:
    query += " AND mood = ?"
    params.append(target_mood)

  if max_duration_sec:
    query += " AND duration_sec <= ?"
    params.append(max_duration_sec)

  df_result = pd.read_sql_query(query, conn, params=params)

  print(f"📻 RADIO STATION: {main_artist}")
  print(f"   [Filter -> Genre: {main_genre}", end="")
  if target_mood:
    print(f" | Mood: {target_mood}", end="")
  if max_duration_sec:
    print(f" | Max Durasi: {max_duration_sec}s", end="")
  print("]")

  if not df_result.empty:
    print("   Rekomendasi Lagu:")
    for _, row in df_result.iterrows():
      mins, secs = divmod(row["duration_sec"], 60)
      print(
          f"   - {row['title']} by {row['artist']} ({mins}:{secs:02d}) [{row['mood']}]"
      )
  else:
    print("   (Tidak ada lagu yang cocok dengan filter ini)")
  print("\n" + "-" * 50 + "\n")


# 4. Eksekusi Simulasi
print("=" * 50)
print("       SPOTIFY SMART RECOMMENDATION SYSTEM        ")
print("=" * 50 + "\n")

recommend_smart_radio("LANY", target_mood="Chill")
recommend_smart_radio("Hindia", target_mood="Sad", max_duration_sec=240)
recommend_smart_radio("Justin Bieber")

conn.close()