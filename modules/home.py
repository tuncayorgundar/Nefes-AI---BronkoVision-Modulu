import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

def render_home_page(selected_patient):
    """
    Seçilen hasta nesnesinin ana sayfasını (bilgilerini) render eder.
    """
    if selected_patient:
        st.header(f"Hasta: {selected_patient.first_name} {selected_patient.last_name}")
        
        # Hasta Detayları
        with st.expander("Hasta Bilgileri", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Doğum Tarihi:** {selected_patient.date_of_birth.strftime('%d-%m-%Y') if selected_patient.date_of_birth else 'Bilinmiyor'}")
                st.markdown(f"**Cinsiyet:** {selected_patient.gender if selected_patient.gender else 'Bilinmiyor'}")
                st.markdown(f"**Kan Grubu:** {selected_patient.blood_type if selected_patient.blood_type else 'Bilinmiyor'}")
            with col2:
                st.markdown(f"**Telefon:** {selected_patient.phone_number if selected_patient.phone_number else 'Bilinmiyor'}")
                st.markdown(f"**Adres:** {selected_patient.address if selected_patient.address else 'Bilinmiyor'}")
                st.markdown(f"**Durum:** {selected_patient.status if selected_patient.status else 'Bilinmiyor'}")
    else:
        st.warning("Seçilen hastaya ait veri bulunamadı.")

def render_general_overview(selected_patient, detailed_patient_data):   
    """
    Seçilen hastanın genel durumunu, tedavi şemalarını ve tüm doz ayarlamalarını gösterir.
    """
