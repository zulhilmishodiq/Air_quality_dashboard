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
    # Pastikan kolom datetime dibaca dengan benar jika ada
    return df

df = load_data()

# Sidebar untuk Filter
st.sidebar.header("🔍 Filter Data Dashboard")

# Filter Stasiun
selected_stations = st.sidebar.multiselect(
    "Pilih Stasiun Pemantauan:",
    options=df['station_name'].unique(),
    default=df['station_name'].unique()
)

# Filter Tahun
selected_years = st.sidebar.multiselect(
    "Pilih Tahun:",
    options=sorted(df['year'].unique()),
    default=[2015] if 2015 in df['year'].unique() else sorted(df['year'].unique())
)

# Terapkan Filter ke DataFrame
filtered_df = df[(df['station_name'].isin(selected_stations)) & (df['year'].isin(selected_years))]

# Judul Utama Dashboard
st.title("🌍 Dashboard Analisis Kualitas Udara (Air Quality)")
st.markdown("Dashboard interaktif ini menyajikan hasil analisis perbandingan polusi udara dan faktor meteorologi antara stasiun pemantauan.")

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
    
    col1.metric("Rata-rata $PM_{2.5}$", f"{avg_pm25:.2f} $\mu g/m^3$")
    col2.metric("Rata-rata $SO_2$", f"{avg_so2:.2f} $\mu g/m^3$")
    col3.metric("Rata-rata Kecepatan Angin", f"{avg_wspm:.2f} m/s")
    
    st.markdown("---")

    # 2. Visualisasi Pertanyaan 1: Tren Bulanan PM2.5
    st.subheader("📈 Perbandingan Rata-rata Konsentrasi Bulanan $PM_{2.5}$")
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
    ax.set_ylabel("Rata-rata $PM_{2.5}$ ($\mu g/m^3$)", fontsize=10)
    ax.set_xticks(range(1, 13))
    ax.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig)

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
    ax2.set_title("Kecepatan Angin vs Kadar $SO_2$", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Kecepatan Angin (m/s)", fontsize=10)
    ax2.set_ylabel("Kadar $SO_2$ ($\mu g/m^3$)", fontsize=10)
    ax2.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig2)

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
        ax3.set_title("Distribusi Kategori Kualitas Udara Berdasarkan $PM_{2.5}$", fontsize=12, fontweight='bold')
        ax3.set_xlabel("Kategori", fontsize=10)
        ax3.set_ylabel("Frekuensi (Jam)", fontsize=10)
        plt.xticks(rotation=20)
        ax3.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig3)

# Footer info
st.markdown("---")
st.markdown("Proyek Akhir Fundamental Analisis Data | Dibuat dengan Streamlit ✨")
