import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import re

# =====================================
# KONFIGURASI HALAMAN
# =====================================
st.set_page_config(
    page_title="Sistem Informasi Data Sektoral Belu",
    page_icon="🏢",
    layout="wide"
)

# =====================================
# CSS
# =====================================
st.markdown("""
<style>
.stApp{
    background-color:#F8FAFC;
}

[data-testid="stMetric"]{
    background:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.1);
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

# =====================================
# FUNGSI NAMA TABEL
# =====================================
def get_table_name(opd):
    return "opd_" + re.sub(
        r'[^a-zA-Z0-9_]',
        '',
        opd.lower().replace(" ", "_")
    )

# =====================================
# DATA OPD
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

table_name = get_table_name(opd_select)

# =====================================
# HEADER
# =====================================
st.title(f"🏢 {opd_select}")
st.write("Sistem Informasi Data Sektoral Kabupaten Belu")

# =====================================
# UPLOAD CSV
# =====================================
st.subheader("📤 Upload Data CSV")

uploaded_file = st.file_uploader(
    "Pilih File CSV",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df_upload = pd.read_csv(uploaded_file)
    except:
        df_upload = pd.read_csv(
            uploaded_file,
            encoding="latin1"
        )

    st.success("File berhasil dibaca")

    st.write("Preview Data")

    st.dataframe(
        df_upload.head(),
        use_container_width=True
    )

    if st.button("💾 Simpan Data"):

        df_upload.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        st.success(
            f"Data berhasil disimpan untuk {opd_select}"
        )

# =====================================
# TAMPILKAN DATA OPD
# =====================================
st.markdown("---")
st.subheader("📋 Data Tersimpan")

try:

    df = pd.read_sql(
        f"SELECT * FROM {table_name}",
        conn
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Jumlah Baris",
        len(df)
    )

    col2.metric(
        "Jumlah Kolom",
        len(df.columns)
    )

    col3.metric(
        "Nama Tabel",
        table_name
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==========================
    # VISUALISASI
    # ==========================
    numeric_cols = list(
        df.select_dtypes(
            include=["int64", "float64"]
        ).columns
    )

    if len(numeric_cols) > 0:

        st.subheader("📊 Grafik Data")

        selected_column = st.selectbox(
            "Pilih Kolom Numerik",
            numeric_cols
        )

        fig = px.histogram(
            df,
            x=selected_column,
            title=f"Distribusi {selected_column}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

except Exception:
    st.info(
        "Belum ada data yang tersimpan untuk OPD ini."
    )

# =====================================
# HAPUS DATA OPD
# =====================================
st.markdown("---")

if st.button("🗑️ Hapus Data OPD Ini"):

    try:

        conn.execute(
            f"DROP TABLE {table_name}"
        )

        conn.commit()

        st.success(
            "Data berhasil dihapus."
        )

        st.rerun()

    except:
        st.warning(
            "Tidak ada data untuk dihapus."
        )

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption(
    "Sistem Dashboard Terintegrasi Kabupaten Belu"
)
