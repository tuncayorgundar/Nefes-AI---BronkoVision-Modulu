# modules/classic_analyzer/sections/blood_tests.py

import streamlit as st
import pandas as pd
from ..utils.styling import highlight_anomalies

def render_blood_tests(patient_id, selected_visit_date, detailed_patient_data):
    """
    Kan testi sonuçlarını gösterir.
    Kullanıcıya anormal sonuçları veya akciğer kanseriyle ilgili testleri filtreleme seçeneği sunar.
    """
    st.subheader("Kan Testi Sonuçları")
    kan_testi_df = detailed_patient_data.get('Kan Testi', pd.DataFrame())

    # Akciğer kanseri ile ilgili testlerin listesi
    lung_cancer_tests = [
        "CEA", 
        "WBC (Beyaz Küre)", 
        "RBC (Kirmizi Küre)", 
        "Hemoglobin", 
        "Hematokrit", 
        "AST", 
        "ALT", 
        "Bilirubin (Total)", 
        "CRP", 
        "LDH", 
        "Kalsiyum (Ca)"
    ]

    col1, col2 = st.columns(2)

    with col1:
        show_anomalies_only = st.checkbox(
            "Sadece Anormal Kan Testlerini Göster",
            key=f"kan_testi_anomalies_{patient_id}_{selected_visit_date}"
        )

    with col2:
        show_lung_cancer_tests = st.checkbox(
            "Sadece Akciğer Kanseri ile İlgili Testleri Göster",
            key=f"kan_testi_akciger_kanseri_{patient_id}_{selected_visit_date}"
        )

    df_to_display = kan_testi_df.copy()

    # Eğer anormallik filtresi seçiliyse, normal sonuçları kaldır
    if show_anomalies_only:
        df_to_display = df_to_display[df_to_display['Status'] != 'Normal']

    # Eğer akciğer kanseri filtresi seçiliyse, sadece ilgili testleri göster
    if show_lung_cancer_tests:
        df_to_display = df_to_display[df_to_display['Test Adı'].isin(lung_cancer_tests)]

    if df_to_display.empty:
        st.info("Gösterilecek kan testi sonucu bulunmamaktadır.")
    else:
        # Sonuçları Streamlit'te göster ve anormal değerleri vurgula
        st.dataframe(
            df_to_display.style.apply(highlight_anomalies, axis=1), 
            use_container_width=True
        )