# modules/bio_analysis/classic_analyzer/sections/clinical.py

import streamlit as st
import pandas as pd

def render_clinical_evaluation(patient_id, selected_visit_date, detailed_patient_data):
    """Klinik değerlendirme formunu oluşturur ve okuma/güncelleme amaçlıdır."""
    
    # st.form() bloğunun içindeki tüm elemanlar tek bir çerçeve içine alınacaktır
    with st.form(key=f"clinical_eval_form_{patient_id}_{selected_visit_date}"):
        st.subheader("Klinik Değerlendirme")
        
        clinical_cols = st.columns(2)
        clinical_eval_df = detailed_patient_data.get('Klinik Değerlendirmeler')
        
        smoking_options = {
            "Hiç Kullanmamış": "Hayatı boyunca hiç sigara içmemiş veya çok az içmiş.",
            "Eski Sigara İçicisi": "Geçmişte içmiş, ancak artık bırakmış.",
            "Aktif Sigara İçicisi": "Halen sigara içmeye devam eden.",
            "Pasif İçici": "Sigara dumanına maruz kalan, kendisi içmeyen.",
            "Diğer Tütün Ürünü Kullanıcısı": "Sigara dışındaki tütün ürünlerini kullanan.",
            "Bilinmiyor / Bilgi Yok": "Kullanım durumu hakkında bilgiye ulaşılamayan."
        }
        
        if clinical_eval_df is not None and not clinical_eval_df.empty:
            clinical_eval_row = clinical_eval_df.iloc[0]
            db_smoking_status = clinical_eval_row.get('SmokingStatus', "Bilinmiyor / Bilgi Yok")
            selected_smoking_index = list(smoking_options.keys()).index(db_smoking_status) if db_smoking_status in smoking_options else list(smoking_options.keys()).index("Bilinmiyor / Bilgi Yok")
            family_history_text = clinical_eval_row.get('FamilyHistory', '')
            comorbidities_text = clinical_eval_row.get('Comorbidities', '')
            ecog_value = int(clinical_eval_row.get('ECOG_Score', 0))
        else:
            selected_smoking_index = list(smoking_options.keys()).index("Bilinmiyor / Bilgi Yok")
            family_history_text = ""
            comorbidities_text = ""
            ecog_value = 0
            st.info("Klinik değerlendirme verisi bulunamadı.")
            
        with clinical_cols[0]:
            smoking_status = st.selectbox(
                "Sigara Kullanım Durumu",
                options=list(smoking_options.keys()),
                index=selected_smoking_index,
                help=smoking_options.get(list(smoking_options.keys())[selected_smoking_index])
            )
            family_history_input = st.text_area(
                "Aile Geçmişi", 
                value=family_history_text,
                height=100
            )
            
        with clinical_cols[1]:
            ecog_score = st.select_slider("ECOG Performans Skoru", options=[0, 1, 2, 3, 4], value=ecog_value)
            comorbidities_input = st.text_area(
                "Komorbid Hastalıklar", 
                value=comorbidities_text,
                height=100
            )
            
        submit_button = st.form_submit_button(label='Güncelle ve Kaydet')

        if submit_button:
            # Sadece görüntüleme amaçlı mesaj
            st.info("Bilgiler güncellendi!")