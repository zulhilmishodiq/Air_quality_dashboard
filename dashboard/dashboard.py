import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Air Quality Dashboard",
    page_icon="🌍",
    layout="wide"
)

# Load Data dengan jalur dinamis yang aman
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "main_data.csv")
    
    if not os.path.exists(file_path):
        file_path = os.path.join(os.path.dirname(base_dir), "main_data.csv")
        
    df = pd.read_csv(file_path)
    return df

df = load_data()

# --- DETEKSI OTOMATIS KOLOM STASIUN ---
# Mencari nama kolom stasiun yang ada di dalam dataset secara otomatis
possible_station_cols = ['station', 'station_name', 'Location', 'loc', 'city']
station_col = None
for col in possible_station_cols:
    if col in df.columns:
        station_col = col
        break

# Jika tidak ditemukan nama standar, ambil kolom bertipe teks (object/string) pertama
if station_col is None:
    for col in df.select_dtypes(include=['object']).columns:
        station_col = col
        break

# --- DETEKSI OTOMATIS KOLOM TAHUN ---
possible_year_cols = ['year', 'Tahun', 'tahun']
year_col = None
for col in possible_year_cols:
    if col in df.columns:
        year_col = col
        break

# Sidebar untuk Filter
st.sidebar.header("🔍 Filter Data Dashboard")

# 1. Filter Stasiun dengan opsi "All"
if station_col:
    station_options = ["All"] + sorted(list(df[station_col].unique().astype(str)))
    selected_station = st.sidebar.selectbox("Pilih Stasiun Pemantauan:", options=station_options)
else:
    selected_station = "All"
    st.sidebar.warning("Kolom stasiun tidak ditemukan.")

# 2. Filter Tahun dengan opsi "All"
if year_col:
    years_list = sorted(list(df[year_col].dropna().unique()))
    year_options = ["All"] + [str(y) for y in years_list]
    selected_year_str = st.sidebar.selectbox("Pilih Tahun:", options=year_options)
else:
    selected_year_str = "All"

# Terapkan Filter ke DataFrame berdasarkan pilihan user
filtered_df = df.copy()

if station_col and selected_station != "All":
    filtered_df = filtered_df[filtered_df[station_col].astype(str) == selected_station]

if year_col and selected_year_str != "All":
    filtered_df = filtered_df[filtered_df[year_col].astype(str) == selected_year_str]


# Judul Utama Dashboard
st.title("🌍 Dashboard Analisis Kualitas Udara (Air Quality)")
st.markdown("Dashboard interaktif ini menyajikan hasil analisis perbandingan polusi udara dan faktor meteorologi secara komprehensif.")

# Penjelasan Istilah Polutan dengan Bahasa Sederhana
with st.expander("ℹ️ Mengenal Istilah Polutan & Parameter (Klik untuk membaca)"):
    st.markdown("""
    - **$PM_{2.5}$ (Partikel Debu Halus):** Partikel polusi udara berukuran super kecil (lebih halus dari sehelai rambut) yang berasal dari asap kendaraan, pembakaran, dan debu. Mudah terhirup masuk ke paru-paru dan memengaruhi kesehatan pernapasan.
    - **$SO_2$ (Sulfur Dioksida):** Gas berbau tajam yang dihasilkan dari pembakaran batu bara, aktivitas pabrik industri, dan mesin kendaraan berat. Dapat menyebabkan iritasi saluran napas dan memicu hujan asam.
    - **Kecepatan Angin (WSPM):** Kecepatan pergerakan angin (meter/detik) yang berperan menyapu dan menyebarkan polutan agar tidak menumpuk di satu area.
    """)

# Periksa apakah data tersedia setelah difilter
if filtered_df.empty:
    st.warning("⚠️ Data tidak ditemukan berdasarkan filter yang dipilih. Silakan pilih ulang stasiun atau tahun.")
