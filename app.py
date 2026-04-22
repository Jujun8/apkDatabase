import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random

# --- CONFIG DASHBOARD ---
st.set_page_config(page_title="Dashboard OPD Kabupaten Belu", layout="wide", page_icon="📊")

# --- CUSTOM CSS (GAYA MODERN GLASSMORPHISM) ---
st.markdown("""
    <style>
    /* Latar belakang aplikasi */
    .stApp {
        background-color: #F8FAFC;
    }
    
    /* Kartu Metric yang melengkung dan berbayang */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 20px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #f1f5f9 !important;
    }

    /* Mempercantik sidebar */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #e2e8f0;
    }

    /* Tombol Custom */
    .stButton>button {
        border-radius: 12px;
        background-color: #6366F1;
        color: white;
        border: none;
        padding: 10px 24px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #4F46E5;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA SOURCE ---
@st.cache_data
def get_opd_data():
    opd_list = [
        "Sekretariat DPRD", "Inspektorat Daerah", "Dinas Lingkungan Hidup dan Perhubungan",
        "Dinas Peternakan dan Perikanan", "Badan Kesatuan Bangsa dan Politik",
        "Badan Pengelola Keuangan dan Aset Daerah", "Bagian Hukum", "Bagian Organisasi Setda Belu",
        "Dinas Kependudukan dan Pencatatan Sipil", "Dinas Koperasi, Tenaga Kerja dan Transmigrasi",
        "Dinas Pariwisata dan Kebudayaan", "BPBD", "Badan Pendapatan Daerah",
        "Badan Pengelola Perbatasan Daerah", "Bappelitbangda", "RSUD Mgr. Gabriel Manek, SVD Atambua",
        "Bagian Kesejahteraan Rakyat Setda Belu", "Bagian Pemerintahan Setda Belu",
        "Dinas Komunikasi dan Informatika", "Satuan Polisi Pamong Praja", "Bagian PBJ Setda Belu",
        "Dinas Kesehatan", "Dinas PUPR", "Dinas Pertanian dan Ketahanan Pangan",
        "BKPSDM", "Bagian Administrasi Pembangunan", "Bagian Perekonomian dan SDA",
        "Bagian Protokol dan Komunikasi Pimpinan", "Bagian Umum Setda Belu",
        "Dinas Pendidikan, Kepemudaan dan Olahraga", "Dinas Perindustrian dan Perdagangan",
        "Dinas Perpustakaan dan Kearsipan", "Dinas Sosial, PMD",
        "Kecamatan Atambua Barat", "Kecamatan Kota Atambua", "Kecamatan Atambua Selatan",
        "Kecamatan Tasifeto Timur", "Kecamatan Lamaknen", "Kecamatan Lamaknen Selatan",
        "Kecamatan Kakuluk Mesak", "Kecamatan Lasiolat", "Kecamatan Nanaet Duasbesi",
        "Kecamatan Raihat", "Kecamatan Raimanuk"
    ]
    
    data = []
    for opd in opd_list:
        data.append({
            "Nama OPD": opd,
            "Realisasi Anggaran (%)": random.randint(40, 95),
            "Progres Fisik (%)": random.randint(35, 98),
            "Jumlah Program": random.randint(5, 25),
            "Pagu Anggaran (M)": round(random.uniform(2, 45), 2),
            "Kategori": random.choice(["Kesehatan", "Infrastruktur", "Sosial", "Administrasi"]),
            "Status": random.choice(["Selesai", "Proses"])
        })
    return pd.DataFrame(data)

df = get_opd_data()

# --- SIDEBAR NAVIGASI ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/01/Logo_Kabupaten_Belu.png", width=80)
st.sidebar.title("Sistem Monitoring")
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔍 Cari Nama OPD...")
selected_opd = st.sidebar.selectbox("Pilih Langsung:", ["RINGKASAN UTAMA"] + list(df['Nama OPD']))

# Logika Pencarian
df_display = df[df['Nama OPD'].str.contains(search_query, case=False)] if search_query else df

# --- KONTEN UTAMA ---
if selected_opd == "RINGKASAN UTAMA":
    st.title("Hello, Admin! 👋")
    st.markdown("Berikut adalah ringkasan kinerja OPD Kabupaten Belu.")
    
    # Row 1: KPI Utama
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Instansi", len(df), "↑ 2")
    c2.metric("Rata-rata Realisasi", f"{round(df['Realisasi Anggaran (%)'].mean(), 1)}%", "5.4%")
    c3.metric("Total Pagu (M)", f"Rp {round(df['Pagu Anggaran (M)'].sum(), 1)}", "↑ 12%")
    c4.metric("Kepatuhan Laporan", "92%", "↑ 0.8%")

    st.markdown("---")

    # Row 2: Grafik Utama
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.subheader("📊 Realisasi Anggaran per OPD (%)")
        fig = px.bar(df_display.head(10), x='Nama OPD', y='Realisasi Anggaran (%)', 
                     color='Realisasi Anggaran (%)', 
                     color_continuous_scale='Blues',
                     template="plotly_white")
        
        # --- PERBAIKAN BARIS 122 ---
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.subheader("🎯 Kategori Bidang")
        fig_pie = px.pie(df, names='Kategori', values='Pagu Anggaran (M)', hole=0.6,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Row 3: Tabel Data (Gaya Order List Modern)
    st.subheader("📋 Daftar Rincian Kerja OPD")
    st.dataframe(df_display[['Nama OPD', 'Kategori', 'Realisasi Anggaran (%)', 'Progres Fisik (%)', 'Status']], 
                 use_container_width=True)

else:
    # --- TAMPILAN DETAIL PER OPD ---
    detail = df[df['Nama OPD'] == selected_opd].iloc[0]
    st.title(f"🏢 {selected_opd}")
    
    d1, d2, d3 = st.columns(3)
    d1.metric("Anggaran", f"{detail['Realisasi Anggaran (%)']}%")
    d2.metric("Fisik", f"{detail['Progres Fisik (%)']}%")
    d3.metric("Pagu", f"Rp {detail['Pagu Anggaran (M)']} M")

    st.markdown("### Visualisasi Capaian")
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = detail['Realisasi Anggaran (%)'],
        gauge = {
            'axis': {'range': [None, 100]}, 
            'bar': {'color': "#6366F1"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#f1f5f9"
        }
    ))
    fig_gauge.update_layout(height=300, paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_gauge, use_container_width=True)

    # Tombol Folder
    st.markdown("---")
    st.subheader("📄 Arsip Digital")
    st.write(f"Mencari dokumen pendukung untuk {selected_opd}...")
    if st.button("📁 Buka Folder Google Drive"):
        st.success("Mengarahkan ke Folder Drive Sektoral...")

st.markdown("---")
st.caption("Pemerintah Kabupaten Belu - Dashboard Data Terintegrasi 2026")
