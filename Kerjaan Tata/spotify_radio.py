import os
import sqlite3
import pandas as pd

# 1. Hubungkan ke database tata.db yang sama
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'tata.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. Reset & buat ulang data khusus daftar artis kamu
cursor.executescript('''
DROP TABLE IF EXISTS songs;

CREATE TABLE songs (
    song_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    genre TEXT
);

INSERT INTO songs (title, artist, genre) VALUES 
-- Pop
('Ghost', 'Justin Bieber', 'Pop'),
('Peaches', 'Justin Bieber', 'Pop'),
('vampire', 'Olivia Rodrigo', 'Pop'),
('drivers license', 'Olivia Rodrigo', 'Pop'),

-- Indie Pop
('ILYSB', 'LANY', 'Indie Pop'),
('dna', 'LANY', 'Indie Pop'),
('High School in Jakarta', 'NIKI', 'Indie Pop'),
('Every Summertime', 'NIKI', 'Indie Pop'),
('To the Bone', 'Pamungkas', 'Indie Pop'),
('Kenangan Manis', 'Pamungkas', 'Indie Pop'),
('Evaluasi', 'Hindia', 'Indie Pop'),
('Rumah Ke Rumah', 'Hindia', 'Indie Pop'),

-- Rock / Indie Rock
('Biarkan Tumbal Berganti', 'Perunggu', 'Rock'),
('33x', 'Perunggu', 'Rock');
''')
conn.commit()

# 3. Ambil daftar semua artis unik
artis_list = pd.read_sql_query(
    'SELECT DISTINCT artist FROM songs;', conn
)['artist'].tolist()


# 4. Fungsi membuat rekomendasi "Artist Radio" ala Spotify
def generate_recommendation_station(main_artist):
  query = f"""
    SELECT DISTINCT artist 
    FROM songs 
    WHERE genre IN (SELECT genre FROM songs WHERE artist = '{main_artist}')
      AND artist != '{main_artist}'
    LIMIT 3;
    """
  related_df = pd.read_sql_query(query, conn)
  related_artists = related_df['artist'].tolist()

  if related_artists:
    related_text = ", ".join(related_artists)
  else:
    related_text = "Artis Populer Lainnya"

  print(f"📻 RADIO STATION: {main_artist}")
  print(f"   With {related_text} and more\n")


# 5. Output Hasil
print("=" * 45)
print("       SPOTIFY RECOMMENDED STATIONS        ")
print("=" * 45 + "\n")

for artist in artis_list:
  generate_recommendation_station(artist)

conn.close()