import os
import sqlite3
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

# 1. Konfigurasi Halaman Web
st.set_page_config(
    page_title="Spotify Super Dashboard", page_icon="🎵", layout="wide"
)

# 🎨 CUSTOM CSS: TEMA DARK MODE KHAS SPOTIFY
st.markdown(
    """
    <style>
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #000000;
    }
    .stButton>button {
        background-color: #1DB954;
        color: white;
        border-radius: 20px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #1ed760;
        color: white;
    }
    hr {
        border-color: #282828;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎵 Spotify Recommendation System (NLP + TF-IDF)")

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, "tata.db")


def get_connection():
  return sqlite3.connect(db_path)


# 2. Inisialisasi Database & Tabel
conn = get_connection()
cursor = conn.cursor()

try:
  cursor.execute("ALTER TABLE songs ADD COLUMN bpm INTEGER DEFAULT 120;")
  cursor.execute(
      "UPDATE songs SET bpm = 115 WHERE genre = 'Pop' OR genre = 'Indie Pop';"
  )
  cursor.execute("UPDATE songs SET bpm = 135 WHERE genre = 'Rock';")
  conn.commit()
except sqlite3.OperationalError:
  pass

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER,
    played_at TEXT,
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS favorites (
    fav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER UNIQUE,
    added_at TEXT,
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_name TEXT,
    song_id INTEGER,
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);
""")
conn.commit()

# Navigasi Sidebar
menu = st.sidebar.radio(
    "🧭 Navigasi Utama",
    [
        "📻 Artist Radio & TF-IDF ML",
        "🔎 Cari Lagu",
        "🎶 Playlist Saya",
        "⭐ Lagu Favorit",
        "📜 Riwayat Pemutaran",
        "📊 Dasbor Analitik",
    ],
)

SAMPLE_AUDIO_URL = (
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
)

# ==========================================
# 🤖 FITUR 1: ARTIST RADIO + TF-IDF NLP ML
# ==========================================
if menu == "📻 Artist Radio & TF-IDF ML":
  st.subheader(
      "🤖 Rekomendasi Pintar (NLP TF-IDF pada Genre, Mood & Meta-Data)"
  )

  df_artists = pd.read_sql_query(
      "SELECT DISTINCT artist FROM songs ORDER BY artist ASC;", conn
  )
  artist_list = df_artists["artist"].tolist()

  col_a, col_b = st.columns(2)
  with col_a:
    selected_artist = st.selectbox("Pilih Artis Acuan:", artist_list)
  with col_b:
    max_dur = st.slider("Durasi Maksimal (detik):", 120, 400, 300, 10)

  # Ambil seluruh lagu dari DB
  query = (
      "SELECT song_id, title, artist, genre, duration_sec, mood, bpm FROM songs"
  )
  df_all = pd.read_sql_query(query, conn)

  # 1. Cari data lagu acuan dari artis yang dipilih
  target_song = df_all[df_all["artist"] == selected_artist].iloc[0]
  st.write(
      f"**Artis Acuan:** `{target_song['artist']}` | **Genre:**"
      f" `{target_song['genre']}` | **Mood:** `{target_song['mood']}`"
  )

  # Filter lagu yang bukan dari artis acuan dan masuk durasi
  df_candidates = df_all[
      (df_all["artist"] != selected_artist)
      & (df_all["duration_sec"] <= max_dur)
  ].copy()

  st.divider()

  if not df_candidates.empty:
    # 2. IMPLEMENTASI NLP (TF-IDF Vectorizer)
    # Gabungkan Genre + Mood menjadi teks fitur
    df_all["text_features"] = df_all["genre"] + " " + df_all["mood"]

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df_all["text_features"])

    # Hitung Cosine Similarity berbasis TF-IDF
    target_idx = target_song.name
    cosine_sim_matrix = cosine_similarity(tfidf_matrix[target_idx], tfidf_matrix)

    # Masukkan skor TF-IDF ke dataframe kandidat
    scores = [
        round(cosine_sim_matrix[0][i] * 100, 1) for i in df_candidates.index
    ]
    df_candidates["Skor TF-IDF (%)"] = scores

    # Urutkan berdasarkan skor TF-IDF tertinggi
    df_candidates = df_candidates.sort_values(
        by="Skor TF-IDF (%)", ascending=False
    )

    st.success(
        f"Ditemukan {len(df_candidates)} lagu rekomendasi berbasis TF-IDF!"
    )

    for _, row in df_candidates.iterrows():
      mins, secs = divmod(row["duration_sec"], 60)
      c1, c2, c3, c4 = st.columns([3, 2, 1, 1])

      with c1:
        st.markdown(f"**{row['title']}**")
        st.caption(f"Artis: {row['artist']} | Genre: {row['genre']}")
      with c2:
        st.write(f"🎭 **{row['mood']}** (`{mins}:{secs:02d}`)")
        st.caption(f"🧠 Kemiripan TF-IDF: **{row['Skor TF-IDF (%)']}%**")
      with c3:
        if st.button("▶️ Putar", key=f"play_{row['song_id']}"):
          now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          cursor.execute(
              "INSERT INTO history (song_id, played_at) VALUES (?, ?);",
              (row["song_id"], now),
          )
          conn.commit()
          st.session_state["now_playing"] = (
              f"{row['title']} - {row['artist']}"
          )
          st.rerun()
      with c4:
        if st.button("❤️ Suka", key=f"fav_{row['song_id']}"):
          now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
          try:
            cursor.execute(
                "INSERT INTO favorites (song_id, added_at) VALUES (?, ?);",
                (row["song_id"], now),
            )
            conn.commit()
            st.toast(f"Disimpan ke Favorit: {row['title']}")
          except sqlite3.IntegrityError:
            st.toast("Lagu ini sudah ada di Favorit!")
      st.divider()
  else:
    st.warning("Tidak ada lagu yang cocok dengan kriteria filter.")

