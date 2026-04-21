import streamlit as st
import pandas as pd
import sqlite3
import os
import re

# --- KONFIGURASI DATABASE ---
DB_NAME = "database_dinas.db"

# --- INIT DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.close()

# --- VALIDASI NAMA TABEL ---
def clean_table_name(name):
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9_]', '_', name)  # ganti karakter aneh
    return name

# --- SIMPAN KE DATABASE ---
def save_to_db(df, table_name):
    try:
        conn = sqlite3.connect(DB_NAME)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error simpan data: {e}")
        return False

# --- UI STREAMLIT ---
st.set_page_config(page_title="Data Center Dinas", layout="wide")

st.title("📂 Sistem Upload Data Dinas")
st.write("Gunakan aplikasi ini untuk mengunggah data sektoral ke database pusat.")

# Sidebar
menu = st.sidebar.selectbox("Menu", ["Upload Data", "Lihat Database"])

init_db()

# ==============================
# MENU UPLOAD DATA
# ==============================
if menu == "Upload Data":
    st.header("Upload File (CSV atau Excel)")
    
    nama_dinas = st.text_input("Nama Dinas / Nama Tabel", "dinas_kesehatan")
    uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # 🔥 HANDLE CSV & EXCEL + ERROR
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    df = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("Preview Data")
            st.dataframe(df.head())

            # INFO tambahan
            st.write("Jumlah baris:", df.shape[0])
            st.write("Jumlah kolom:", df.shape[1])

            if st.button("Simpan ke Database"):
                if nama_dinas:
                    table_name = clean_table_name(nama_dinas)

                    sukses = save_to_db(df, table_name)
                    if sukses:
                        st.success(f"✅ Data berhasil disimpan ke tabel: {table_name}")
                else:
                    st.warning("Mohon isi nama dinas.")

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")

# ==============================
# MENU LIHAT DATABASE
# ==============================
elif menu == "Lihat Database":
    st.header("Isi Database Saat Ini")

    conn = sqlite3.connect(DB_NAME)

    try:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

        if not tables.empty:
            selected_table = st.selectbox("Pilih Tabel", tables['name'])

            if selected_table:
                try:
                    data_db = pd.read_sql(f"SELECT * FROM `{selected_table}`", conn)
                    st.dataframe(data_db)

                    # Tombol hapus tabel
                    if st.button("🗑️ Hapus Tabel Ini"):
                        conn.execute(f"DROP TABLE `{selected_table}`")
                        conn.commit()
                        st.success("Tabel berhasil dihapus")
                        st.rerun()

                except Exception as e:
                    st.error(f"Gagal membaca tabel: {e}")

        else:
            st.info("Belum ada data di database.")

    except Exception as e:
        st.error(f"Error database: {e}")

    conn.close()
