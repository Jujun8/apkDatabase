import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# =====================================
# GOOGLE SHEETS & DRIVE
# =====================================

# =====================================
# GOOGLE SHEETS & DRIVE
# =====================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=SCOPES
)

gc = gspread.authorize(creds)


SPREADSHEET_ID = "1devdxVPKESQCYCaC8UdEZt2jyqjxFXPLhGN2nVlLiQo"



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

def get_metadata_sheet():

    spreadsheet = gc.open_by_key(
        SPREADSHEET_ID
    )

    try:
        return spreadsheet.worksheet("metadata")

    except:

        ws = spreadsheet.add_worksheet(
            title="metadata",
            rows=1000,
            cols=20
        )

        ws.append_row([
            "id",
            "opd",
            "nama_dataset",
            "keterangan",
            "sheet_name",
            "tanggal_upload"
        ])

        return ws

def save_dataset_to_sheet(df, sheet_name):

    spreadsheet = gc.open_by_key(
        SPREADSHEET_ID
    )

    try:
        old_ws = spreadsheet.worksheet(sheet_name)
        spreadsheet.del_worksheet(old_ws)
    except:
        pass

    ws = spreadsheet.add_worksheet(
        title=sheet_name,
        rows=max(len(df)+100, 1000),
        cols=max(len(df.columns)+10, 20)
    )

    data = [df.columns.tolist()] + \
           df.astype(str).values.tolist()

    ws.update(data)

    return True


def read_dataset_from_sheet(sheet_name):

    spreadsheet = gc.open_by_key(
        SPREADSHEET_ID
    )

    ws = spreadsheet.worksheet(
        sheet_name
    )

    data = ws.get_all_records()

    return pd.DataFrame(data)


def delete_dataset(sheet_name):

    spreadsheet = gc.open_by_key(
        SPREADSHEET_ID
    )

    ws = spreadsheet.worksheet(
        sheet_name
    )

    spreadsheet.del_worksheet(ws)


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

        sheet_name = create_dataset_table_name(
            opd_select,
            nama_dataset
        )

        save_dataset_to_sheet(
            df_upload,
            sheet_name
        )

        metadata_sheet = get_metadata_sheet()

        metadata_sheet.append_row([
            str(datetime.now().timestamp()),
            opd_select,
            nama_dataset,
            keterangan,
            sheet_name,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ])

# =====================================
# DATASET OPD
# =====================================
# =====================================
# DATASET OPD
# =====================================

st.markdown("---")
st.subheader("📚 Dataset Tersimpan")

metadata_sheet = get_metadata_sheet()

data_meta = metadata_sheet.get_all_records()

metadata = pd.DataFrame(data_meta)

if "keterangan" not in metadata.columns:
    metadata["keterangan"] = ""

if len(metadata) > 0:

    metadata = metadata[
        metadata["opd"] == opd_select
    ]

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
            f"**Keterangan :** {row.get('keterangan','-')}"
        )

        st.write(
            f"**Tanggal Upload :** {row['tanggal_upload']}"
        )

        # =====================================
        # EDIT KETERANGAN
        # =====================================

        with st.expander("✏ Edit Keterangan"):

            ket_baru = st.text_area(
                "Keterangan",
                value=row.get(
                    "keterangan",
                    ""
                )
            )

            if st.button(
                "Simpan Keterangan"
            ):

                cell = metadata_sheet.find(
                    row["id"]
                )

                metadata_sheet.update_cell(
                    cell.row,
                    4,
                    ket_baru
                )

                st.success(
                    "Keterangan diperbarui"
                )

                st.rerun()

        # =====================================
        # BACA DATASET DARI GOOGLE SHEETS
        # =====================================
        
        try:

            st.write("ROW DATA:")
            st.json(dict(row))

            sheet_name = str(
                row.get("sheet_name", "")
            ).strip()

            st.write("SHEET NAME:")
            st.write(sheet_name)

            if sheet_name == "":

                st.warning(
                    "Sheet name kosong"
                )

                st.stop()

            # BACA DATASET
            df = read_dataset_from_sheet(
                sheet_name
            )

            st.success(
                f"Dataset berhasil dibaca ({len(df)} baris)"
            )

            # DEBUG
            st.write("JUMLAH BARIS:")
            st.write(len(df))

            st.write("NAMA KOLOM:")
            st.write(df.columns.tolist())

            st.markdown("---")

            st.subheader("📊 Data Dataset")

            st.dataframe(
                df,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                "Gagal membaca dataset."
            )

            st.exception(e)

            st.stop()

            col1,col2,col3 = st.columns(3)

            col1.metric(
                "Jumlah Baris",
                len(df)
            )

            col2.metric(
                "Jumlah Kolom",
                len(df.columns)
            )

            col3.metric(
                "Dataset",
                row["nama_dataset"]
            )

            # =====================================
            # DOWNLOAD CSV
            # =====================================

            csv_download = df.to_csv(
                index=False
            )

            st.download_button(
                "⬇ Download CSV",
                csv_download,
                file_name=f"{row['nama_dataset']}.csv",
                mime="text/csv"
            )

            # =====================================
            # GRAFIK OTOMATIS
            # =====================================

            st.markdown("---")

            st.subheader(
                "📈 Visualisasi Data"
            )

            numeric_cols = df.select_dtypes(
                include="number"
            ).columns

            if len(numeric_cols) > 0:

                kolom_grafik = st.selectbox(
                    "Pilih Kolom Numerik",
                    numeric_cols
                )

                fig = px.histogram(
                    df,
                    x=kolom_grafik,
                    title=f"Distribusi {kolom_grafik}"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "Tidak ada kolom numerik untuk divisualisasikan."
                )

        except Exception as e:

            st.error(
                "Gagal membaca dataset."
            )

            st.exception(e)

        # =====================================
        # HAPUS DATASET
        # =====================================

        st.markdown("---")

        if st.button(
            "🗑 Hapus Dataset",
            type="primary"
        ):

            

            cell = metadata_sheet.find(
                row["id"]
            )

            metadata_sheet.delete_rows(
                cell.row
            )

            st.success(
                "Dataset berhasil dihapus"
            )

            st.rerun()

    else:

        st.info(
            "Belum ada dataset untuk OPD ini."
        )

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