# Pemutar Audio Permanen di Sidebar
if "now_playing" in st.session_state:
  st.sidebar.markdown("---")
  st.sidebar.markdown(
      f"🎧 **Sedang Diputar:**\n`{st.session_state['now_playing']}`"
  )
  st.sidebar.audio(SAMPLE_AUDIO_URL)

# ==========================================
# 🔎 FITUR 2: SEARCH BAR
# ==========================================
elif menu == "🔎 Cari Lagu":
  st.subheader("🔎 Cari Lagu atau Artis")
  search_query = st.text_input("Ketik judul lagu atau nama artis:")

  if search_query:
    search_sql = """
            SELECT song_id, title, artist, genre, mood, duration_sec 
            FROM songs 
            WHERE title LIKE ? OR artist LIKE ?
        """
    param = f"%{search_query}%"
    df_search = pd.read_sql_query(search_sql, conn, params=[param, param])

    if not df_search.empty:
      st.dataframe(df_search, use_container_width=True)
    else:
      st.warning("Lagu atau artis tidak ditemukan.")

# ==========================================
# 🎶 FITUR 3: PLAYLIST MANAGEMENT
# ==========================================
elif menu == "🎶 Playlist Saya":
  st.subheader("🎶 Kelola Playlist Pribadi")

  col_p1, col_p2 = st.columns(2)
  with col_p1:
    pl_name = st.text_input("Buat Playlist Baru:")
    df_all_songs = pd.read_sql_query("SELECT song_id, title FROM songs;", conn)
    song_options = {
        row["title"]: row["song_id"] for _, row in df_all_songs.iterrows()
    }
    selected_song_title = st.selectbox(
        "Pilih Lagu untuk Ditambahkan:", list(song_options.keys())
    )

    if st.button("➕ Tambah ke Playlist"):
      if pl_name.strip():
        song_id = song_options[selected_song_title]
        cursor.execute(
            "INSERT INTO playlists (playlist_name, song_id) VALUES (?, ?);",
            (pl_name, song_id),
        )
        conn.commit()
        st.success(
            f"Berhasil menambahkan '{selected_song_title}' ke playlist"
            f" '{pl_name}'!"
        )
      else:
        st.error("Nama playlist tidak boleh kosong!")

  with col_p2:
    st.markdown("##### 📜 Daftar Playlist")
    df_pl = pd.read_sql_query(
        """
            SELECT p.playlist_name AS 'Nama Playlist', s.title AS 'Judul Lagu', s.artist AS 'Artis'
            FROM playlists p
            JOIN songs s ON p.song_id = s.song_id
        """,
        conn,
    )
    if not df_pl.empty:
      st.dataframe(df_pl, use_container_width=True)
    else:
      st.info("Belum ada playlist yang dibuat.")

