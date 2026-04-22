import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIG DASHBOARD ---
st.set_page_config(page_title="Dashboard OPD Kabupaten Belu", layout="wide", page_icon="📊")

# --- CUSTOM CSS UNTUK TAMPILAN MENARIK ---
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 12px; shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    div[data-testid="stExpander"] { background-color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA SOURCE (SEMUA OPD DARI DAFTAR ANDA) ---
@st.cache_data
def get_opd_data():
    # Daftar seluruh OPD berdasarkan permintaan Anda
    opd_list = [
        # Kelompok 1
        "Sekretariat DPRD", "Inspektorat Daerah", "Dinas Lingkungan Hidup dan Perhubungan",
        "Dinas Peternakan dan Perikanan", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bagian Hukum", "Bagian Organisasi Setda Belu",
        # Kelompok 2
        "Dinas Kependudukan dan Pencatatan Sipil", "Dinas Koperasi, Tenaga Kerja dan Transmigrasi",
        "Dinas Pariwisata dan Kebudayaan", "BPBD", "Badan Pendapatan Daerah",
        "Badan Pengelola Perbatasan Daerah", "Bappelitbangda", "RSUD Mgr. Gabriel Manek, SVD Atambua",
        "Bagian Kesejahteraan Rakyat Setda Belu", "Bagian Pemerintahan Setda Belu",
        # Kelompok 3
        "Dinas Komunikasi dan Informatika", "Satuan Polisi Pamong Praja", "Bagian PBJ Setda Belu",
        "Dinas Kesehatan", "Dinas PUPR", "Dinas Pertanian dan Ketahanan Pangan",
        "BKPSDM", "Bagian Administrasi Pembangunan", "Bagian Perekonomian dan SDA",
        "Bagian Protokol dan Komunikasi Pimpinan", "Bagian Umum Setda Belu",
        "Dinas Pendidikan, Kepemudaan dan Olahraga", "Dinas Perindustrian dan Perdagangan",
        "Dinas Perpustakaan dan Kearsipan", "Dinas Sosial, PMD",
        # Kecamatan
        "Kecamatan Atambua Barat", "Kecamatan Kota Atambua", "Kecamatan Atambua Selatan",
        "Kecamatan Tasifeto Timur", "Kecamatan Lamaknen", "Kecamatan Lamaknen Selatan",
        "Kecamatan Kakuluk Mesak", "Kecamatan Lasiolat", "Kecamatan Nanaet Duasbesi",
        "Kecamatan Raihat", "Kecamatan Raimanuk"
    ]
    
    # Simulasi data (Ganti bagian ini dengan fungsi pembaca PDF/Google Drive nanti)
    import random
    data = []
    for opd in opd_list:
        data.append({
            "Nama OPD": opd,
            "Realisasi Anggaran (%)": random.randint(40, 95),
            "Progres Fisik (%)": random.randint(35, 98),
            "Jumlah Program": random.randint(5, 25),
            "Pagu Anggaran (M)": round(random.uniform(2, 45), 2),
            "Status": "Aktif"
        })
    return pd.DataFrame(data)

df = get_opd_data()

# --- SIDEBAR NAVIGASI ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=100)
st.sidebar.title("Dashboard Monitoring")
st.sidebar.info("Data bersumber dari folder Google Drive: 'Data Sektoral'")

# Filter Pencarian
search_query = st.sidebar.text_input("🔍 Cari Nama OPD/Dinas...")
selected_opd = st.sidebar.selectbox("Atau Pilih Langsung:", ["RINGKASAN UTAMA"] + list(df['Nama OPD']))

# Logika Pencarian
if search_query:
    df_display = df[df['Nama OPD'].str.contains(search_query, case=False)]
else:
    df_display = df

# --- KONTEN UTAMA ---
if selected_opd == "RINGKASAN UTAMA":
    st.title("📊 Ringkasan Kinerja Seluruh OPD Belu")
    
    # Row 1: KPI Utama
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Instansi", len(df))
    c2.metric("Rata-rata Realisasi", f"{round(df['Realisasi Anggaran (%)'].mean(), 1)}%")
    c3.metric("Total Pagu (Simulasi)", f"Rp {round(df['Pagu Anggaran (M)'].sum(), 1)} M")

    # Row 2: Grafik Perbandingan Utama
    st.markdown("### Grafik Perbandingan Realisasi Anggaran (%)")
    fig = px.bar(df_display, x='Nama OPD', y='Realisasi Anggaran (%)', 
                 color='Realisasi Anggaran (%)', color_continuous_scale='Blues',
                 hover_data=['Progres Fisik (%)', 'Pagu Anggaran (M)'])
    st.plotly_chart(fig, use_container_width=True)

    # Row 3: Tabel Data Lengkap
    with st.expander("Lihat Seluruh Data Tabel"):
        st.dataframe(df_display, use_container_width=True)

else:
    # --- TAMPILAN DETAIL PER OPD ---
    detail = df[df['Nama OPD'] == selected_opd].iloc[0]
    
    st.title(f"🏢 Detail OPD: {selected_opd}")
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        st.subheader("Indikator Utama")
        st.metric("Realisasi Anggaran", f"{detail['Realisasi Anggaran (%)']}%")
        st.metric("Progres Fisik", f"{detail['Progres Fisik (%)']}%")
        st.metric("Program Kerja", f"{detail['Jumlah Program']}")

    with col2:
        st.subheader("Keuangan")
        st.info(f"**Pagu Anggaran:** \n\n Rp {detail['Pagu Anggaran (M)']} Miliar")
        st.success(f"**Status Laporan:** \n\n Terverifikasi")

    with col3:
        # Grafik Gauge untuk Visualisasi Menarik
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = detail['Realisasi Anggaran (%)'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Persentase Capaian"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#1f77b4"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Informasi Tambahan (Placeholder untuk file PDF)
    st.markdown("---")
    st.subheader("📄 Dokumen Terkait di Google Drive")
    st.write(f"Sistem mendeteksi dokumen PDF untuk **{selected_opd}** tersedia di folder.")
    if st.button("Buka Folder Drive"):
        st.write("Mengarahkan ke: https://drive.google.com/drive/folders/1cEzFO8LXTtv_ypHp109jHwGJjoGCIFQD")

# Footer
st.markdown("---")
st.caption("Dashboard Pemerintah Kabupaten Belu - Data Terintegrasi Google Drive")
