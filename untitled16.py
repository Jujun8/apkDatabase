import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Informasi Data Sektoral Belu", layout="wide", page_icon="🏢")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #F8FAFC; }
    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #f1f5f9 !important;
    }
    .opd-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        border-left: 5px solid #6366F1;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA KOMINFO ---
def load_kominfo_data():
    try:
        base_path = "KOMINFO"
        def read_csv_safe(filename):
            path = os.path.join(base_path, filename)
            if not os.path.exists(path): return None
            try:
                return pd.read_csv(path, encoding='latin-1')
            except:
                return pd.read_csv(path)

        asn = read_csv_safe("ASN-Berpendidikan-TIK.csv")
        sarpras = read_csv_safe("Data-Sarana-dan-Prasarana-Diskominfo.csv")
        internet = read_csv_safe("Data-Internet-OPD-Beserta-Kapasitasnya-.csv")
        tower = read_csv_safe("DATA-TOWER.csv")
        duk = read_csv_safe("DUK-KOMINFO-Upload.csv")
        return asn, sarpras, internet, tower, duk
    except:
        return None, None, None, None, None

# --- LOAD DATA BKPSDM (TAHUN 2020) ---
def load_bkpsdm_data():
    try:
        base_path = "BKPSDM"
        
        # Fungsi khusus membaca CSV dengan melompati baris judul atas agar header tabel terbaca benar
        def read_bkpsdm_csv(filename, skip=0):
            path = os.path.join(base_path, filename)
            if not os.path.exists(path):
                return None
            return pd.read_csv(path, skiprows=skip, encoding='latin-1')

        # Membaca file spesifik tahun 2020 yang Anda berikan
        # skiprows disesuaikan dengan struktur file CSV yang biasanya memiliki judul di baris 1-2
        instansi_2020 = read_csv_safe("Data Pegawai Berdasarkan Komposisi Instansi di Kabupaten Belu Tahun 2020.csv", skip=2)
        golongan_2020 = read_csv_safe("Data Pegawai Berdasarkan Golongan Ruang di Kabupaten Belu Tahun 2020.csv", skip=1)

        return instansi_2020, golongan_2020
    except Exception as e:
        st.error(f"❌ Gagal memuat data BKPSDM: {e}")
        return None, None

# --- KONFIGURASI OPD ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bappelitbangda", "BPBD", 
        "Badan Pendapatan Daerah", "Badan Pengelola Perbatasan Daerah", 
        "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia"
    ],
    "DINAS": ["Dinas Komunikasi dan Informatika", "Dinas Kesehatan", "Dinas PUPR"], # ... dst
    "KECAMATAN": ["Kecamatan Kota Atambua", "Kecamatan Atambua Barat"] # ... dst
}

# --- SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=70)
st.sidebar.title("Pusat Data Belu")
group_select = st.sidebar.selectbox("Pilih Kelompok:", list(opd_groups.keys()))
opd_select = st.sidebar.selectbox("Pilih OPD/Dinas:", opd_groups[group_select])

# --- HEADER ---
st.title(f"🏢 {opd_select}")

# ================== LOGIKA TAMPILAN ==================

if opd_select == "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia":
    st.subheader("👥 Data Kepegawaian Tahun 2020")
    
    instansi, golongan = load_bkpsdm_data()

    if instansi is not None and golongan is not None:
        # Menghitung Total Pegawai (contoh KPI)
        total_pegawai = 0
        if 'Jumlah' in instansi.columns:
            total_pegawai = pd.to_numeric(instansi['Jumlah'], errors='coerce').sum()

        c1, c2 = st.columns(2)
        c1.metric("Total Pegawai (2020)", f"{int(total_pegawai)} Orang")
        c2.metric("Tahun Data", "2020")

        st.markdown("---")
        tab1, tab2 = st.tabs(["Komposisi per Instansi", "Berdasarkan Golongan"])

        with tab1:
            st.write("### Data Pegawai per Urusan/Instansi")
            st.dataframe(instansi, use_container_width=True)
            
            # Visualisasi jika kolom yang diperlukan ada
            if 'Urusan/Instansi' in instansi.columns and 'Jumlah' in instansi.columns:
                df_chart = instansi.dropna(subset=['Jumlah']).head(15) # Ambil 15 teratas
                fig = px.bar(df_chart, x='Urusan/Instansi', y='Jumlah', title="Top 15 Instansi Berdasarkan Jumlah Pegawai")
                st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.write("### Data Pegawai per Golongan Ruang")
            st.dataframe(golongan, use_container_width=True)
            st.info("Catatan: Data golongan mencakup tenaga teknis dan guru.")
    else:
        st.warning("⚠️ File CSV Tahun 2020 untuk BKPSDM tidak ditemukan di folder 'BKPSDM'.")

elif opd_select == "Dinas Komunikasi dan Informatika":
    st.subheader("📡 Dashboard Kominfo")
    # ... (Logika Kominfo tetap sama seperti sebelumnya)
    st.info("Menampilkan data sarana prasarana dan internet.")

else:
    st.markdown('<div class="opd-card">⚠️ Data untuk instansi ini belum diunggah ke sistem.</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption(f"Sumber: Data Sektoral Kabupaten Belu | OPD: {opd_select}")
