import streamlit as st
import pandas as pd
import sqlite3

# --- KONFIGURASI DATABASE ---
DB_NAME = "database_dinas.db"

# --- INIT DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.close()

# --- SIMPAN KE DATABASE ---
def save_to_db(df, table_name):
    try:
        conn = sqlite3.connect(DB_NAME)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Error simpan data: {e}")
        return False

# --- DAFTAR DINAS ---
DAFTAR_DINAS = {
    "Sekretariat DPRD": "sekretariat_dprd",
    "Inspektorat Daerah": "inspektorat_daerah",
    "Dinas Lingkungan Hidup dan Perhubungan": "dlh_perhubungan",
    "Dinas Peternakan dan Perikanan": "peternakan_perikanan",
    "Badan Kesatuan Bangsa dan Politik": "kesbangpol",
    "Badan Pengelola Keuangan dan Aset Daerah": "bpkad",
    "Bagian Hukum": "bagian_hukum",
    "Bagian Organisasi Setda Belu": "bagian_organisasi",

    "Dinas Kependudukan dan Pencatatan Sipil": "dukcapil",
    "Dinas Koperasi, Tenaga Kerja dan Transmigrasi": "koperasi_nakertrans",
    "Dinas Parawisata dan Kebudayaan": "pariwisata_kebudayaan",
    "Dinas Pemberdayaan Perempuan, Perlindungan Anak, Pengendalian Penduduk dan KB": "dp3ap2kb",
    "Dinas Penanaman Modal dan PTSP": "dpmptsp",
    "Badan Penanggulangan Bencana Daerah": "bpbd",
    "Badan Pendapatan Daerah": "bapenda",
    "Badan Pengelola Perbatasan Daerah": "bppd",
    "Badan Perencanaan Pembangunan, Penelitian dan Pengembangan Daerah": "bappelitbangda",
    "RSUD Mgr. Gabriel Manek, SVD Atambua": "rsud_atambua",
    "Bagian Kesejahteraan Rakyat Setda Belu": "bagian_kesra",
    "Bagian Pemerintahan Setda Belu": "bagian_pemerintahan",

    "Dinas Komunikasi dan Informatika": "kominfo",
    "Satuan Polisi Pamong Praja": "satpol_pp",
    "Bagian Pengadaan Barang dan Jasa Setda Belu": "bagian_pbj",
    "Dinas Kesehatan": "dinas_kesehatan",
    "Dinas Pekerjaan Umum dan Perumahan Rakyat": "pupr",
    "Dinas Pertanian dan Ketahanan Pangan": "pertanian",
    "Badan Kepegawaian dan Pengembangan SDM Daerah": "bkpsdm",
    "Bagian Administrasi Pembangunan Setda Belu": "bagian_admpembangunan",
    "Bagian Perekonomian dan SDA Setda Belu": "bagian_ekonomi_sda",
    "Bagian Protokol dan Komunikasi Pimpinan Setda Belu": "bagian_prokopim",
    "Bagian Umum Setda Belu": "bagian_umum",
    "Dinas Pendidikan, Kepemudaan dan Olahraga": "pendidikan",
    "Dinas Perindustrian dan Perdagangan": "perindag",
    "Dinas Perpustakaan dan Kearsipan": "perpustakaan",
    "Dinas Sosial, Pemberdayaan Masyarakat dan Desa": "dinsos_pmd",

    "Kecamatan Atambua Barat": "kec_atambua_barat",
    "Kecamatan Kota Atambua": "kec_kota_atambua",
    "Kecamatan Atambua Selatan": "kec_atambua_selatan",
    "Kecamatan Tasifeto Timur": "kec_tasifeto_timur",
    "Kecamatan Lamaknen": "kec_lamaknen",
    "Kecamatan Lamaknen Selatan": "kec_lamaknen_selatan",
    "Kecamatan Kakuluk Mesak": "kec_kakuluk_mesak",
    "Kecamatan Lasiolat": "kec_lasiolat",
    "Kecamatan Nanaet Duasbesi": "kec_nanaet_duasbesi",
    "Kecamatan Raihat": "kec_raihat",
    "Kecamatan Raimanuk": "kec_raimanuk"
}

# --- UI STREAMLIT ---
st.set_page_config(page_title="Data Center Dinas", layout="wide")

st.title("📂 Sistem Upload Data Dinas")
st.write("Upload data sektoral OPD ke database pusat.")

menu = st.sidebar.selectbox("Menu", ["Upload Data", "Lihat Database"])

init_db()

# ==============================
# MENU UPLOAD DATA
# ==============================
if menu == "Upload Data":
    st.header("Upload File (CSV atau Excel)")
    
    # 🔥 PILIH DINAS (TIDAK KETIK)
    nama_dinas_display = st.selectbox("Pilih Dinas / Instansi", list(DAFTAR_DINAS.keys()))
    nama_dinas = DAFTAR_DINAS[nama_dinas_display]

    uploaded_file = st.file_uploader("Pilih file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # HANDLE CSV & EXCEL
            if uploaded_file.name.endswith('.csv'):
                try:
                    df = pd.read_csv(uploaded_file, encoding='utf-8')
                except:
                    df = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                df = pd.read_excel(uploaded_file)

            st.subheader("Preview Data")
            st.dataframe(df.head())

            st.write("Jumlah baris:", df.shape[0])
            st.write("Jumlah kolom:", df.shape[1])

            if st.button("Simpan ke Database"):
                sukses = save_to_db(df, nama_dinas)
                if sukses:
                    st.success(f"✅ Data masuk ke tabel: {nama_dinas}")

        except Exception as e:
            st.error(f"❌ Gagal membaca file: {e}")

# ==============================
# MENU LIHAT DATABASE
# ==============================
elif menu == "Lihat Database":
    st.header("Isi Database")

    conn = sqlite3.connect(DB_NAME)

    try:
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)

        if not tables.empty:
            selected_table = st.selectbox("Pilih Tabel", tables['name'])

            if selected_table:
                data_db = pd.read_sql(f"SELECT * FROM `{selected_table}`", conn)
                st.dataframe(data_db)

                if st.button("🗑️ Hapus Tabel"):
                    conn.execute(f"DROP TABLE `{selected_table}`")
                    conn.commit()
                    st.success("Tabel dihapus")
                    st.rerun()
        else:
            st.info("Belum ada data.")

    except Exception as e:
        st.error(f"Error database: {e}")

    conn.close()
