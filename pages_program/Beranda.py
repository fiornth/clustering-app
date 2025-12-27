# Page Beranda.py
# import library
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px 
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import davies_bouldin_score

# fungsi describe cluster
def describe_cluster(row):
    """Menentukan karakteristik dan rekomendasi tiap cluster"""
    avg_pkwtt = row.get('total_pkwtt', 0 )
    avg_pkwt = row.get('total_pkwt', 0 )
    pp = row.get('pp', 0 )
    pkb = row.get('pkb', 0 )

    # klasifikasi skala perusahaan
    total_pekerja = avg_pkwtt + avg_pkwt 
    if total_pekerja < 5: 
        skala = "Merepresentasikan perusahaan mikro"
    elif total_pekerja >=5 and total_pekerja <20:
        skala = "Merepresentasikan perusahaan kecil"
    elif total_pekerja >=20 and total_pekerja <100:
        skala = "Merepresentasikan perusahaan menengah"
    else:
        skala = "Merepresentasikan perusahaan besar"

    # klasifikasi kepemilikan dokumen
    if pp == 1 and pkb == 1:
        status = "memiliki PP dan PKB"
    elif pp == 0 and pkb == 1:
        status = "hanya memiliki PKB"
    elif pp == 1 and pkb == 0:
        status = "hanya memiliki PP"
    elif pp <= 0.5 and pkb <= 0.5:
        status = "mayoritas belum memiliki PP dan PKB"
    elif pp < 0.5 and pkb >= 0.5:
        status = "mayoritas memiliki PKB"
    elif pp >= 0.5 and pkb < 0.5:
        status = "mayoritas memiliki PP"
    else: 
        status = "distribusi kepemilikan dokumen bervariasi"

    # Gabung ciri 
    karakteristik = f"{skala} yang {status}"
    return karakteristik

