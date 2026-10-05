# modules/bio_analysis/classic_analyzer/analyzer.py

import streamlit as st
import pandas as pd
from datetime import datetime
import warnings

from modules.bio_analysis.classic_analyzer.sections import genetic_chart
from repositories.detailed_data_repository import DetailedDataRepository

# Sections ve utils paketlerini doğru şekilde import edin
from .sections import blood_tests, genetic, clinical, vitals, treatment, blood_test_chart
from .utils import styling

# pandas'tan gelen UserWarning'leri görmezden gelir
warnings.filterwarnings('ignore')

# Not: data_repository parametresi kaldırıldı
class ClassicBioAnalyzer:
    def __init__(self, user_role, patient_id, patient_data, detailed_patient_data,db_connector):
        self.user_role = user_role
        self.patient_id = patient_id
        self.patient_data = patient_data
        self.detailed_patient_data = detailed_patient_data
        self.data_repo = DetailedDataRepository(db_connector)
        

    def render(self):
        """Kapsamlı klasik biyolojik analiz ekranını oluşturur."""
        
        visit_dates_str = [d.strftime('%Y-%m-%d') for d in self.patient_data.visit_dates]
        
        if not visit_dates_str:
            st.info("Bu hasta için ziyaret tarihi bulunmamaktadır.")
            return

        selected_visit_date = st.selectbox(
            "Ziyaret Tarihi Seçin:",
            options=visit_dates_str,
            index=len(visit_dates_str) - 1,
            key=f"classic_bio_date_select_{self.patient_id}"
        )

        patient_details_for_selected_date = self.detailed_patient_data.get(selected_visit_date, {})
        
        if not patient_details_for_selected_date:
            st.warning(f"Seçilen tarih için detaylı veri bulunamadı.")
            return
        
        # Tüm kan testleri verisini çek
        all_blood_tests_df = self.data_repo.get_all_blood_tests_for_patient(self.patient_id)
        
        # Fonksiyon çağrıları ile her bir bölümü render etme
        blood_tests.render_blood_tests(self.patient_id, selected_visit_date, patient_details_for_selected_date)
        
        chart_renderer = blood_test_chart.BloodTestChart(self.patient_id, all_blood_tests_df)
        chart_renderer.render()
        
        genetic.render_genetic_markers(self.patient_id, selected_visit_date, patient_details_for_selected_date)
                # ---
        # Yeni genetik grafik verisini çek ve grafiği render et
        all_genetic_markers_df = self.data_repo.get_all_genetic_markers_for_patient(self.patient_id)
        genetic_chart_renderer = genetic_chart.GeneticChart(self.patient_id, all_genetic_markers_df)
        with st.expander("Genetik Biyobelirteç Zaman Çizelgesini Göster", expanded=False):
             genetic_chart_renderer.render()
        # ---
        # Not: data_repository parametresi kaldırıldı
        clinical.render_clinical_evaluation(self.patient_id, selected_visit_date, patient_details_for_selected_date)
        
        vitals.render_vital_signs(self.patient_id, selected_visit_date, patient_details_for_selected_date)
        treatment.render_treatment_response(self.patient_id, selected_visit_date, patient_details_for_selected_date)