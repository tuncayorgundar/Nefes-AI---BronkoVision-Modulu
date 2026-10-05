# modules/classic_analyzer/sections/treatment.py

import streamlit as st

def render_treatment_response(patient_id, selected_visit_date, detailed_patient_data):
    """Tedavi yanıtı formunu gösterir."""
    st.subheader("Tedavi Yanıtı")
    response_cols = st.columns(3)

    with response_cols[0]:
        st.selectbox(
            "RECIST Kriterleri",
            ["Tam Yanıt (CR)", "Kısmi Yanıt (PR)", "Stabil Hastalık (SD)", "Progresif Hastalık (PD)"],
            key=f"recist_{patient_id}_{selected_visit_date}"
        )
    with response_cols[1]:
        st.number_input("Tümör Boyutu Değişimi (%)", -100, 100, 0, key=f"tumor_change_{patient_id}_{selected_visit_date}")
    with response_cols[2]:
        st.selectbox(
            "Yan Etki Değerlendirmesi (CTCAE)",
            ["Grade 0", "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"],
            key=f"toxicity_{patient_id}_{selected_visit_date}"
        )