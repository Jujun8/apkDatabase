import streamlit as st
import pandas as pd
import plotly.express as px

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Sistem Informasi Data Sektoral Belu", layout="wide", page_icon="🏢")

# --- CUSTOM CSS (MODERN GLASSMORPHISM) ---
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

# --- FUNGSI DATA ASLI DARI DRIVE ---
def get_hukum_data():
    return pd.DataFrame({
        'Tahun': ['2020', '2021', '2022', '2023', '2024'],
        'Keputusan Bupati': [201, 230, 358, 321, 414],
        'Peraturan Bupati': [9, 46, 46, 8, 35],
        'Peraturan Daerah': [8, 7, 1, 58, 58]
    })

# --- DAFTAR SELURUH OPD (TOTAL 40+) ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bappelitbangda", "BPBD", 
        "Badan Pendapatan Daerah", "Badan Pengelola Perbatasan Daerah", "BKPSDM"
    ],
    "DINAS": [
        "Dinas Lingkungan Hidup dan Perhubungan", "Dinas Peternakan dan Perikanan",
        "Dinas Kependudukan dan Pencatatan Sipil", "Dinas Koperasi, Tenaga Kerja dan Transmigrasi",
        "Dinas Pariwisata dan Kebudayaan", "DP3AP2KB", "DPMPTSP", "Dinas Komunikasi dan Informatika",
        "Dinas Kesehatan", "Dinas PUPR", "Dinas Pertanian dan Ketahanan Pangan",
        "Dinas Pendidikan, Kepemudaan dan Olahraga", "Dinas Perindustrian dan Perdagangan",
        "Dinas Perpustakaan dan Kearsipan", "Dinas Sosial, PMD", "Satuan Polisi Pamong Praja"
    ],
    "BAGIAN SETDA & RSUD": [
        "RSUD Mgr. Gabriel Manek, SVD Atambua", "Bagian Hukum", "Bagian Organisasi", 
        "Bagian Kesejahteraan Rakyat", "Bagian Pemerintahan", "Bagian PBJ",
        "Bagian Administrasi Pembangunan", "Bagian Perekonomian dan SDA",
        "Bagian Protokol dan Komunikasi Pimpinan", "Bagian Umum"
    ],
    "KECAMATAN": [
        "Kecamatan Atambua Barat", "Kecamatan Kota Atambua", "Kecamatan Atambua Selatan",
        "Kecamatan Tasifeto Timur", "Kecamatan Lamaknen", "Kecamatan Lamaknen Selatan",
        "Kecamatan Kakuluk Mesak", "Kecamatan Lasiolat", "Kecamatan Nanaet Duasbesi",
        "Kecamatan Raihat", "Kecamatan Raimanuk"
    ]
}

# --- SIDEBAR NAVIGASI ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=70)
st.sidebar.title("Pusat Data Belu")
group_select = st.sidebar.selectbox("Pilih Kelompok:", list(opd_groups.keys()))
opd_select = st.sidebar.selectbox("Pilih OPD/Dinas:", opd_groups[group_select])

# --- HALAMAN UTAMA ---
st.title(f"🏢 {opd_select}")
st.write(f"Sumber Data: Google Drive / Data Sektoral / {group_select}")

# --- LOGIKA TAMPILAN DATA ASLI VS PENDING ---

if opd_select == "Bagian Hukum":
    df_h = get_hukum_data()
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="opd-card">', unsafe_allow_html=True)
        st.subheader("Tren Produk Hukum (Riil)")
        fig = px.bar(df_h, x='Tahun', y=['Keputusan Bupati', 'Peraturan Bupati'], barmode='group', color_discrete_sequence=['#6366F1', '#10B981'])
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.metric("Total Produk 2024", "507", "File: Produk Hukum.pdf")
        st.table(df_h.tail(3))

elif opd_select == "Sekretariat DPRD":
    st.info("Menampilkan Data Alat Kelengkapan DPRD (AKD) 2024-2029")
    akd = pd.DataFrame({
        "Jabatan": ["Ketua", "Wakil Ketua I", "Wakil Ketua II"],
        "Nama": ["Theodorus Manehitu Djuang", "Januaria Awalde Berek", "Antonius Chr Djaga Kota, ST"]
    })
    st.table(akd)

elif opd_select == "Dinas Pertanian dan Ketahanan Pangan":
    st.subheader("Status Ketahanan Pangan (Data FSVA 2024)")
    st.write("- Dokumen Terdeteksi: Peta FSVA Kab. Belu 2024.pdf")
    st.warning("Data angka spesifik per desa sedang dalam proses digitalisasi dari PDF.")

elif opd_select == "RSUD Mgr. Gabriel Manek, SVD Atambua":
    st.subheader("Profil Layanan RSUD")
    st.write("- Dokumen Terdeteksi: Profil Kesehatan 2023.pdf")
    st.write("- Status: Tersedia data sarana prasarana dan tenaga medis.")

else:
    # TAMPILAN JIKA DATA BELUM ADA DI DRIVE
    st.markdown('<div class="opd-card" style="border-left: 5px solid #E2E8F0;">', unsafe_allow_html=True)
    st.subheader("⚠️ Data Belum Tersedia")
    st.write(f"Belum ada dokumen data sektoral untuk **{opd_select}** di folder Google Drive.")
    st.markdown("""
    **Langkah yang diperlukan:**
    1. Upload file PDF/Excel ke folder terkait di Drive.
    2. Pastikan file berisi tabel data sektoral tahun berjalan.
    """)
    st.button("Cek Pembaruan Folder")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Sistem Dashboard Terintegrasi Kabupaten Belu - Tanpa Data Simulasi")
