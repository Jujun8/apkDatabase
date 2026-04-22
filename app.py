import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup
import random

# --- CONFIG DASHBOARD ---
st.set_page_config(page_title="Dashboard OPD Kabupaten Belu", layout="wide")

# --- 1. FUNGSI AMBIL DATA OTOMATIS (WEB SCRAPER) ---
# Di sini Anda bisa memasukkan URL website resmi dinas terkait
@st.cache_data(ttl=3600) # Data disimpan di cache selama 1 jam agar tidak lambat
def fetch_data_from_web():
    # Ini adalah simulasi. Jika ada website asli, ganti URL di bawah ini
    # Contoh: response = requests.get("https://belukab.go.id/data-opd")
    
    opd_names = [
        "Sekretariat DPRD", "Inspektorat Daerah", "DLH & Perhubungan", 
        "Dinas Peternakan & Perikanan", "Kesbangpol", "BPKAD", "Bagian Hukum",
        "Dispendukcapil", "Disparbud", "Bapenda", "Bappelitbangda", 
        "RSUD Mgr. Gabriel Manek", "Diskominfo", "PUPR", "Dinas Kesehatan",
        "Kecamatan Atambua Barat", "Kecamatan Kota Atambua"
    ]
    
    # Simulasi data yang ditarik dari web
    rows = []
    for name in opd_names:
        rows.append({
            "OPD": name,
            "Anggaran": random.randint(500, 2000), # Juta Rupiah
            "Realisasi (%)": random.randint(40, 95),
            "Program": random.randint(5, 20),
            "Status": random.choice(["Aktif", "Selesai", "Proses"])
        })
    return pd.DataFrame(rows)

# Load Data
df = fetch_data_from_web()

# --- 2. TAMPILAN SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=80)
st.sidebar.title("Filter Data OPD")
st.sidebar.markdown("Pilih dinas untuk melihat detail")

selected_opd = st.sidebar.selectbox("Cari OPD/Dinas:", ["SEMUA OPD"] + list(df['OPD'].unique()))

# --- 3. MAIN DASHBOARD ---
if selected_opd == "SEMUA OPD":
    st.title("📊 Dashboard Utama Semua OPD")
    st.info("Menampilkan ringkasan data otomatis dari website dinas Kabupaten Belu.")
    
    # Baris Metric Utama
    m1, m2, m3 = st.columns(3)
    m1.metric("Total OPD Pantauan", len(df))
    m2.metric("Rata-rata Realisasi", f"{round(df['Realisasi (%)'].mean(), 1)}%")
    m3.metric("Total Program", df['Program'].sum())

    # Grafik Perbandingan
    st.markdown("### Perbandingan Realisasi Anggaran")
    fig = px.bar(df, x='OPD', y='Realisasi (%)', color='Realisasi (%)',
                 color_continuous_scale='Blues', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabel Seluruh Data
    st.markdown("### Data Lengkap")
    st.dataframe(df, use_container_width=True)

else:
    # --- 4. TAMPILAN DETAIL PER DINAS ---
    data_detail = df[df['OPD'] == selected_opd].iloc[0]
    
    st.title(f"🏢 Detail: {selected_opd}")
    st.success(f"Menampilkan data terkini untuk {selected_opd}")

    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.subheader("Informasi Kunci")
        st.write(f"**Total Anggaran:** Rp {data_detail['Anggaran']} Juta")
        st.write(f"**Realisasi:** {data_detail['Realisasi (%)']}%")
        st.write(f"**Jumlah Program:** {data_detail['Program']}")
        st.write(f"**Status Saat Ini:** {data_detail['Status']}")
        
        # Grafik Gauge sederhana
        fig_gauge = px.pie(values=[data_detail['Realisasi (%)'], 100-data_detail['Realisasi (%)']], 
                           names=['Realisasi', 'Sisa'], hole=0.7,
                           color_discrete_sequence=['#1f77b4', '#e5ecf6'])
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_b:
        st.subheader("Grafik Capaian")
        # Contoh grafik batang tambahan untuk detail
        detail_chart = px.bar(x=["Program", "Target", "Capaian"], 
                             y=[data_detail['Program'], 100, data_detail['Realisasi (%)']],
                             title="Statistik Kinerja")
        st.plotly_chart(detail_chart, use_container_width=True)

# Footer
st.markdown("---")
st.caption("Data diperbarui secara otomatis dari sistem OPD Belu.")
