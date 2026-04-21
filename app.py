import streamlit as st
import pandas as pd
import sqlite3
import os

# --- KONFIGURASI DATABASE ---
DB_NAME = "database_dinas.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.close()

def save_to_db(df, table_name):
    try:
        conn = sqlite3.connect(DB_NAME)
        # Append data jika tabel sudah ada, buat baru jika belum
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# --- UI STREAMLIT ---
st.set_page_config(page_title="Data Center Dinas", layout="wide")

st.title("📂 Sistem Upload Data Dinas")
st.write("Gunakan aplikasi ini untuk mengunggah data sektoral ke database pusat.")

# Sidebar untuk menu
menu = st.sidebar.selectbox("Menu", ["Upload Data", "Lihat Database"])

init_db()

if menu == "Upload Data":
    st.header("Upload File (CSV atau Excel)")
    
    # Input Nama Dinas/Tabel
    nama_dinas = st.text_input("Nama Dinas / Nama Tabel (Tanpa Spasi)", "dinas_kesehatan")
    
    uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        # Membaca file berdasarkan format
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Preview Data")
        st.dataframe(df.head())

        if st.button("Simpan ke Database"):
            if nama_dinas:
                sukses = save_to_db(df, nama_dinas.lower())
                if sukses:
                    st.success(f"Data berhasil disimpan ke tabel: {nama_dinas}")
            else:
                st.warning("Mohon isi nama dinas terlebih dahulu.")

elif menu == "Lihat Database":
    st.header("Isi Database Saat Ini")
    
    conn = sqlite3.connect(DB_NAME)
    # Cek tabel yang ada di SQLite
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
    
    if not tables.empty:
        selected_table = st.selectbox("Pilih Tabel untuk Dilihat", tables['name'])
        
        if selected_table:
            data_db = pd.read_sql(f"SELECT * FROM {selected_table}", conn)
            st.dataframe(data_db)
            
            # Fitur hapus data (opsional)
            if st.button("Kosongkan Tabel Ini"):
                conn.execute(f"DROP TABLE {selected_table}")
                st.rerun()
    else:
        st.info("Belum ada data di database.")
    
    conn.close()
