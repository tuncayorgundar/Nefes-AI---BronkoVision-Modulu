# mainapp.py
# Ana uygulama dosyası

import base64
import streamlit as st
import os
import pandas as pd
from datetime import datetime

from database_connector import DatabaseConnector
from repositories.detailed_data_repository import DetailedDataRepository
from repositories.patient_repository import PatientRepository

# UI bileşenlerini import edin
from ui_components import topbar, sidebar
from modules import demo_presentation

# --- Helper Fonksiyonları ---

def get_image_as_base64(path):
    """Belirtilen yoldaki bir görüntüyü base64 formatına dönüştürür."""
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"Görüntü dosyası bulunamadı: {path}")
        return None

# mainapp.py dosyanızdaki get_data_from_db fonksiyonunun güncellenmiş hali

@st.cache_data(ttl=3600)
def get_data_from_db():
    """
    Veritabanından tüm hasta verilerini ve detaylı verileri çeker ve doğru bir yapıda organize eder.
    """
    db_connector = DatabaseConnector()
    if not db_connector.connect():
        st.error("Veritabanı bağlantısı başarısız. Lütfen ayarları kontrol edin.")
        return None, None

    try:
        patient_repo = PatientRepository(db_connector)
        all_patients = patient_repo.get_all_patients()
        
        if not all_patients:
            st.warning("Veritabanında hiç hasta bulunamadı.")
            return [], {}

        detailed_repo = DetailedDataRepository(db_connector)
        all_detailed_data = {}

        for patient in all_patients:
            # Hastanın tüm detaylı verilerini tutacak ana sözlük
            patient_detailed_data = {}

            # Hastanın tüm ziyaret tarihlerini çekin
            visit_dates = patient.visit_dates
            
            # Reponun ziyaretten bağımsız olarak çektiği ilaç verilerini buraya ekleyin
            regimens_df = detailed_repo.medication_repo.get_patient_regimens(patient.patient_id)
            all_adjustments = []
            if not regimens_df.empty:
                for regimen_id in regimens_df['RegimenID']:
                    adjustments = detailed_repo.medication_repo.get_regimen_adjustments(regimen_id)
                    if not adjustments.empty:
                        all_adjustments.append(adjustments)
                if all_adjustments:
                    dose_adjustments_df = pd.concat(all_adjustments, ignore_index=True)
                else:
                    dose_adjustments_df = pd.DataFrame()
            else:
                dose_adjustments_df = pd.DataFrame()

            patient_detailed_data['Tedavi Şemaları'] = regimens_df
            patient_detailed_data['Doz Ayarlamaları'] = dose_adjustments_df
            
            # Her bir ziyaret için detaylı verileri çekip ana sözlüğe ekleyin
            for visit_date_obj in visit_dates:
                visit_date_str = visit_date_obj.strftime('%Y-%m-%d')
                data_for_visit = detailed_repo.get_detailed_data_for_visit(patient.patient_id, visit_date_str)
                patient_detailed_data[visit_date_str] = data_for_visit

            
            all_detailed_data[patient.patient_id] = patient_detailed_data

        return all_patients, all_detailed_data
    
    finally:
        db_connector.close_connection()

        
# --- Streamlit Uygulama Yapılandırması ---
try:
    icon_path = os.path.join("assets", "logo_transparent.png")
    app_icon = get_image_as_base64(icon_path)
    
    st.set_page_config(
        page_title="NefesAI",
        page_icon=app_icon,
        layout="wide",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    st.error(f"Uygulama yapılandırması sırasında bir hata oluştu: {e}")
    st.set_page_config(page_title="NefesAI", layout="wide")

# --- Ana Uygulama Mantığı ---
logo_path = os.path.join("assets", "logo_transparent.png")

# Veritabanından verileri çek ve önbelleğe al
all_patients, detailed_data_by_patient = get_data_from_db()

# Veri çekilemediyse uygulamayı durdur
if all_patients is None:
    st.stop()

# patient_selected_id'yi oturum durumunda saklayın
if 'patient_selected_id' not in st.session_state:
    st.session_state.patient_selected_id = None

# Kenar çubuğunu render et ve kullanıcı seçimlerini al
user_role, patient_selected_from_sidebar = sidebar.render_sidebar(all_patients, logo_path)

# Eğer kenar çubuğundan bir hasta seçildiyse, oturum durumunu güncelleyin
if patient_selected_from_sidebar is not None and patient_selected_from_sidebar != st.session_state.patient_selected_id:
    st.session_state.patient_selected_id = patient_selected_from_sidebar

# Artık ana mantık için oturum durumundaki değişkeni kullanın
if st.session_state.patient_selected_id is not None:
    # Seçilen hasta için detaylı verileri al
    selected_patient = next((p for p in all_patients if p.patient_id == st.session_state.patient_selected_id), None)
    selected_patient_detailed_data = detailed_data_by_patient.get(st.session_state.patient_selected_id, {})
    topbar.render_full_ui(user_role, st.session_state.patient_selected_id, all_patients, selected_patient_detailed_data)
else:
    demo_presentation.render_demo_presentation()
