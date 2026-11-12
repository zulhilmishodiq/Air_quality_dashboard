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

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    return df

df = load_data()

# Sidebar untuk Filter
st.sidebar.header("🔍 Filter Data Dashboard")

# 1. Filter Stasiun dengan opsi "All"
station_options = ["All"] + list(df['station_name'].unique())
selected_station = st.sidebar.selectbox(
    "Pilih Stasiun Pemantauan:",
    options=station_options
)

# 2. Filter Tahun dengan opsi "All"
year_options = ["All"] + sorted(list(df['year'].unique()))
selected_year = st.sidebar.selectbox(
    "Pilih Tahun:",
    options=year_options,
    index=1 if 2019 in year_options or 2015 in year_options else 0 # Default ke tahun tertentu jika ada
)

# Terapkan Filter ke DataFrame berdasarkan pilihan user
filtered_df = df.copy()

if selected_station != "All":
    filtered_df = filtered_df[filtered_df['station_name'] == selected_station]

if selected_year != "All":
    filtered_df = filtered_df[filtered_df['year'] == selected_year]


# Judul Utama Dashboard
st.title("🌍 Dashboard Analisis Kualitas Udara (Air Quality)")
st.markdown("Dashboard interaktif ini menyajikan hasil analisis perbandingan polusi udara dan faktor meteorologi antara stasiun pemantauan secara komprehensif.")

# Periksa apakah data tersedia setelah difilter
if filtered_df.empty:
    st.warning("⚠️ Data tidak ditemukan berdasarkan filter yang dipilih. Silakan pilih ulang stasiun atau tahun.")
else:
    # 1. Metric Ringkasan
    st.subheader("📊 Ringkasan Statistik Utama")
    col1, col2, col3 = st.columns(3)
    
    avg_pm25 = filtered_df['PM2.5'].mean()
    avg_so2 = filtered_df['SO2'].mean()
    avg_wspm = filtered_df['WSPM'].mean()
    
    col1.metric("Rata-rata (Partikel Debu Halus) $PM_{2.5}$", f"{avg_pm25:.2f} $\mu g/m^3$")
    col2.metric("Rata-rata (Sulfur Dioksida) $SO_2$", f"{avg_so2:.2f} $\mu g/m^3$")
    col3.metric("Rata-rata (Kecepatan Angin) WSPM", f"{avg_wspm:.2f} m/s")

    st.markdown("---")

    # 2. Visualisasi Pertanyaan 1: Tren Bulanan PM2.5
    st.subheader("📈 Tren Rata-rata Konsentrasi Bulanan (Partikel Debu Halus) $PM_{2.5}$")
    monthly_pm25 = filtered_df.groupby(['station_name', 'month'])['PM2.5'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=monthly_pm25, 
        x='month', 
        y='PM2.5', 
        hue='station_name', 
        marker='o', 
        linewidth=2.5,
        ax=ax
    )
    ax.set_title("Tren Bulanan Konsentrasi $PM_{2.5}$", fontsize=12, fontweight='bold')
    ax.set_xlabel("Bulan", fontsize=10)
    ax.set_ylabel("Rata-rata (Partikel Debu Halus) $PM_{2.5}$ ($\mu g/m^3$)", fontsize=10)
    ax.set_xticks(range(1, 13))
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)
    
    # **Insight untuk Grafik 1**
    st.markdown("""
    > **💡 Insight Grafik Tren Bulanan:**
    > - Polutan (Partikel Debu Halus) $PM_{2.5}$ menunjukkan pola musiman yang signifikan, di mana tingkat konsentrasi cenderung melonjak naik pada bulan-bulan musim dingin (awal dan akhir tahun).
    > - Dengan memilih opsi "All" pada filter stasiun, pengguna dapat melihat perbandingan langsung tren antarwilayah secara makro tanpa batasan satu lokasi saja.
    """)

    # 3. Visualisasi Pertanyaan 2: Scatter Plot WSPM vs SO2
    st.subheader("💨 Pengaruh Kecepatan Angin (WSPM) terhadap Kadar $SO_2$")
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=filtered_df, 
        x='WSPM', 
        y='SO2', 
        hue='station_name', 
        alpha=0.4, 
        palette='Set1',
        ax=ax2
    )
    ax2.set_title("Kecepatan Angin vs Kadar (Sulfur Dioksida) $SO_2$", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Kecepatan Angin (m/s)", fontsize=10)
    ax2.set_ylabel("Kadar $SO_2$ ($\mu g/m^3$)", fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig2)
    
    # **Insight untuk Grafik 2**
    st.markdown("""
    > **💡 Insight Grafik Korelasi Angin & Polutan:**
    > - Sebaran data memperlihatkan tren korelasi negatif antara kecepatan angin (*WSPM*) dan kadar gas (Sulfur Dioksida) $SO_2$.
    > - Kecepatan angin yang lebih tinggi membantu mempercepat proses dispersi (penyebaran) gas polutan di udara, sehingga konsentrasinya di permukaan tanah berkurang.
    """)

    # 4. Visualisasi Analisis Lanjutan: Distribusi Kategori Kualitas Udara
    if 'air_quality_category' in filtered_df.columns:
        st.subheader("📊 Distribusi Kategori Kualitas Udara")
        cat_counts = filtered_df.groupby(['station_name', 'air_quality_category']).size().reset_index(name='count')
        
        fig3, ax3 = plt.subplots(figsize=(12, 5))
        sns.barplot(
            data=cat_counts, 
            x='air_quality_category', 
            y='count', 
            hue='station_name',
            order=['Baik (Good)', 'Sedang (Moderate)', 'Tidak Sehat untuk Sensitif', 'Tidak Sehat (Unhealthy)', 'Sangat Tidak Sehat', 'Berbahaya (Hazardous)'],
            ax=ax3
        )
        ax3.set_title("Distribusi Kategori Kualitas Udara Berdasarkan (Partikel Debu Halus) $PM_{2.5}$", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Kategori", fontsize=10)
        ax3.set_ylabel("Frekuensi (Jam)", fontsize=10)
        plt.xticks(rotation=20)
        ax3.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig3)
        
        # **Insight untuk Grafik 3**
        st.markdown("""
        > **💡 Insight Analisis Lanjutan (Kategori Kualitas Udara):**
        > - Sebagian besar rentang waktu berada dalam kategori "Baik" hingga "Sedang". 
        > - Namun, kemunculan kategori "Tidak Sehat" hingga "Sangat Tidak Sehat" perlu diwaspadai karena menunjukkan durasi paparan polusi berbahaya bagi kesehatan masyarakat di wilayah stasiun terkait.
        """)

# Footer info
st.markdown("---")
st.markdown("Proyek Akhir Fundamental Analisis Data | Dibuat dengan Streamlit ✨")