# ==========================================
# ⭐ FITUR 4: LAGU FAVORIT
# ==========================================
elif menu == "⭐ Lagu Favorit":
  st.subheader("⭐ Daftar Lagu Favorit Saya")

  fav_query = """
        SELECT f.fav_id AS 'ID', s.title AS 'Judul Lagu', s.artist AS 'Artis', s.genre AS 'Genre', s.mood AS 'Mood', f.added_at AS 'Ditambahkan Pada'
        FROM favorites f
        JOIN songs s ON f.song_id = s.song_id
        ORDER BY f.added_at DESC
    """
  df_fav = pd.read_sql_query(fav_query, conn)

  if not df_fav.empty:
    st.dataframe(df_fav, use_container_width=True)
    if st.button("🗑️ Kosongkan Favorit", key="clear_fav_btn"):
      cursor.execute("DELETE FROM favorites;")
      conn.commit()
      st.rerun()
  else:
    st.info("Belum ada lagu favorit.")

# ==========================================
# 📜 FITUR 5: RIWAYAT & UNDUH CSV
# ==========================================
elif menu == "📜 Riwayat Pemutaran":
  st.subheader("📜 Riwayat Lagu yang Diputar")

  hist_query = """
        SELECT h.history_id AS 'ID', s.title AS 'Judul Lagu', s.artist AS 'Artis', s.genre AS 'Genre', h.played_at AS 'Waktu Diputar'
        FROM history h
        JOIN songs s ON h.song_id = s.song_id
        ORDER BY h.played_at DESC
    """
  df_hist = pd.read_sql_query(hist_query, conn)

  if not df_hist.empty:
    st.dataframe(df_hist, use_container_width=True)

    col1, col2 = st.columns([1, 4])
    with col1:
      csv_data = df_hist.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="📥 Unduh CSV",
          data=csv_data,
          file_name="riwayat_spotify.csv",
          mime="text/csv",
          key="download_csv_btn",
      )
    with col2:
      if st.button("🗑️ Hapus Semua Riwayat", key="clear_hist_btn"):
        cursor.execute("DELETE FROM history;")
        conn.commit()
        st.rerun()
  else:
    st.info("Belum ada riwayat lagu yang diputar.")

# ==========================================
# 📊 FITUR 6: ANALYTICS DASHBOARD
# ==========================================
elif menu == "📊 Dasbor Analitik":
  st.subheader("📊 Analisis Data Streaming Spotify")

  col1, col2 = st.columns(2)

  with col1:
    st.markdown("##### 🥧 Sebaran Genre Lagu (Pie Chart)")
    df_genre_count = pd.read_sql_query(
        "SELECT genre, COUNT(*) as jumlah FROM songs GROUP BY genre;", conn
    )
    fig_pie = px.pie(
        df_genre_count,
        values="jumlah",
        names="genre",
        title="Persentase Genre Lagu",
        hole=0.3,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

  with col2:
    st.markdown("##### 🔥 Top Lagu Paling Sering Diputar (Most Played)")
    top_play_query = """
            SELECT s.title AS 'Judul Lagu', COUNT(h.history_id) AS 'Diputar'
            FROM history h
            JOIN songs s ON h.song_id = s.song_id
            GROUP BY s.song_id
            ORDER BY Diputar DESC
            LIMIT 5;
        """
    df_top = pd.read_sql_query(top_play_query, conn)
    if not df_top.empty:
      fig_bar = px.bar(
          df_top,
          x="Judul Lagu",
          y="Diputar",
          text="Diputar",
          title="5 Lagu Teratas",
          color="Diputar",
      )
      st.plotly_chart(fig_bar, use_container_width=True)
    else:
      st.info("Putar beberapa lagu terlebih dahulu!")

conn.close()