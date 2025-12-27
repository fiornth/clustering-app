# Page Dashboard.py
# import library 
import streamlit as st
import plotly.express as px
import pandas as pd

def dashboard_page():
    st.title("📈 Dashboard Analisis Perusahaan")

    df = st.session_state.get('data', None)
    if df is None:
        st.warning("Silakan unggah data terlebih dahulu di tab Beranda.")
        return
    
    # Filter cluster 
    st.sidebar.markdown("### 🔍 Filter")
    cluster_options = sorted(df['cluster'].unique())
    selected_clusters = st.sidebar.multiselect(
        "Pilih Cluster:",
        options=cluster_options,
        default=cluster_options,
        help="Pilih satu atau beberapa cluster untuk ditampilkan pada dashboard."
    )

    # Filter data sesuai cluster yang dipilih
    df_filtered = df[df['cluster'].isin(selected_clusters)]
    
    if len(selected_clusters) == 0:
        st.warning("⚠️ Silakan pilih minimal satu cluster pada filter untuk menampilkan dashboard.")
        return

    # Metrics (statistik ringkas)
    total_perusahaan = len(df_filtered)
    total_tenaga_kerja = df_filtered[['pkwtt_pria','pkwtt_wanita','pkwt_pria','pkwt_wanita']].sum().sum()
    total_tka = df_filtered[['tka_pria','tka_wanita']].sum().sum() if {'tka_pria','tka_wanita'}.issubset(df_filtered.columns) else 0
    total_disabilitas = df_filtered[['disabilitas_pria','disabilitas_wanita']].sum().sum() if {'disabilitas_pria','disabilitas_wanita'}.issubset(df_filtered.columns) else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Perusahaan", f"{total_perusahaan:,}")
    col2.metric("Total Tenaga Kerja", f"{total_tenaga_kerja:,}")
    col3.metric("Total TK Asing", f"{total_tka:,}")
    col4.metric("Total TK Disabilitas", f"{total_disabilitas:,}")

    st.markdown("---")

    # Baris 1: Gender dan PKWT/PKWTT
    col1, col2 = st.columns(2)
    with col1:
        total_pria = df_filtered[['pkwtt_pria', 'pkwt_pria']].sum().sum()
        total_wanita = df_filtered[['pkwtt_wanita', 'pkwt_wanita']].sum().sum()

        df_gender = pd.DataFrame({
            'Gender' : ['Pria', 'Wanita'],
            'Jumlah' : [total_pria, total_wanita]
        })

        fig_pie = px.pie(
            df_gender,
            names= 'Gender',
            values= 'Jumlah',
            color='Gender',
            title="Distribusi Gender Tenaga Kerja",
            color_discrete_map={
                'Pria': "#6FAEFF",
                'Wanita': "#FF2289"}
        )

        fig_pie.update_traces(
            textinfo='percent'
        )

        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Caption gender
        if total_pria > total_wanita:
            st.markdown(f"➥ Tenaga kerja **didominasi oleh pria** dengan total {total_pria:,}.")
        else:
            st.markdown(f"➥ Tenaga kerja **didominasi oleh wanita** dengan total {total_wanita:,}.")

    with col2:
        total_pkwtt = df_filtered[['pkwtt_pria', 'pkwtt_wanita']].sum().sum()
        total_pkwt = df_filtered[['pkwt_pria', 'pkwt_wanita']].sum().sum()
        df_status = pd.DataFrame({
            'Status': ['PKWT', 'PKWTT'],
            'Jumlah': [total_pkwt, total_pkwtt]
        })
        fig_status = px.bar(df_status, x='Status', y='Jumlah', title="Jenis Hubungan Kerja", text='Jumlah')
        fig_status.update_traces(texttemplate='%{text:.0f}', textposition='outside')
        fig_status.update_layout(yaxis_title="Jumlah", xaxis_title="")
        st.plotly_chart(fig_status, use_container_width=True)

        # Caption status
        if total_pkwtt > total_pkwt:
            st.markdown(f"➥ Pekerja dengan hubungan kerja **PKWTT lebih banyak** daripada PKWT.")
        else:
            st.markdown(f"➥ Pekerja dengan hubungan kerja **PKWT lebih banyak** daripada PKWTT.") 

    # Baris 2: Permodalan dan Klasifikasi 
    col3, col4 = st.columns(2)
    with col3:
        if 'permodalan' in df_filtered.columns:
            permodalan_count = df_filtered['permodalan'].value_counts().reset_index()
            permodalan_count.columns = ['Permodalan', 'Jumlah']
            fig_mod = px.bar(permodalan_count, x='Permodalan', y='Jumlah', title="Distribusi Permodalan", text='Jumlah')
            fig_mod.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_mod, use_container_width=True)

            # Caption permodalan
            top_mod = permodalan_count.iloc[0]
            st.markdown(f"➥ Jenis permodalan yang paling banyak adalah **{top_mod['Permodalan']}** dengan {top_mod['Jumlah']} perusahaan.")
        else:
            st.info("Kolom 'permodalan' tidak tersedia.")

    with col4:
        if 'klasifikasi_perusahaan' in df_filtered.columns:
            klasifikasi_count = df_filtered['klasifikasi_perusahaan'].value_counts().reset_index()
            klasifikasi_count.columns = ['Klasifikasi', 'Jumlah']
            fig_klas = px.bar(klasifikasi_count, x='Klasifikasi', y='Jumlah', title="Klasifikasi Perusahaan", text='Jumlah')
            fig_klas.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_klas, use_container_width=True)

            # Caption klasifikasi perusahaan
            top_klas = klasifikasi_count.iloc[0]
            st.markdown(f"➥ Kategori perusahaan yang paling banyak adalah **{top_klas['Klasifikasi']}** dengan {top_klas['Jumlah']} perusahaan.")
        else:
            st.info("Kolom 'klasifikasi_perusahaan' tidak tersedia.")

    # Baris 3: Distribusi per Kelurahan 
    st.markdown("### Distribusi Perusahaan per Kelurahan")
    if 'kelurahan' in df_filtered.columns:
        kelurahan_count = df_filtered['kelurahan'].value_counts().reset_index()
        kelurahan_count.columns = ['Kelurahan', 'Jumlah']
        fig_kel = px.bar(
            kelurahan_count,
            x='Kelurahan', y='Jumlah',
            text='Jumlah',
            title="Jumlah Perusahaan per Kelurahan"
        )
        fig_kel.update_traces(texttemplate='%{text}', textposition='outside')
        fig_kel.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_kel, use_container_width=True)

        # Caption distribusi kelurahan
        top_kel = kelurahan_count.iloc[0]
        st.markdown(f"➥ Kelurahan dengan jumlah perusahaan terbanyak adalah **{top_kel['Kelurahan']}** dengan {top_kel['Jumlah']} perusahaan.")
    else:
        st.info("Kolom 'kelurahan' tidak tersedia.")