# Main function halaman beranda 
def home_page():
    st.title("🏢 Klasterisasi Perusahaan di Kota Depok")

    if 'data' not in st.session_state: 
        st.session_state['data'] = None

    st.markdown("""
    **Catatan:**
    - Upload data atau gunakan data default
    - File harus dalam format .xlsx atau .csv
    - Pastikan terdapat kolom: pkwtt_pria, pkwtt_wanita, pkwt_pria, pkwt_wanita, pp, pkb
    """)

    uploaded_file = st.file_uploader("Upload file data", type=["csv", "xlsx"])

    if uploaded_file is not None:
        try: 
            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success("File berhasil diunggah.")
        except Exception as e: 
            st.error(f"Gagal membaca file: {e}")
            return
    else: 
        st.info("Menggunakan data default")
        try: 
            df = pd.read_csv("data/data_default_rahasia.csv")
        except Exception as e: 
            st.error(f"Data default tidak ditemukan: {e}")
            return 
        
    # copy raw 
    df_raw = df.copy()

    try:
        # nama kolom ke lowercase
        df.columns = df.columns.str.lower()
        required_columns = ['pkwtt_pria', 'pkwtt_wanita', 'pkwt_pria', 'pkwt_wanita', 'pp', 'pkb']
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            st.error(f"Kolom wajib tidak ada: {missing}. Silakan perbaiki file dan unggah ulang.")
            return
        
        # remove duplicates
        before = len(df)
        df = df.drop_duplicates()
        after_dup = len(df)
        removed_dup = before - after_dup

        # remove invalid data
        df = df[df['klasifikasi_perusahaan'].str.lower() != 'belum input data']
        after_removal = len(df)
        removed_invalid = after_dup - after_removal

        # info baris data
        st.info(f"Data awal: {before:,} baris | Data duplikat: {removed_dup:,} baris | Data Invalid: {removed_invalid:,} baris")

        # feature engineering
        df['total_pkwtt'] = df['pkwtt_pria'] + df['pkwtt_wanita']   
        df['total_pkwt'] = df['pkwt_pria'] + df['pkwt_wanita']

        # feature encoding
        df['pp'] = df['pp'].str.lower().str.strip().map({'ya' : 1, 'tidak': 0})
        df['pkb'] = df['pkb'].str.lower().str.strip().map({'ya' : 1, 'tidak': 0})

        # feature selection
        features = ['total_pkwtt', 'total_pkwt', 'pp', 'pkb']
        X = df[features].copy()

        # feature transformation
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # cari jumlah cluster optimal
        best_k = 2
        best_dbi = float('inf')
        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            labels = kmeans.fit_predict(X_scaled)
            dbi = davies_bouldin_score(X_scaled, labels)
            if dbi < best_dbi:
                best_dbi = dbi
                best_k = k
        
        st.success(f"Jumlah cluster optimal (DBI): {best_k}")

        # model clustering final 
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
        df['cluster'] = kmeans.fit_predict(X_scaled).astype(int).astype(str)

        # simpan sesi 
        st.session_state['data'] = df.copy()
        st.session_state['data_raw'] = df_raw.copy()

        # warna cluster
        df['cluster'] = df['cluster'].astype(str)
        clusters = sorted(df['cluster'].unique())
        base_colors = px.colors.qualitative.D3

        while len(base_colors) < len(clusters):
            base_colors += base_colors

        custom_colors = {cluster: base_colors[i] for i, cluster in enumerate(clusters)}

        # karakteristik cluster
        st.subheader("Karakteristik Setiap Cluster")
        cluster_counts = df['cluster'].value_counts().sort_index()
        cols = st.columns(len(cluster_counts))
        for i, (cluster, count) in enumerate(cluster_counts.items()):
            with cols[i]:
                st.metric(label=f"Cluster {cluster}", value=count)

        cluster_summary = df.groupby('cluster')[features].mean().round(2)
        score = (1 - cluster_summary['pp'] * 0.5) + (1 - cluster_summary['pkb'] * 0.5)
        cluster_summary['rank'] = score.rank(ascending=False).astype(int)

        st.dataframe(cluster_summary)
        st.markdown("""
        <div style='text-align: right; font-style: italic; font-size: 11px; color: gray;'>
        *Rank didasarkan atas kepemilikan dokumen (PP & PKB)
        </div>
        """, unsafe_allow_html=True)

        # visualisasi hasil cluster
        fitur_tk = ['total_pkwtt', 'total_pkwt']
        fitur_adm = ['pp', 'pkb']

        df_tk = df[fitur_tk + ['cluster']].groupby('cluster').mean().reset_index()
        df_adm = df[fitur_adm + ['cluster']].groupby('cluster').mean().reset_index()

        df_tk_melt = df_tk.melt(id_vars='cluster', var_name='Fitur', value_name='Rata-rata')
        df_adm_melt = df_adm.melt(id_vars='cluster', var_name='Fitur', value_name='Rata-rata')

        nama_fitur = {
            'total_pkwtt': 'Pekerja Tetap <br> (total_pkwtt)',
            'total_pkwt': 'Pekerja Kontrak <br> (total_pkwt)',
            'pp': 'PP',
            'pkb': 'PKB'
        }

        df_tk_melt['Fitur'] = df_tk_melt['Fitur'].replace(nama_fitur)
        df_adm_melt['Fitur'] = df_adm_melt['Fitur'].replace(nama_fitur)

        df_tk_melt['cluster'] = df_tk_melt['cluster'].astype(str)
        fig_tenaga = px.bar(
            df_tk_melt, x='Fitur', y='Rata-rata', color='cluster',
            color_discrete_map=custom_colors, barmode='group',
            title="Profiling Tenaga Kerja"
        )
        fig_tenaga.update_layout(yaxis = dict(range=[0, 800]), xaxis_tickangle=0)

        df_adm_melt['cluster'] = df_adm_melt['cluster'].astype(str)
        fig_dokumen = px.bar(
            df_adm_melt, x='Fitur', y='Rata-rata', color='cluster',
            color_discrete_map=custom_colors, barmode='group',
            title="Profiling Kepemilikan Dokumen"
        )

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_tenaga, use_container_width=True)
        with col2:
            st.plotly_chart(fig_dokumen, use_container_width=True)

        # deskripsi hasil cluster
        st.subheader("Deskripsi Cluster")
        for idx, row in cluster_summary.iterrows():
            karakteristik = describe_cluster(row)
            st.markdown(f"""
            **Cluster {idx}**
            - 🧩 **Karakteristik:** {karakteristik}
            """)

        # data tabs per cluster
        st.subheader("Data dengan Label Cluster")

        tabs = st.tabs(["Data Asli"] + [f"Cluster {i}" for i in sorted(df['cluster'].unique())])
        with tabs[0]:
            st.write("Data asli dan Cluster")
            st.dataframe(df)
        for i, cluster in enumerate(sorted(df['cluster'].unique()), start=1):
            with tabs[i]:
                st.write(f"Data untuk Cluster {cluster}")
                st.dataframe(df[df['cluster'] == cluster])

    except Exception as e:
        st.error(f"Terjadi kesalahan saat proses: {e}")