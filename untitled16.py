import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
st.cache_data.clear()
st.cache_resource.clear()


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

@st.cache_resource
def get_gspread_client():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=SCOPES
    )
    return gspread.authorize(creds)

gc = get_gspread_client()

SPREADSHEET_ID = "1devdxVPKESQCYCaC8UdEZt2jyqjxFXPLhGN2nVlLiQo"

@st.cache_resource
def get_spreadsheet():
    return gc.open_by_key(SPREADSHEET_ID)

spreadsheet = get_spreadsheet()

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


@st.cache_data(ttl=60)
def read_dataset_from_sheet(sheet_name):
    try:
        ws = spreadsheet.worksheet(sheet_name)
        data = ws.get_all_values()

        if len(data) == 0:
            return pd.DataFrame()

        return pd.DataFrame(data[1:], columns=data[0])

    except:
        return pd.DataFrame()


def delete_dataset(sheet_name):

    spreadsheet = gc.open_by_key(
        SPREADSHEET_ID
    )

    ws = spreadsheet.worksheet(
        sheet_name
    )

    spreadsheet.del_worksheet(ws)

@st.cache_data(ttl=30)
def load_metadata():
    sheet = get_metadata_sheet()
    data = sheet.get_all_values()

    if len(data) <= 1:
        return pd.DataFrame()

    return pd.DataFrame(data[1:], columns=data[0])

def df_to_pdf(df, watermark_text="SISTEM DATA BELU", logo_path="logo.png"):
    buffer = BytesIO()

    try:
        pdf = SimpleDocTemplate(buffer)

        data = [df.columns.tolist()] + df.astype(str).values.tolist()

        table = Table(data)

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))

        def add_header(canvas_obj, doc):
            canvas_obj.saveState()

            # ================= LOGO =================
            try:
                logo = ImageReader(logo_path)
                canvas_obj.drawImage(logo, 40, 720, width=70, height=70, mask='auto')
            except:
                pass

            # ================= JUDUL =================
            canvas_obj.setFont("Helvetica-Bold", 12)
            canvas_obj.drawString(110, 780, "PEMERINTAH KABUPATEN BELU")

            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.drawString(110, 760, watermark_text)

            # ================= WATERMARK =================
            
            width, height = doc.pagesize

            canvas_obj.saveState()

            canvas_obj.setFont("Helvetica-Bold", 42)
            canvas_obj.setFillGray(0.88)

            canvas_obj.drawCentredString(
                width / 2,
                height / 2 + 20,
                "BIDANG STATISTIK"
            )

            canvas_obj.drawCentredString(
                width / 2,
                height / 2 - 30,
                "DAN PERSANDIAN"
            )

            canvas_obj.restoreState()

            canvas_obj.restoreState()

        pdf.build([table], onFirstPage=add_header, onLaterPages=add_header)

        buffer.seek(0)
        return buffer

    except Exception as e:
        st.error(f"Gagal membuat PDF: {e}")
        return None

def get_drive_service():
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/drive"
        ]
    )

    return build(
        "drive",
        "v3",
        credentials=creds
    )

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
col_logo, col_title = st.columns([1, 6])

with col_logo:
    st.image("logo.png", width=100)

