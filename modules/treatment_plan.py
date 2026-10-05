import streamlit as st
import pandas as pd
from datetime import datetime

def render_treatment_plan_page(user_role, selected_patient, detailed_patient_data):
    """
    Tedavi Planı sayfasının içeriğini render eder.
    'selected_patient': seçilen hasta nesnesi
    'detailed_patient_data': seçilen hastanın tüm ziyaretlerine ait detaylı veriler sözlüğü
    """
    if not selected_patient:
        st.warning("Lütfen tedavi planlarını görüntülemek için bir hasta seçin.")
        return

    patient_name = f"{selected_patient.first_name} {selected_patient.last_name}"
    patient_id = selected_patient.patient_id # for key generation if needed

    st.header(f"Tedavi Planı: {patient_name}")
    st.write(f"**{patient_name}** için mevcut ve geçmiş tedavi planları burada yönetilir.")
    st.write("---")

    # Doktorlar için bir tedavi planı formu
    if user_role in ["Doktor", "Yönetici"]:
        st.subheader("Yeni Tedavi Planı Oluştur")
        with st.form("treatment_plan_form", clear_on_submit=True):
            treatment_type = st.selectbox(
                "Tedavi Tipi",
                ["Kemoterapi", "Radyoterapi", "Cerrahi", "İmmünoterapi", "Hedefli Tedavi"],
                key=f"treatment_type_{patient_id}"
            )
            treatment_details = st.text_area(
                "Tedavi Detayları ve İlaç Bilgileri",
                key=f"treatment_details_{patient_id}"
            )
            start_date = st.date_input(
                "Başlangıç Tarihi",
                datetime.today(),
                key=f"start_date_{patient_id}"
            )
            end_date = st.date_input(
                "Bitiş Tarihi",
                datetime.today(),
                key=f"end_date_{patient_id}"
            )

            submitted = st.form_submit_button("Planı Kaydet")
            if submitted:
                # Burası, tedavi planını veritabanına veya veri yapısına kaydedeceğiniz yerdir.
                # Şu an için sadece başarı mesajı gösteriliyor ve konsola yazdırılıyor.
                # Gerçek bir uygulamada, bu verileri DetailedDataRepository üzerinden veritabanına kaydetmeniz gerekir.
                st.success(f"Tedavi planı başarıyla kaydedildi: **{treatment_type}**")
                st.json({
                    "patient_id": selected_patient.patient_id,
                    "visit_date": datetime.today().strftime('%Y-%m-%d'), # Genellikle yeni planlar mevcut güne kaydedilir
                    "Tedavi Tipi": treatment_type,
                    "Detaylar": treatment_details,
                    "Başlangıç": str(start_date),
                    "Bitiş": str(end_date)
                })

    # Geçmiş tedavi planlarını görüntüleme
    st.subheader("Geçmiş Tedavi Planları")
    
    all_treatment_plans_df = []
    if detailed_patient_data:
        for visit_date_str, visit_data in detailed_patient_data.items():
            if 'treatment_plan' in visit_data and not visit_data['treatment_plan'].empty:
                # Ziyaret tarihini DataFrame'e ekleyelim
                temp_df = visit_data['treatment_plan'].copy()
                temp_df['Ziyaret Tarihi'] = datetime.strptime(visit_date_str, '%Y-%m-%d').strftime('%d.%m.%Y')
                all_treatment_plans_df.append(temp_df)

    if all_treatment_plans_df:
        combined_df = pd.concat(all_treatment_plans_df, ignore_index=True)
        
        # Sütun isimlerini okunur hale getirelim (örneğin 'plan_id' yerine 'Plan ID' gibi)
        # Eğer DataFrame'lerinizde farklı sütun isimleri varsa, burayı düzenlemeniz gerekebilir.
        column_mapping = {
            'plan_id': 'Plan ID',
            'treatment_type': 'Tedavi Tipi',
            'details': 'Detaylar',
            'start_date': 'Başlangıç Tarihi',
            'end_date': 'Bitiş Tarihi',
            'status': 'Durum'
        }
        
        # Sadece mevcut sütunları eşlemeye çalışın
        display_df = combined_df.rename(columns={k: v for k, v in column_mapping.items() if k in combined_df.columns})
        
        # Tarih sütunlarını formatlayalım
        for col in ['Başlangıç Tarihi', 'Bitiş Tarihi']:
            if col in display_df.columns:
                display_df[col] = pd.to_datetime(display_df[col]).dt.strftime('%d.%m.%Y')

        st.dataframe(display_df.set_index('Plan ID') if 'Plan ID' in display_df.columns else display_df, use_container_width=True)
    else:
        st.info("Bu hasta için kayıtlı geçmiş tedavi planı bulunmamaktadır.")