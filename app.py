import streamlit as st
import pandas as pd
import sqlite3

# ========================
# KONEKSI DATABASE (SQLITE)
# ========================
conn = sqlite3.connect("db_dinas.db", check_same_thread=False)

# ========================
# BUAT TABEL (JIKA BELUM ADA)
# ========================
conn.execute("""
CREATE TABLE IF NOT EXISTS dinas (
    id_dinas INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_dinas TEXT,
    alamat TEXT,
    kontak TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id_user INTEGER PRIMARY KEY AUTOINCREMENT,
    nama TEXT,
    username TEXT,
    password TEXT,
    role TEXT,
    id_dinas INTEGER
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS kategori_data (
    id_kategori INTEGER PRIMARY KEY AUTOINCREMENT,
    nama_kategori TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS data_laporan (
    id_laporan INTEGER PRIMARY KEY AUTOINCREMENT,
    id_dinas INTEGER,
    id_kategori INTEGER,
    tanggal TEXT,
    isi_data TEXT,
    status TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS log_aktivitas (
    id_log INTEGER PRIMARY KEY AUTOINCREMENT,
    id_user INTEGER,
    aktivitas TEXT,
    waktu TEXT
)
""")

conn.commit()

# ========================
# INSERT DATA DUMMY (JIKA KOSONG)
# ========================
cek = pd.read_sql("SELECT COUNT(*) as jumlah FROM dinas", conn)

if cek["jumlah"][0] == 0:
    conn.execute("""
    INSERT INTO dinas (nama_dinas, alamat, kontak)
    VALUES 
    ('Dinas Kominfo', 'Jl. Merdeka', '08123456789'),
    ('Dinas Pendidikan', 'Jl. Sekolah', '08234567890')
    """)

    conn.execute("""
    INSERT INTO users (nama, username, password, role, id_dinas)
    VALUES 
    ('Admin Kominfo', 'admin1', '123', 'admin', 1),
    ('User Kominfo', 'user1', '123', 'dinas', 1),
    ('Admin Pendidikan', 'admin2', '123', 'admin', 2)
    """)

    conn.execute("""
    INSERT INTO kategori_data (nama_kategori)
    VALUES ('Laporan Bulanan'), ('Laporan Tahunan')
    """)

    conn.commit()

# ========================
# LOAD DINAS
# ========================
df_dinas = pd.read_sql("SELECT * FROM dinas", conn)

st.title("📊 Dashboard Dinas")

# ========================
# 🔥 UPLOAD EXCEL
# ========================
st.subheader("📥 Upload Data Laporan")

uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])

if uploaded_file is not None:
    df_excel = pd.read_excel(uploaded_file)

    st.write("Preview Data:")
    st.dataframe(df_excel)

    # Validasi kolom
    required_cols = ["tanggal", "isi_data", "status"]
    if not all(col in df_excel.columns for col in required_cols):
        st.error("Kolom harus: tanggal, isi_data, status")
    else:
        # Pilih dinas
        dinas_option = st.selectbox("Pilih Dinas", df_dinas["nama_dinas"])
        id_dinas_upload = int(df_dinas[df_dinas["nama_dinas"] == dinas_option]["id_dinas"].values[0])

        # Ambil kategori
        df_kategori = pd.read_sql("SELECT * FROM kategori_data", conn)
        kategori_option = st.selectbox("Pilih Kategori", df_kategori["nama_kategori"])
        id_kategori_upload = int(df_kategori[df_kategori["nama_kategori"] == kategori_option]["id_kategori"].values[0])

        if st.button("Simpan Data"):
            for _, row in df_excel.iterrows():
                conn.execute("""
                INSERT INTO data_laporan (id_dinas, id_kategori, tanggal, isi_data, status)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    id_dinas_upload,
                    id_kategori_upload,
                    str(row["tanggal"]),
                    row["isi_data"],
                    row["status"]
                ))

            conn.commit()
            st.success("Data berhasil diupload!")

# ========================
# PILIH DINAS
# ========================
pilih_dinas = st.selectbox(
    "Pilih Dinas untuk Melihat Data",
    df_dinas["nama_dinas"]
)

dinas_terpilih = df_dinas[df_dinas["nama_dinas"] == pilih_dinas]
id_dinas = int(dinas_terpilih["id_dinas"].values[0])

# ========================
# DETAIL DINAS
# ========================
st.subheader("🏢 Detail Dinas")
st.write(dinas_terpilih)

# ========================
# USER DINAS
# ========================
df_user = pd.read_sql(
    f"SELECT * FROM users WHERE id_dinas = {id_dinas}", conn
)

st.subheader("👥 User Dinas")
st.metric("Jumlah User", len(df_user))
st.dataframe(df_user)

# ========================
# DATA LAPORAN
# ========================
query_laporan = f"""
SELECT 
    l.id_laporan,
    l.tanggal,
    k.nama_kategori,
    l.status,
    l.isi_data
FROM data_laporan l
JOIN kategori_data k ON l.id_kategori = k.id_kategori
WHERE l.id_dinas = {id_dinas}
"""

df_laporan = pd.read_sql(query_laporan, conn)

st.subheader("📄 Data Laporan")
st.metric("Jumlah Laporan", len(df_laporan))
st.dataframe(df_laporan)

# ========================
# GRAFIK
# ========================
if not df_laporan.empty:
    st.subheader("📊 Statistik Status Laporan")
    st.bar_chart(df_laporan["status"].value_counts())

# ========================
# LOG AKTIVITAS
# ========================
query_log = f"""
SELECT l.aktivitas, l.waktu, u.nama
FROM log_aktivitas l
JOIN users u ON l.id_user = u.id_user
WHERE u.id_dinas = {id_dinas}
ORDER BY l.waktu DESC
LIMIT 10
"""

df_log = pd.read_sql(query_log, conn)

st.subheader("📝 Log Aktivitas")
st.dataframe(df_log)
