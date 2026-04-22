import streamlit as st
import pandas as pd
import mysql.connector

# ========================
# KONEKSI DATABASE
# ========================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="08102005",
    database="db_dinas"
)

# ========================
# LOAD DINAS
# ========================
df_dinas = pd.read_sql("SELECT * FROM dinas", conn)

st.title("📊 Dashboard Dinas")

# ========================
# PILIH DINAS
# ========================
pilih_dinas = st.selectbox(
    "Pilih Dinas",
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
# DATA LAPORAN (JOIN)
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
# GRAFIK STATUS
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
