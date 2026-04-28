import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Sistem Informasi Data Sektoral Belu",
    layout="wide",
    page_icon="🏢"
)

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

# --- DATA DUMMY (HUKUM) ---
def get_hukum_data():
    return pd.DataFrame({
        'Tahun': ['2020', '2021', '2022', '2023', '2024'],
        'Keputusan Bupati': [201, 230, 358, 321, 414],
        'Peraturan Bupati': [9, 46, 46, 8, 35],
        'Peraturan Daerah': [8, 7, 1, 58, 58]
    })

# --- LOAD DATA KOMINFO ---
def load_kominfo_data():
    try:
        base_path = "KOMINFO"

        def read_csv_safe(filename):
            path = os.path.join(base_path, filename)

            if not os.path.exists(path):
                st.error(f"❌ File tidak ditemukan: {path}")
                return None

            try:
                return pd.read_csv(path)
            except:
                return pd.read_csv(path, encoding='latin-1')

        asn = read_csv_safe("ASN-Berpendidikan-TIK.csv")
        sarpras = read_csv_safe("Data-Sarana-dan-Prasarana-Diskominfo.csv")
        internet = read_csv_safe("Data-Internet-OPD-Beserta-Kapasitasnya-.csv")
        towerBantuan = read_csv_safe("DATA-TOWER.csv")
        duk = read_csv_safe("DUK-KOMINFO-Upload.csv")
        towerTelekomunikasi = read_csv_safe("Data Tower Telekomunikasi.csv")

        return asn, sarpras, internet, towerBantuan, duk, towerTelekomunikasi

    except Exception as e:
        st.error(f"❌ ERROR LOAD DATA: {e}")
        return None, None, None, None, None, None

# --- LOAD DATA BKPSDM ---
def load_bkpsdm_data_by_year(year):
    try:
        base_path = os.path.join("BKPSDM", str(year))

        def read_csv_safe(filename):
            path = os.path.join(base_path, filename)

            if not os.path.exists(path):
                st.warning(f"⚠️ File tidak ditemukan: {path}")
                return pd.DataFrame()

            try:
                return pd.read_csv(path)
            except:
                return pd.read_csv(path, encoding="latin-1")

        pegawaiKomposisi = read_csv_safe("Data Pegawai Berdasarkan Komposisi Instansi di Kabupaten Belu Tahun 2020.csv")
        pegawaiPangkat = read_csv_safe("Data Pegawai Berdasarkan Pangkat di Kabupaten Belu Tahun 2020.csv")
        pegawaiHonorer = read_csv_safe("Data Pegawai Honorer Tingkat Pendidikan Formal di Kabupaten Belu Tahun 2020.csv")

        return pegawaiKomposisi, pegawaiPangkat, pegawaiHonorer

    except Exception as e:
        st.error(f"❌ ERROR LOAD DATA BKPSDM: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# --- OPD ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah",
        "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah",
        "Bappelitbangda", "BPBD",
        "Badan Pendapatan Daerah",
        "Badan Pengelola Perbatasan Daerah",
        "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia"
    ],

    "DINAS": [
        "Dinas Lingkungan Hidup dan Perhubungan",
        "Dinas Peternakan dan Perikanan",
        "Dinas Kependudukan dan Pencatatan Sipil",
        "Dinas Koperasi, Tenaga Kerja dan Transmigrasi",
        "Dinas Pariwisata dan Kebudayaan",
        "Dinas Komunikasi dan Informatika",
        "Dinas Kesehatan", "Dinas PUPR",
        "Dinas Pertanian dan Ketahanan Pangan",
        "Dinas Pendidikan, Kepemudaan dan Olahraga",
        "Dinas Perindustrian dan Perdagangan",
        "Dinas Perpustakaan dan Kearsipan",
        "Dinas Sosial, PMD",
        "Satuan Polisi Pamong Praja"
    ],

    "BAGIAN SETDA & RSUD": [
        "RSUD Mgr. Gabriel Manek, SVD Atambua",
        "Bagian Hukum", "Bagian Organisasi",
        "Bagian Kesejahteraan Rakyat",
        "Bagian Pemerintahan", "Bagian PBJ",
        "Bagian Administrasi Pembangunan",
        "Bagian Perekonomian dan SDA",
        "Bagian Protokol dan Komunikasi Pimpinan",
        "Bagian Umum"
    ],

    "KECAMATAN": [
        "Kecamatan Atambua Barat",
        "Kecamatan Kota Atambua",
        "Kecamatan Atambua Selatan",
        "Kecamatan Tasifeto Timur",
        "Kecamatan Lamaknen",
        "Kecamatan Lamaknen Selatan",
        "Kecamatan Kakuluk Mesak",
        "Kecamatan Lasiolat",
        "Kecamatan Nanaet Duasbesi",
        "Kecamatan Raihat",
        "Kecamatan Raimanuk"
    ]
}

