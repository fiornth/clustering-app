# Page Info.py
import streamlit as st

def info_page():
    st.title("ℹ️ Informasi Sistem")
    st.markdown("""
    Aplikasi ini menggunakan algoritma **K-Means Clustering** untuk mengelompokkan perusahaan berdasarkan data ketenagakerjaan.

    ### Tujuan
    - Mengidentifikasi pola ketenagakerjaan di Kota Depok.
    - Mengelompokkan perusahaan berdasarkan kesamaan karakteristik tenaga kerja dan kepemilikan dokumen PP & PKB.
    - Memvisualisasikan data ketenagakerjaan dalam bentuk dashboard interaktif.

    ### Cara Menggunakan
    **Halaman Beranda:**
    1. Pilih **Beranda**, unggah data perusahaan dalam format CSV/XLSX atau gunakan data default yang disediakan.
    2. Sistem secara otomatis akan melakukan pre-processing, menentukan jumlah cluster (*k*) terbaik, dan menampilkan hasil clustering.
    3. User dapat mengunduh data hasil clustering.
    
    **Halaman Dashboard:**  
    1. Pilih **Dashboard** untuk melihat visualisasi dari data yang telah diunggah atau data default.
    2. Gunakan filter di sidebar untuk memilih cluster yang ingin ditampilkan.

    ### Tentang K-Means
    K-Means adalah algoritma *unsupervised learning* yang membagi data menjadi beberapa kelompok berdasarkan kemiripan fitur. 
    Pada penelitian ini, jumlah cluster (k) optimal ditentukan secara otomatis menggunakan metode Davies-Bouldin Index (DBI).
    """)