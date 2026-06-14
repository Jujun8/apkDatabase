import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# =====================================
# KONFIGURASI HALAMAN
# =====================================
st.set_page_config(
    page_title="Sistem Informasi Data Sektoral Belu",
    layout="wide",
    page_icon="🏢"
)

# =====================================
# CUSTOM CSS
# =====================================
st.markdown("""
<style>
.stApp {
    background-color: #F8FAFC;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 20px !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.opd-card {
    background-color: white;
    padding: 25px;
    border-radius: 20px;
    margin-bottom: 20px;
    border-left: 5px solid #6366F1;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# DATABASE SQLITE
# =====================================
conn = sqlite3.connect(
    "db_sektoral.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS data_sektoral (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opd TEXT,
    kategori TEXT,
    nama_data TEXT,
    nilai TEXT,
    tahun INTEGER
)
""")

conn.commit()

# =====================================
# DAFTAR OPD
# =====================================
opd_groups = {

    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD",
        "Inspektorat Daerah",
        "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah",
        "Bappelitbangda",
        "BPBD",
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
        "Dinas Kesehatan",
        "Dinas PUPR",
        "Dinas Pertanian dan Ketahanan Pangan",
        "Dinas Pendidikan, Kepemudaan dan Olahraga",
        "Dinas Perindustrian dan Perdagangan",
        "Dinas Perpustakaan dan Kearsipan",
        "Dinas Sosial, PMD",
        "Satuan Polisi Pamong Praja"
    ],

    "BAGIAN SETDA & RSUD": [
        "RSUD Mgr. Gabriel Manek, SVD Atambua",
        "Bagian Hukum",
        "Bagian Organisasi",
        "Bagian Kesejahteraan Rakyat",
        "Bagian Pemerintahan",
        "Bagian PBJ",
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

# =====================================
# SIDEBAR
# =====================================
st.sidebar.title("🏢 Pusat Data Belu")

group_select = st.sidebar.selectbox(
    "Pilih Kelompok",
    list(opd_groups.keys())
)

opd_select = st.sidebar.selectbox(
    "Pilih OPD",
    opd_groups[group_select]
)

# =====================================
# HEADER
# =====================================
st.title(f"🏢 {opd_select}")
st.write("Sistem Informasi Data Sektoral Kabupaten Belu")

# =====================================
# FORM INPUT DATA
# =====================================
st.subheader("➕ Tambah Data")

with st.form("form_input_data"):

    kategori = st.text_input("Kategori Data")

    nama_data = st.text_input("Nama Data")

    nilai = st.text_input("Nilai")

    tahun = st.number_input(
        "Tahun",
        min_value=2020,
        max_value=2035,
        value=2025
    )

    simpan = st.form_submit_button(
        "💾 Simpan Data"
    )

    if simpan:

        cursor.execute("""
        INSERT INTO data_sektoral
        (opd, kategori, nama_data, nilai, tahun)
        VALUES (?, ?, ?, ?, ?)
        """, (
            opd_select,
            kategori,
            nama_data,
            nilai,
            tahun
        ))

        conn.commit()

        st.success(
            "✅ Data berhasil disimpan"
        )

# =====================================
# AMBIL DATA OPD
# =====================================
query = """
SELECT *
FROM data_sektoral
WHERE opd = ?
"""

df = pd.read_sql_query(
    query,
    conn,
    params=(opd_select,)
)

# =====================================
# METRIK
# =====================================
st.markdown("---")

c1, c2, c3 = st.columns(3)

c1.metric(
    "Jumlah Data",
    len(df)
)

c2.metric(
    "Jumlah Kategori",
    df["kategori"].nunique()
    if not df.empty else 0
)

c3.metric(
    "Jumlah Tahun",
    df["tahun"].nunique()
    if not df.empty else 0
)

# =====================================
# TABEL DATA
# =====================================
st.subheader("📋 Data Sektoral")

if not df.empty:

    st.dataframe(
        df,
        use_container_width=True
    )

else:

    st.info(
        "Belum ada data untuk OPD ini."
    )

# =====================================
# GRAFIK
# =====================================
if not df.empty:

    grafik = (
        df.groupby("tahun")
        .size()
        .reset_index(name="Jumlah")
    )

    fig = px.bar(
        grafik,
        x="tahun",
        y="Jumlah",
        title=f"Jumlah Data {opd_select} per Tahun"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption(
    "Sistem Dashboard Terintegrasi Kabupaten Belu"
)