# --- SIDEBAR ---
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png",
    width=50
)
st.sidebar.title("Pusat Data Belu")

group_select = st.sidebar.selectbox("Pilih Kelompok:", list(opd_groups.keys()))
opd_select = st.sidebar.selectbox("Pilih OPD/Dinas:", opd_groups[group_select])

# --- HEADER ---
st.title(f"🏢 {opd_select}")
st.write(f"Sumber Data: Excel Lokal / Data Sektoral / {group_select}")

# ================== LOGIKA ==================

if opd_select == "Dinas Komunikasi dan Informatika":

    st.subheader("📡 Dashboard Terintegrasi Kominfo")

    if os.path.exists("KOMINFO"):
        st.write("📂 Isi folder data:", os.listdir("KOMINFO"))
    else:
        st.error("Folder 'KOMINFO' tidak ditemukan")

    asn, sarpras, internet, towerBantuan, duk, towerTelekomunikasi = load_kominfo_data()

    if asn is not None:

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("ASN TIK", len(asn))
        c2.metric("Sarpras", len(sarpras))
        c3.metric("OPD Internet", len(internet))
        c4.metric("Tower Bantuan Bakti", len(towerBantuan))
        c5.metric("Tower Telekomunikasi", len(towerTelekomunikasi))

        st.markdown("---")

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
            ["ASN", "Internet", "Tower Bantuan", "Tower Telekomunikasi", "Sarpras", "DUK"]
        )

        with tab1:
            st.dataframe(asn)

        with tab2:
            st.dataframe(internet)

        with tab3:
            st.dataframe(towerBantuan)

        with tab4:
            st.dataframe(towerTelekomunikasi)

        with tab5:
            st.dataframe(sarpras)

        with tab6:
            st.dataframe(duk)

elif opd_select == "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia":

    st.subheader("👨‍💼 Dashboard BKPSDM")

    tahun_pilih = st.selectbox("Pilih Tahun", [2020, 2021, 2022, 2023, 2024])

    pegawaiKomposisi, pegawaiPangkat, pegawaiHonorer = load_bkpsdm_data_by_year(tahun_pilih)

    c1, c2, c3 = st.columns(3)
    c1.metric("Data Pegawai Berdasarkan Komposisi Instansi", len(pegawaiKomposisi))
    c2.metric("Data Pegaawai Berdasarkan Pangkat", len(pegawaiPangkat))
    c3.metric("Data pegawai Honorer Berdasarkan Tingkat", len(pegawaiHonorer))
    

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(
        ["Data Pegawai Berdasarkan Komposisi Instansi", "Data Pegaawai Berdasarkan Pangkat", "Data pegawai Honorer Berdasarkan Tingkat"]
    )

    with tab1:
        st.dataframe(pegawaiKomposisi)

    with tab2:
        st.dataframe(pegawaiPangkat)

    with tab3:
        st.dataframe(pegawaiHonorer)



elif opd_select == "Bagian Hukum":
    st.dataframe(get_hukum_data())

elif opd_select == "Sekretariat DPRD":
    st.table(pd.DataFrame({
        "Jabatan": ["Ketua", "Wakil Ketua"],
        "Nama": ["Contoh 1", "Contoh 2"]
    }))

else:
    st.markdown('<div class="opd-card">', unsafe_allow_html=True)
    st.subheader("⚠️ Data Belum Tersedia")
    st.write(f"Data untuk **{opd_select}** belum tersedia.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Sistem Dashboard Terintegrasi Kabupaten Belu")
