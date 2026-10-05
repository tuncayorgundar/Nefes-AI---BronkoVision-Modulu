# modules/classic_analyzer/sections/vitals.py

import streamlit as st
import pandas as pd

def render_vital_signs(patient_id, selected_visit_date, detailed_patient_data):
    """Vital bulgular formunu gösterir."""
    st.subheader("Vital Bulgular")

    # Tüm vital bulguları bir formun içine yerleştirin.
    # Bu, butona basıldığında tüm input'ların durumunu tek seferde yakalamayı sağlar.
    with st.form(key=f"vital_signs_form_{patient_id}_{selected_visit_date}"):
        vital_cols = st.columns(4)
        vital_signs_df = detailed_patient_data.get('Vital Bulgular')

        vital_signs_dict = {}
        if vital_signs_df is not None and not vital_signs_df.empty:
            vital_signs_dict = vital_signs_df.set_index('TestName')['Value'].to_dict()

        with vital_cols[0]:
            st.number_input("Kan Basıncı (Sistolik)", min_value=80, max_value=200, value=int(vital_signs_dict.get('Tansiyon (Sistolik)', 120)), key=f"bp_sys_{patient_id}_{selected_visit_date}")
            st.number_input("Kan Basıncı (Diastolik)", min_value=40, max_value=120, value=int(vital_signs_dict.get('Tansiyon (Diyastolik)', 80)), key=f"bp_dia_{patient_id}_{selected_visit_date}")
        
        with vital_cols[1]:
            st.number_input("Nabız (/dk)", min_value=40, max_value=200, value=int(vital_signs_dict.get('Nabız', 80)), key=f"pulse_{patient_id}_{selected_visit_date}")
            st.number_input("Solunum Sayısı (/dk)", min_value=8, max_value=40, value=int(vital_signs_dict.get('Solunum Sayısı', 16)), key=f"resp_{patient_id}_{selected_visit_date}")
        
        with vital_cols[2]:
            st.number_input("SpO2 (%)", min_value=70.0, max_value=100.0, value=float(vital_signs_dict.get('Oksijen Saturasyonu', 98)), key=f"spo2_{patient_id}_{selected_visit_date}")
            st.number_input("Vücut Sıcaklığı (°C)", min_value=35.0, max_value=42.0, value=float(vital_signs_dict.get('Vücut Sicakligi', 36.5)), key=f"temp_{patient_id}_{selected_visit_date}")
        
        with vital_cols[3]:
            st.number_input("Kilo (kg)", min_value=30, max_value=200, value=int(vital_signs_dict.get('Kilo', 70)), key=f"weight_{patient_id}_{selected_visit_date}")
            st.number_input("Boy (cm)", min_value=100, max_value=220, value=int(vital_signs_dict.get('Boy', 170)), key=f"height_{patient_id}_{selected_visit_date}")
        
        # Formun altına Güncelle ve Kaydet butonunu ekleyin.
        submitted = st.form_submit_button(label='Güncelle ve Kaydet')

        if submitted:
            # Butona basıldığında bir başarı mesajı gösterin.
            # Veri kaydetme mantığı buraya eklenebilir.
            st.success("Vital bulgular başarıyla güncellendi!")