with col_title:
    st.title("SISTEM INFORMASI DATA SEKTORAL")
    st.subheader("Kabupaten Belu")
    st.write(f"OPD : {opd_select}")


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

    if uploaded_file is None:
        st.warning("Silakan upload file terlebih dahulu")
        st.stop()

    if nama_dataset.strip() == "":
        st.warning("Nama dataset wajib diisi")
        st.stop()

    sheet_name = create_dataset_table_name(opd_select, nama_dataset)

    save_dataset_to_sheet(df_upload, sheet_name)

    metadata_sheet = get_metadata_sheet()
    metadata_sheet.append_row([
        str(datetime.now().timestamp()),
        opd_select,
        nama_dataset,
        keterangan,
        sheet_name,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        pdf_link

    ])

    st.success("✅ Dataset berhasil disimpan")

    st.cache_data.clear()  # 🔥 refresh data cache
    st.rerun()
    pdf_link = ""

    if uploaded_pdf is not None:

        drive_service = get_drive_service()

        file_metadata = {
            "name": uploaded_pdf.name
        }

        media = MediaIoBaseUpload(
            uploaded_pdf,
            mimetype="application/pdf",
            resumable=True
        )

        uploaded_file_drive = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id"
        ).execute()

        file_id = uploaded_file_drive.get("id")

        drive_service.permissions().create(
            fileId=file_id,
            body={
                "type": "anyone",
                "role": "reader"
            }
        ).execute()

        pdf_link = f"https://drive.google.com/file/d/{file_id}/view"

# =====================================
# DATASET TERSIMPAN
# =====================================

st.markdown("---")
st.subheader("📚 Dataset Tersimpan")

metadata = load_metadata()

if metadata.empty:
    st.info("Belum ada dataset.")
    st.stop()

# filter OPD
metadata = metadata[metadata["opd"] == opd_select]

if metadata.empty:
    st.info("Belum ada dataset untuk OPD ini.")
    st.stop()

# pilih dataset
dataset_pilih = st.selectbox(
    "Pilih Dataset",
    metadata["nama_dataset"].tolist()
)

row = metadata[
    metadata["nama_dataset"] == dataset_pilih
].iloc[0]
        # ==========================
        # INFORMASI DATASET
        # ==========================

col1, col2 = st.columns(2)

with col1:
    st.write(
         f"**📁 Nama Dataset:** {row['nama_dataset']}"
    )

    st.write(
        f"**📅 Tanggal Upload:** {row['tanggal_upload']}"
    )

with col2:
    st.write(
         f"**📝 Keterangan:** {row.get('keterangan','-')}"
    )

st.markdown("---")

        # ==========================
        # TAMPILKAN DATASET
        # ==========================
try:
    sheet_name = row["sheet_name"]
    df = read_dataset_from_sheet(sheet_name)

except Exception as e:
    st.error(f"Gagal membaca dataset: {e}")
    st.stop()
    
if "pdf_link" in row and row["pdf_link"]:
    st.link_button(
        "📄 Buka Dokumen PDF",
        row["pdf_link"]
    )
# ==========================
# VALIDASI DATA
# ==========================
if df is None or df.empty:
    st.warning("Dataset kosong")
    st.stop()

# ==========================
# TAMPIL DATASET
# ==========================
st.subheader("📊 Data Dataset")
st.write(f"Jumlah Data: {len(df)} baris")

st.dataframe(df, use_container_width=True)

# ==========================
# DOWNLOAD PDF
# ==========================
try:
    pdf_file = df_to_pdf(
        df,
        watermark_text=" ",
        logo_path="logo.png"
    )

    if pdf_file is not None:
        st.download_button(
            "⬇ Download PDF",
            data=pdf_file,
            file_name=f"{row['nama_dataset']}.pdf",
            mime="application/pdf"
        )

except Exception as e:
    st.error(f"Gagal membuat PDF: {e}")
st.markdown("---")



# ==========================
# HAPUS DATASET
# ==========================

if st.button("🗑 Hapus Dataset", type="primary"):

    try:
        # hapus sheet dataset
        delete_dataset(row["sheet_name"])

        # ambil metadata sheet (yang benar)
        sheet = get_metadata_sheet()

        # hapus baris metadata berdasarkan ID
        cell = sheet.find(row["id"])
        sheet.delete_rows(cell.row)

        st.cache_data.clear()

        st.success("Dataset berhasil dihapus")
        st.rerun()

    except Exception as e:
        st.error(f"Gagal menghapus dataset: {e}")



# =====================================
# FOOTER
# =====================================

st.markdown("---")
st.caption("Sistem Dashboard Terintegrasi Kabupaten Belu")







