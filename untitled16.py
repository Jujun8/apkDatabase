import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import re
from datetime import datetime

# =====================================
# KONFIGURASI HALAMAN
# =====================================
st.set_page_config(
    page_title="Sistem Informasi Data Sektoral Belu",
    page_icon="🏢",
    layout="wide"
)

# =====================================
# CUSTOM CSS
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
# DATABASE
# =====================================
conn = sqlite3.connect(
    "db_sektoral.db",
    check_same_thread=False
)

conn.execute("""
CREATE TABLE IF NOT EXISTS metadata_dataset(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opd TEXT,
    nama_dataset TEXT,
    keterangan TEXT,
    nama_tabel TEXT,
    tanggal_upload TEXT
)
""")

conn.commit()

# =====================================
# FUNGSI
# =====================================
def create_dataset_table_name(opd, nama_dataset):

    opd_clean = re.sub(
        r'[^a-zA-Z0-9]',
        '_',
        opd.lower()
    )

    dataset_clean = re.sub(
        r'[^a-zA-Z0-9]',
        '_',
        nama_dataset.lower()
    )

    return f"{opd_clean}_{dataset_clean}"

# =====================================
# DATA OPD
# =====================================
opd_groups = {

    "SEKRETARIAT & BADAN": [
        "Sekretariat DPRD",
        "Inspektorat Daerah",
        "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah",
        "BP4D",
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
        "Satuan Polisi Pamong Praja",
        "Dinas Pemberdayaan Perempuan, Perlindungan Anak, Pegendalian Penduduk dan Keluarga Berencana"
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
# FORM UPLOAD DATASET
# =====================================
# =====================================
# FORM UPLOAD DATASET
# =====================================
st.subheader("📤 Upload Dataset")

nama_dataset = st.text_input(
    "📝 Nama Dataset",
    placeholder="Contoh: Data DUK Kominfo 2025"
)

keterangan = st.text_area(
    "📄 Keterangan Dataset",
    placeholder="Masukkan deskripsi dataset..."
)

uploaded_file = st.file_uploader(
    "Upload File CSV",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        # UTF-8
        df_upload = pd.read_csv(uploaded_file)

    except:

        uploaded_file.seek(0)

        try:
            # UTF-8 BOM
            df_upload = pd.read_csv(
                uploaded_file,
                encoding="utf-8-sig"
            )

        except:

            uploaded_file.seek(0)

            # Excel Indonesia
            df_upload = pd.read_csv(
                uploaded_file,
                encoding="cp1252"
            )

    # =====================================
    # BERSIHKAN DATA
    # =====================================

    # Hapus kolom kosong (Unnamed)
    df_upload = df_upload.loc[
        :,
        ~df_upload.columns.astype(str).str.contains("^Unnamed")
    ]

    # Ganti NaN menjadi kosong
    df_upload = df_upload.fillna("")

    # Hapus baris yang benar-benar kosong
    df_upload = df_upload[
        ~(df_upload.astype(str)
            .apply(lambda x: x.str.strip())
            .eq("")
            .all(axis=1))
    ]

    # Rapikan index
    df_upload.reset_index(
        drop=True,
        inplace=True
    )

    st.success("✅ File berhasil dibaca")

    st.write("Preview Data")

    st.dataframe(
        df_upload.head(20),
        use_container_width=True
    )

    st.info(
        f"📊 {len(df_upload)} baris | "
        f"{len(df_upload.columns)} kolom"
    )

    if st.button("💾 Simpan Dataset"):

        if nama_dataset.strip() == "":

            st.warning(
                "Nama dataset wajib diisi"
            )

        else:

            dataset_table = create_dataset_table_name(
                opd_select,
                nama_dataset
            )

            df_upload.to_sql(
                dataset_table,
                conn,
                if_exists="replace",
                index=False
            )

            conn.execute("""
            INSERT INTO metadata_dataset(
                opd,
                nama_dataset,
                keterangan,
                nama_tabel,
                tanggal_upload
            )
            VALUES(?,?,?,?,?)
            """,
            (
                opd_select,
                nama_dataset,
                keterangan,
                dataset_table,
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()

            st.success(
                "✅ Dataset berhasil disimpan"
            )

            st.rerun()

# =====================================
# DATASET OPD
# =====================================
st.markdown("---")
st.subheader("📚 Dataset Tersimpan")

metadata = pd.read_sql_query(
    """
    SELECT *
    FROM metadata_dataset
    WHERE opd = ?
    ORDER BY tanggal_upload DESC
    """,
    conn,
    params=(opd_select,)
)

if len(metadata) > 0:

    dataset_pilih = st.selectbox(
        "Pilih Dataset",
        metadata["nama_dataset"]
    )

    row = metadata[
        metadata["nama_dataset"] == dataset_pilih
    ].iloc[0]

    st.info(
        f"📁 Dataset : {row['nama_dataset']}"
    )

    st.write(
        f"**Keterangan :** {row['keterangan']}"
    )

    st.write(
        f"**Tanggal Upload :** {row['tanggal_upload']}"
    )

    df = pd.read_sql(
    f"SELECT * FROM {row['nama_tabel']}",
    conn
    )

    df = df.fillna("")

    col1, col2 = st.columns(2)

    col1.metric(
        "Jumlah Baris",
        len(df)
    )

    col2.metric(
        "Jumlah Kolom",
        len(df.columns)
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    # ==========================
    # GRAFIK
    # ==========================
    numeric_cols = list(
        df.select_dtypes(
            include=["int64", "float64"]
        ).columns
    )

    if len(numeric_cols) > 0:

        st.subheader("📊 Visualisasi Data")

        kolom = st.selectbox(
            "Pilih Kolom Numerik",
            numeric_cols
        )

        fig = px.histogram(
            df,
            x=kolom,
            title=f"Distribusi {kolom}"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ==========================
    # HAPUS DATASET
    # ==========================
    if st.button("🗑️ Hapus Dataset Ini"):

        conn.execute(
            f"DROP TABLE {row['nama_tabel']}"
        )

        conn.execute("""
        DELETE FROM metadata_dataset
        WHERE id = ?
        """,
        (int(row["id"]),)
        )

        conn.commit()

        st.success(
            "Dataset berhasil dihapus"
        )

        st.rerun()

else:

    st.info(
        "Belum ada dataset untuk OPD ini."
    )

# =====================================
# FOOTER
# =====================================
st.markdown("---")
st.caption(
    "Sistem Dashboard Terintegrasi Kabupaten Belu"
)
