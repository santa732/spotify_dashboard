import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. Jalur folder tempat skrip ini berada
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'tata.db')
sql_script_path = os.path.join(base_dir, 'Script week4.sql')

# Jika nama file script kamu tidak ada ekstensi .sql, gunakan baris di bawah ini:
if not os.path.exists(sql_script_path):
  sql_script_path = os.path.join(base_dir, 'Script week4')

conn = sqlite3.connect(db_path)

# 2. Eksekusi file SQL untuk mengisi database jika masih kosong
with open(sql_script_path, 'r', encoding='utf-8') as sql_file:
  sql_script = sql_file.read()

cursor = conn.cursor()
cursor.executescript(sql_script)
conn.commit()

# 3. Kueri SQL untuk Visualisasi
query_artist = """
SELECT artist, COUNT(*) AS total_lagu 
FROM songs 
GROUP BY artist 
ORDER BY total_lagu DESC 
LIMIT 5;
"""

query_genre = """
SELECT genre, COUNT(*) AS total_lagu 
FROM songs 
GROUP BY genre 
ORDER BY total_lagu DESC;
"""

df_artist = pd.read_sql_query(query_artist, conn)
df_genre = pd.read_sql_query(query_genre, conn)

conn.close()

# 4. Tampilkan Grafik Visualisasi
sns.set_theme(style='darkgrid')
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Bar Chart Artis
sns.barplot(
    data=df_artist, x='total_lagu', y='artist', ax=axes[0], palette='viridis'
)
axes[0].set_title('Top 5 Artis Terbanyak', fontsize=12, fontweight='bold')
axes[0].set_xlabel('Jumlah Lagu')

# Pie Chart Genre
axes[1].pie(
    df_genre['total_lagu'],
    labels=df_genre['genre'],
    autopct='%1.1f%%',
    colors=sns.color_palette('pastel'),
)
axes[1].set_title('Persentase Genre Lagu', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()