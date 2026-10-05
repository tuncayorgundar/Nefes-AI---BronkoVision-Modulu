# ui_components/topbar.py
# UI bileşenleri için üst çubuk (topbar) bileşeni

import streamlit as st
from modules import dosage_optimization, home, treatment_plan, demo_presentation
from modules.bio_analysis import bio_analysis_page
from modules.image_analysis_page.image_analysis import analysis_workflow_page
from modules import all_patients as all_patients_module # Yeni modülü import edin ve ismini değiştirin

def render_full_ui(user_role, patient_selected_id, all_patients, detailed_patient_data):
    """
    Kullanıcı rolüne göre sekmeleri (tab) oluşturur ve içeriklerini render eder.
    """
    tabs_to_show = []
    tab_content_funcs = []
    
    # Tüm kullanıcılar için "Uygulama Hakkında" sekmesi
    tabs_to_show.append("Uygulama Hakkında")
    tab_content_funcs.append(lambda: demo_presentation.render_demo_presentation())

    # Seçilen hastayı all_patients listesinden bul
    selected_patient = next((p for p in all_patients if p.patient_id == patient_selected_id), None)
    # Doktorlar için 'Tüm Hastalarım' sekmesini ekleyin
    if user_role in ["Doktor", "Yönetici"]:
        tabs_to_show.append("Tüm Hastalarım")
        tab_content_funcs.append(lambda: all_patients_module.render_all_patients_page(all_patients))
    # Rol bazlı sekmeler
      # Rol bazlı sekmeler
    if user_role in ["Doktor", "Yönetici"]:
        tabs_to_show.append("Ana Ekran")
        tab_content_funcs.append(lambda: (
            home.render_home_page(selected_patient),
            home.render_general_overview(selected_patient, detailed_patient_data)
        ))

    if user_role in ["Doktor", "Yönetici", "Laboratuvar Uzmanı"]:
        tabs_to_show.append("Biyoanaliz")
        tab_content_funcs.append(lambda: bio_analysis_page.render_bio_analysis_page(user_role, selected_patient, detailed_patient_data))

    if user_role in ["Doktor", "Yönetici", "Radyoloji Uzmanı"]:
        tabs_to_show.append("Görüntü Analizi ")
        tab_content_funcs.append(lambda: analysis_workflow_page(user_role, selected_patient, detailed_patient_data))
    
        
    if user_role in ["Doktor", "Yönetici", "Eczacı"]:
        tabs_to_show.append("Doz Optimizasyonu")
        tab_content_funcs.append(lambda: dosage_optimization.render_dosage_optimization_page(selected_patient, detailed_patient_data))

    if user_role in ["Doktor", "Yönetici"]:
        tabs_to_show.append("Tedavi Planı")
        tab_content_funcs.append(lambda: treatment_plan.render_treatment_plan_page(user_role, selected_patient, detailed_patient_data))

    # Sekmeleri oluştur ve içeriklerini render et
    tabs = st.tabs(tabs_to_show)

    for tab, func in zip(tabs, tab_content_funcs):
        with tab:
            func()