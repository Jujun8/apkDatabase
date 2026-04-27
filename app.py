import streamlit as st
import pandas as pd
import plotly.express as px

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

# --- LOAD DATA KOMINFO (CSV) ---
def load_kominfo_data():
    try:
        asn = pd.read_csv("/content/ASN-Berpendidikan-TIK.csv")
        sarpras = pd.read_csv("/content/Data-Sarana-dan-Prasarana-Diskominfo.csv")
        internet = pd.read_csv("/content/Data-Internet-OPD-Beserta-Kapasitasnya-.csv")
        tower = pd.read_csv("/content/DATA-TOWER.csv")
        duk = pd.read_csv("/content/DUK-KOMINFO-Upload.csv")
        return asn, sarpras, internet, tower, duk
    except:
        return None, None, None, None, None

# --- OPD ---
opd_groups = {
    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD", "Inspektorat Daerah", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bappelitbangda", "BPBD", 
        "Badan Pendapatan Daerah", "Badan Pengelola Perbatasan Daerah", "BKPSDM"
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

        # TAB DATA
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "ASN", "Internet", "Tower", "Sarpras", "DUK"
        ])

        # ASN
        with tab1:
            st.dataframe(asn)
            num = asn.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(asn, x=asn.columns[0], y=num), use_container_width=True)

        # INTERNET
        with tab2:
            st.dataframe(internet)
            num = internet.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(internet, x=internet.columns[0], y=num), use_container_width=True)

        # TOWER
        with tab3:
            st.dataframe(tower)
            num = tower.select_dtypes(include='number').columns
            if len(num) > 0:
                st.plotly_chart(px.bar(tower, x=tower.columns[0], y=num), use_container_width=True)

        # SARPRAS
        with tab4:
            st.dataframe(sarpras)

        # DUK
        with tab5:
            st.dataframe(duk)

    else:
        st.warning("⚠️ File CSV Kominfo belum ditemukan")

# ================= OPD LAIN =================

elif opd_select == "Bagian Hukum":
    df_h = get_hukum_data()
    st.dataframe(df_h)

elif opd_select == "Sekretariat DPRD":
    st.info("Data AKD DPRD")
    st.table(pd.DataFrame({
        "Jabatan": ["Ketua", "Wakil Ketua"],
        "Nama": ["Contoh 1", "Contoh 2"]
    }))

else:
    st.markdown('<div class="opd-card">', unsafe_allow_html=True)
    st.subheader("⚠️ Data Belum Tersedia")
    st.write(f"Data untuk **{opd_select}** belum tersedia dalam sistem.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("---")
st.caption("Sistem Dashboard Terintegrasi Kabupaten Belu")
