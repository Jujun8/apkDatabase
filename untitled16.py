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
        tower = read_csv_safe("DATA-TOWER.csv")
        duk = read_csv_safe("DUK-KOMINFO-Upload.csv")

        return asn, sarpras, internet, tower, duk

    except Exception as e:
        st.error(f"❌ ERROR LOAD DATA KOMINFO: {e}")
        return None, None, None, None, None

# --- LOAD DATA BKPSDM ---
def load_bkpsdm_data():
    try:
        # Asumsikan Anda akan membuat folder bernama "BKPSDM"
        base_path = "BKPSDM"

        def read_csv_safe(filename):
            path = os.path.join(base_path, filename)

            if not os.path.exists(path):
                st.error(f"❌ File tidak ditemukan: {path}")
                return None

            try:
                return pd.read_csv(path)
            except:
                return pd.read_csv(path, encoding='latin-1')

        # SILAKAN GANTI NAMA FILE CSV INI SESUAI DENGAN DATA YANG ANDA MILIKI
        pegawai = read_csv_safe("Data-Pegawai.csv")
        pendidikan = read_csv_safe("Data-Pendidikan.csv")
        jabatan = read_csv_safe("Data-Jabatan.csv")
        pelatihan = read_csv_safe("Data-Pelatihan.csv")

        return pegawai, pendidikan, jabatan, pelatihan

    except Exception as e:
        st.error(f"❌ ERROR LOAD DATA BKPSDM: {e}")
        return None, None, None, None

# --- OPD ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bappelitbangda", "BPBD", 
        "Badan Pendapatan Daerah", "Badan Pengelola Perbatasan Daerah", "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia"
    ],
    "DINAS": [
        "Dinas Lingkungan Hidup dan Perhubungan", "Dinas Peternakan dan Perikanan",
        "Dinas Kependudukan dan Pencatatan Sipil", "Dinas Koperasi, Tenaga Kerja dan Transmigrasi",
        "Dinas Pariwisata dan Kebudayaan", "DP3AP2KB", "DPMPTSP",
        "Dinas Komunikasi dan Informatika",
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

# --- SIDEBAR ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=70)
st.sidebar.title("Pusat Data Belu")
group_select = st.sidebar.selectbox("Pilih Kelompok:", list(opd_groups.keys()))
opd_select = st.sidebar.selectbox("Pilih OPD/Dinas:", opd_groups[group_select])

# --- HEADER ---
st.title(f"🏢 {opd_select}")
st.write(f"Sumber Data: Excel Lokal / Data Sektoral / {group_select}")

# ================== LOGIKA ==================

if opd_select == "Dinas Komunikasi dan Informatika":

    st.subheader("📡 Dashboard Terintegrasi Kominfo")

    asn, sarpras, internet, tower, duk = load_kominfo_data()

    if asn is not None:
        # KPI
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("ASN TIK", len(asn))
        c2.metric("Sarpras", len(sarpras))
        c3.metric("OPD Internet", len(internet))
        c4.metric("Tower", len(tower))

        st.markdown("---")

        # TAB
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["ASN", "Internet", "Tower", "Sarpras", "DUK"])

        with tab1:
            st.dataframe(asn)
            num = asn.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(asn, x=asn.columns[0], y=num), use_container_width=True)

        with tab2:
            st.dataframe(internet)
            num = internet.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(internet, x=internet.columns[0], y=num), use_container_width=True)

        with tab3:
            st.dataframe(tower)
            num = tower.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(tower, x=tower.columns[0], y=num), use_container_width=True)

        with tab4:
            st.dataframe(sarpras)

        with tab5:
            st.dataframe(duk)
    else:
        st.warning("⚠️ Data Kominfo belum terbaca")

# ================= BKPSDM =================
elif opd_select == "Badan Kepegawaian dan Pengembangan Sumber Daya Manusia":

    st.subheader("👥 Dashboard Terintegrasi BKPSDM")

    pegawai, pendidikan, jabatan, pelatihan = load_bkpsdm_data()

    # Cek apakah setidaknya ada 1 data yang berhasil dimuat untuk menampilkan layout
    if any(df is not None for df in [pegawai, pendidikan, jabatan, pelatihan]):
        
        # KPI (Dibuat aman dengan mengecek apakah df None atau tidak)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Data Pegawai", len(pegawai) if pegawai is not None else 0)
        c2.metric("Data Pendidikan", len(pendidikan) if pendidikan is not None else 0)
        c3.metric("Data Jabatan", len(jabatan) if jabatan is not None else 0)
        c4.metric("Data Pelatihan", len(pelatihan) if pelatihan is not None else 0)

        st.markdown("---")

        # TAB
        tab1, tab2, tab3, tab4 = st.tabs(["Pegawai", "Pendidikan", "Jabatan", "Pelatihan"])

        with tab1:
            if pegawai is not None:
                st.dataframe(pegawai)
                num = pegawai.select_dtypes(include='number').columns
                if len(num) > 0:
                    st.plotly_chart(px.bar(pegawai, x=pegawai.columns[0], y=num), use_container_width=True)
            else:
                st.info("File Data-Pegawai.csv tidak ditemukan.")

        with tab2:
            if pendidikan is not None:
                st.dataframe(pendidikan)
                num = pendidikan.select_dtypes(include='number').columns
                if len(num) > 0:
                    st.plotly_chart(px.bar(pendidikan, x=pendidikan.columns[0], y=num), use_container_width=True)
            else:
                st.info("File Data-Pendidikan.csv tidak ditemukan.")

        with tab3:
            if jabatan is not None:
                st.dataframe(jabatan)
                num = jabatan.select_dtypes(include='number').columns
                if len(num) > 0:
                    st.plotly_chart(px.bar(jabatan, x=jabatan.columns[0], y=num), use_container_width=True)
            else:
                st.info("File Data-Jabatan.csv tidak ditemukan.")

        with tab4:
            if pelatihan is not None:
                st.dataframe(pelatihan)
            else:
                st.info("File Data-Pelatihan.csv tidak ditemukan.")
    else:
        st.warning("⚠️ Data BKPSDM belum terbaca. Pastikan folder 'BKPSDM' dan file CSV sudah disiapkan.")

# ================= OPD LAIN =================
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
