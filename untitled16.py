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

# --- FUNGSI LOAD DATA KOMINFO ---
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

# --- FUNGSI LOAD DATA BKPSDM (PINTAR & DINAMIS) ---
def load_data_by_year(opd_folder, year):
    if not os.path.exists(opd_folder):
        return []
    
    files = [f for f in os.listdir(opd_folder) if f.endswith('.csv') and str(year) in f]
    
    data_list = []
    for file in files:
        path = os.path.join(opd_folder, file)
        try:
            # Aturan SKIPROWS Pintar berdasarkan Nama File
            skip_rows = 0
            if "Komposisi Instansi" in file:
                skip_rows = 2
            elif "Golongan Ruang" in file:
                skip_rows = 4
            elif "Pendidikan Formal" in file or "Tingkat Pendidikan" in file:
                skip_rows = 1
                
            df = pd.read_csv(path, skiprows=skip_rows, encoding='latin-1', on_bad_lines='skip')
            df = df.dropna(axis=1, how='all').dropna(how='all')
            data_list.append({"nama_file": file, "data": df})
        except Exception as e:
            st.error(f"❌ Gagal membaca file {file}: {e}")
            
    return data_list

# --- KONFIGURASI OPD ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bappelitbangda", "BPBD", 
        "Badan Pendapatan Daerah", "Badan Pengelola Perbatasan Daerah", 
        "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia"
    ],
    "DINAS": ["Dinas Komunikasi dan Informatika", "Dinas Kesehatan", "Dinas PUPR"],
    "KECAMATAN": ["Kecamatan Kota Atambua", "Kecamatan Atambua Barat"]
}

# --- SIDEBAR (Dibuat lebih awal agar variabel opd_select bisa digunakan) ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=70)
st.sidebar.title("Pusat Data Belu")
group_select = st.sidebar.selectbox("Pilih Kelompok:", list(opd_groups.keys()))
opd_select = st.sidebar.selectbox("Pilih OPD/Dinas:", opd_groups[group_select])

# --- HEADER ---
st.title(f"🏢 {opd_select}")

# ================== LOGIKA TAMPILAN (BKPSDM & OPD LAIN) ==================

if opd_select == "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia":
    
    st.subheader("👥 Dashboard Kepegawaian")
    
    # FILTER TAHUN (2020 - 2024)
    st.markdown('<div class="opd-card">', unsafe_allow_html=True)
    col_filter, _ = st.columns([1, 2])
    selected_year = col_filter.selectbox("Pilih Tahun Data:", [2020, 2021, 2022, 2023, 2024], index=0)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load data berdasarkan folder BKPSDM dan tahun yang dipilih
    data_items = load_data_by_year("BKPSDM", selected_year)
    
    if not data_items:
        st.warning(f"⚠️ Data untuk tahun {selected_year} belum tersedia di folder BKPSDM.")
        st.info("Pastikan file CSV memiliki angka tahun di dalam namanya (contoh: 'Data Pegawai... 2020.csv').")
    else:
        # Menampilkan data dalam Tab secara dinamis
        tab_names = [item['nama_file'].replace(".csv", "")[:30] + "..." if len(item['nama_file']) > 30 else item['nama_file'].replace(".csv", "") for item in data_items]
        tabs = st.tabs(tab_names)
        
        for i, item in enumerate(data_items):
            with tabs[i]:
                df = item['data']
                st.write(f"**Sumber File:** `{item['nama_file']}`")
                st.dataframe(df, use_container_width=True)
                
                # Visualisasi Otomatis Pintar
                num_cols = df.select_dtypes(include=['number']).columns.tolist()
                # Hindari membuat grafik dari kolom 'No.' atau '%'
                num_cols = [col for col in num_cols if 'no' not in col.lower() and '%' not in col.lower()]
                cat_cols = df.select_dtypes(include=['object']).columns.tolist()
                
                if len(num_cols) > 0 and len(cat_cols) > 0:
                    col_x = cat_cols[0]
                    col_y = num_cols[0]
                    
                    # Filter baris 'TOTAL' agar grafik tidak rusak
                    df_chart = df[~df[col_x].astype(str).str.contains("TOTAL", case=False, na=False)]
                    df_chart = df_chart.dropna(subset=[col_y]).head(20)
                    
                    fig = px.bar(df_chart, x=col_x, y=col_y, 
                                 title=f"Visualisasi: {col_x} vs {col_y}",
                                 color=col_y, color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True)

elif opd_select == "Dinas Komunikasi dan Informatika":
    st.subheader("📡 Dashboard Kominfo")
    st.info("Menampilkan data sarana prasarana dan internet.")
    
    asn, sarpras, internet, tower, duk = load_kominfo_data()
    if asn is not None:
        st.success("✅ Data Kominfo berhasil dimuat! Anda dapat menambahkan grafik Kominfo di sini.")
        # Jika Anda ingin memunculkan tabel kominfo, Anda bisa menambahkan st.dataframe(asn) dsb di sini.

else:
    st.markdown('<div class="opd-card">⚠️ Data untuk instansi ini belum diunggah ke sistem.</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption(f"Sumber: Data Sektoral Kabupaten Belu | OPD: {opd_select}")
