import streamlit as st
import pandas as pd
import mysql.connector

# ========================
# KONFIGURASI DATABASE
# ========================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="db_dinas"
)

# ========================
# LOAD DATA DINAS
# ========================
query_dinas = "SELECT * FROM dinas"
df_dinas = pd.read_sql(query_dinas, conn)

# ========================
# UI DASHBOARD
# ========================
st.set_page_config(page_title="Dashboard Dinas", layout="wide")

st.title("📊 Dashboard Data Dinas")

# ========================
# PILIH DINAS
# ========================
pilih_dinas = st.selectbox(
    "Pilih Dinas",
    df_dinas["nama_dinas"]
)

# Ambil data dinas terpilih
dinas_terpilih = df_dinas[df_dinas["nama_dinas"] == pilih_dinas]
id_dinas = int(dinas_terpilih["id_dinas"].values[0])

# ========================
# DETAIL DINAS
# ========================
st.subheader("🏢 Detail Dinas")

col1, col2 = st.columns(2)

with col1:
    st.write("**Nama Dinas:**", dinas_terpilih["nama_dinas"].values[0])
    st.write("**Alamat:**", dinas_terpilih["alamat"].values[0])

with col2:
    st.write("**Kontak:**", dinas_terpilih["kontak"].values[0])

# ========================
# DATA USER
# ========================
query_user = f"""
SELECT * FROM users WHERE id_dinas = {id_dinas}
"""
df_user = pd.read_sql(query_user, conn)

st.subheader("👥 Data User")

# METRIK
st.metric("Jumlah User", len(df_user))

# TABEL
st.dataframe(df_user, use_container_width=True)

# ========================
# OPTIONAL: FILTER ROLE
# ========================
if not df_user.empty:
    role_filter = st.selectbox("Filter Role", ["Semua"] + list(df_user["role"].unique()))

    if role_filter != "Semua":
        df_user = df_user[df_user["role"] == role_filter]

    st.write("### Data Setelah Filter")
    st.dataframe(df_user, use_container_width=True)
