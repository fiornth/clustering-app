# Main App 
import streamlit as st 
from streamlit_option_menu import option_menu
from pages_program import Beranda, Dashboard, Info

st.set_page_config(page_title="Klasterisasi Perusahaan", layout="wide")

# Logo di sidebar
st.sidebar.image("Lambang_Kota_Depok.png", width=130)

# Garis pemisah
st.sidebar.markdown("---") 

# Sidebar navigation
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Beranda", "Dashboard", "Informasi"],
        icons=["house", "bar-chart-line", "book"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "3!important", "background-color": "#f0f2f5"},
            "icon": {"color": "black", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "--hover-color": "#e0e0e0"
            },
            "nav-link-selected": {"background-color": "#103a82"},
        }
    )

# Routing ke halaman sesuai pilihan
if selected == "Beranda":
    Beranda.home_page()
elif selected == "Dashboard":
    Dashboard.dashboard_page()
else:
    Info.info_page()