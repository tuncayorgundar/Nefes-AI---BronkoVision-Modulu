# modules/bio_analysis_page.py

import streamlit as st
import os

from database_connector import DatabaseConnector
from modules.bio_analysis.classic_analyzer.analyzer import ClassicBioAnalyzer
from modules.bio_analysis.ai_analyzer.ai_analyzer import render_enhanced_bio_analysis_page, render_performance_dashboard

# Not: data_repository parametresi kaldırıldı
def render_bio_analysis_page(user_role, selected_patient, detailed_patient_data):
    """
    Ana BiyoAnaliz sayfası - kullanıcı OnkoNixAI modunu seçebilir.
    """
    st.header(f"Biyoanaliz: {selected_patient.first_name} {selected_patient.last_name} - {selected_patient.patient_id}")
    
    analysis_mode = st.radio(
        "Analiz Modu Seçin:",
        ["Klasik Biyoanaliz", "OnkoNixAI - Gelişmiş AI Analizi"],
        key=f"analysis_mode_{selected_patient.patient_id}",
        horizontal=True
    )
    
    st.markdown("---")
    db_connector = DatabaseConnector()
    if not db_connector.connect():
        st.error("Veritabanı bağlantısı kurulamadı. Lütfen yöneticinize danışın.")
        return
    if analysis_mode == "OnkoNixAI - Gelişmiş AI Analizi":
        render_enhanced_bio_analysis_page(user_role, selected_patient.patient_id, selected_patient, detailed_patient_data)
        
        if user_role in ["Yönetici", "Doktor", "Radyoloji Uzmanı"]:
            with st.expander("📊 Model Performans Metrikleri"):
                render_performance_dashboard()
    
    else:
        # Not: data_repository parametresi kaldırıldı
        classic_analyzer = ClassicBioAnalyzer(
            user_role=user_role,
            patient_id=selected_patient.patient_id,
            patient_data=selected_patient,
            detailed_patient_data=detailed_patient_data,
            db_connector=db_connector
        )
        classic_analyzer.render()