else:
    # 1. Metric Ringkasan (Cek ketersediaan kolom secara aman)
    st.subheader("📊 Ringkasan Statistik Utama")
    col1, col2, col3 = st.columns(3)
    
    avg_pm25 = filtered_df['PM2.5'].mean() if 'PM2.5' in filtered_df.columns else 0
    avg_so2 = filtered_df['SO2'].mean() if 'SO2' in filtered_df.columns else 0
    avg_wspm = filtered_df['WSPM'].mean() if 'WSPM' in filtered_df.columns else 0
    
    col1.metric("Rata-rata PM2.5 (Debu Halus)", f"{avg_pm25:.2f} ug/m3")
    col2.metric("Rata-rata SO2 (Sulfur Dioksida)", f"{avg_so2:.2f} ug/m3")
    col3.metric("Rata-rata Kecepatan Angin", f"{avg_wspm:.2f} m/s")

    st.markdown("---")

    # 2. Visualisasi Pertanyaan 1: Tren Bulanan PM2.5
    if 'PM2.5' in filtered_df.columns and 'month' in filtered_df.columns and station_col:
        st.subheader("📈 Tren Rata-rata Konsentrasi Bulanan PM2.5")
        monthly_pm25 = filtered_df.groupby([station_col, 'month'])['PM2.5'].mean().reset_index()
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.lineplot(
            data=monthly_pm25, 
            x='month', 
            y='PM2.5', 
            hue=station_col, 
            marker='o', 
            linewidth=2.5,
            ax=ax
        )
        ax.set_title("Tren Bulanan Konsentrasi PM2.5", fontsize=12, fontweight='bold')
        ax.set_xlabel("Bulan", fontsize=10)
        ax.set_ylabel("Rata-rata PM2.5 (ug/m3)", fontsize=10)
        ax.set_xticks(range(1, 13))
        ax.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig)
        
        st.markdown("""
        > **💡 Insight Grafik Tren Bulanan:**
        > - Polutan $PM_{2.5}$ menunjukkan pola musiman yang signifikan, di mana tingkat konsentrasi cenderung melonjak naik pada bulan-bulan musim dingin (awal dan akhir tahun).
        > - Dengan memilih opsi "All" pada filter stasiun, pengguna dapat melihat perbandingan langsung tren antarwilayah secara makro tanpa batasan satu lokasi saja.
        """)

    # 3. Visualisasi Pertanyaan 2: Scatter Plot WSPM vs SO2
    if 'WSPM' in filtered_df.columns and 'SO2' in filtered_df.columns and station_col:
        st.subheader("💨 Pengaruh Kecepatan Angin (WSPM) terhadap Kadar SO2")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.scatterplot(
            data=filtered_df, 
            x='WSPM', 
            y='SO2', 
            hue=station_col, 
            alpha=0.4, 
            palette='Set1',
            ax=ax2
        )
        ax2.set_title("Kecepatan Angin vs Kadar Sulfur Dioksida (SO2)", fontsize=12, fontweight='bold')
        ax2.set_xlabel("Kecepatan Angin (m/s)", fontsize=10)
        ax2.set_ylabel("Kadar SO2 (ug/m3)", fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.6)
        st.pyplot(fig2)
        
        st.markdown("""
        > **💡 Insight Grafik Korelasi Angin & Polutan:**
        > - Sebaran data memperlihatkan tren korelasi negatif antara kecepatan angin (*WSPM*) dan kadar gas $SO_2$.
        > - Kecepatan angin yang tinggi membantu mempercepat proses dispersi (penyebaran) gas polutan di udara, sehingga konsentrasinya di permukaan tanah berkurang.
        """)

    # 4. Visualisasi Analisis Lanjutan: Distribusi Kategori Kualitas Udara
    if 'air_quality_category' in filtered_df.columns and station_col:
        st.subheader("📊 Distribusi Kategori Kualitas Udara")
        cat_counts = filtered_df.groupby([station_col, 'air_quality_category']).size().reset_index(name='count')
        
        fig3, ax3 = plt.subplots(figsize=(12, 5))
        sns.barplot(
            data=cat_counts, 
            x='air_quality_category', 
            y='count', 
            hue=station_col,
            order=['Baik (Good)', 'Sedang (Moderate)', 'Tidak Sehat untuk Sensitif', 'Tidak Sehat (Unhealthy)', 'Sangat Tidak Sehat', 'Berbahaya (Hazardous)'],
            ax=ax3
        )
        ax3.set_title("Distribusi Kategori Kualitas Udara Berdasarkan PM2.5", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Kategori", fontsize=10)
        ax3.set_ylabel("Frekuensi (Jam)", fontsize=10)
        plt.xticks(rotation=20)
        ax3.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig3)
        
        st.markdown("""
        > **💡 Insight Analisis Lanjutan (Kategori Kualitas Udara):**
        > - Sebagian besar rentang waktu berada dalam kategori "Baik" hingga "Sedang". 
        > - Namun, kemunculan kategori "Tidak Sehat" hingga "Sangat Tidak Sehat" perlu diwaspadai karena menunjukkan durasi paparan polusi berbahaya bagi kesehatan masyarakat di wilayah stasiun terkait.
        """)

# Footer info
st.markdown("---")
st.markdown("Proyek Akhir Fundamental Analisis Data | Dibuat dengan Streamlit ✨")
