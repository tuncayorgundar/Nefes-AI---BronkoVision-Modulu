import streamlit as st
import pandas as pd
from datetime import datetime

def render_all_patients_page(all_patients):
    """
    Tüm hasta listesini bir tablo halinde gösterir.
    Kullanıcı hastayı bu sayfadan seçebilir.
    """
    st.title("Tüm Hastalarım")
    st.markdown("""
    Aşağıda, sisteme kayıtlı tüm hastaların listesini görebilirsiniz.
    En uzun süre gelmeyen hastalar listenin en üstünde yer almaktadır.
    Detayları görüntülemek için hasta adını veya kimlik numarasını tıklayabilirsiniz.
    """)

    if not all_patients:
        st.info("Sistemde kayıtlı hasta bulunmamaktadır.")
        return

    # Hasta nesnelerinden bir DataFrame oluşturun
    # Bu DataFrame sıralama ve seçim için gerekli tüm veriyi içerir.
    patients_df = pd.DataFrame([{
        'Hasta ID': p.patient_id,
        'Adı': p.first_name,
        'Soyadı': p.last_name,
        'Doğum Tarihi': p.date_of_birth,
        'Cinsiyet': p.gender,
        'Son Ziyaret Tarihi': max(p.visit_dates) if p.visit_dates else None
    } for p in all_patients])

    # Son ziyaret tarihini datetime formatına dönüştür
    patients_df['Son Ziyaret Tarihi'] = pd.to_datetime(patients_df['Son Ziyaret Tarihi'])
    
    # En uzun süre gelmeyenleri bulmak için sıralama anahtarını hesapla
    bugün = datetime.now().date()
    patients_df['Ziyaret Farkı'] = patients_df['Son Ziyaret Tarihi'].apply(
        lambda x: (bugün - x.date()).days if pd.notna(x) else float('inf')
    )

    # DataFrame'i ziyaret farkına göre azalan sırada sırala (en eskiden en yeniye)
    patients_df = patients_df.sort_values(by='Ziyaret Farkı', ascending=False, na_position='first')

    # Gösterilecek DataFrame'i oluştur
    # Bu DataFrame, Hasta ID'sini ve Ziyaret Farkı'nı içermez, sadece formatlanmış veriyi içerir.
    display_df = patients_df.copy()
    display_df['Son Ziyaret'] = display_df['Ziyaret Farkı'].apply(
        lambda x: f"{int(x)} gün önce" if x != float('inf') else "Hiç ziyaret etmedi"
    )
    display_df['Doğum Tarihi'] = pd.to_datetime(display_df['Doğum Tarihi']).dt.strftime('%d-%m-%Y')
    
    # Gösterilecek sütunları seç
    display_df = display_df[['Adı', 'Soyadı', 'Doğum Tarihi', 'Cinsiyet', 'Son Ziyaret']]


    # Kullanıcı bir satırı seçtiğinde çalışacak geri çağırım fonksiyonu
    def handle_patient_selection():
        selected_rows = st.session_state['patient_table_selection']['selection']['rows']
        if selected_rows:
            # Sıralanmış DataFrame'in doğru indeksini kullanarak hasta ID'sini al
            selected_index = patients_df.index[selected_rows[0]]
            selected_patient_id = patients_df.loc[selected_index]['Hasta ID']
            st.session_state.patient_selected_id = selected_patient_id
            st.success(f"Hasta ID {selected_patient_id} seçildi. Ana ekrana dönerek detaylarını görüntüleyebilirsiniz.")

    # Tabloyu göster ve geri çağırım işlevini kullan
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        on_select=handle_patient_selection,
        selection_mode='single-row',
        column_order=['Adı', 'Soyadı', 'Doğum Tarihi', 'Cinsiyet', 'Son Ziyaret'],
        key="patient_table_selection"
    )

    if not st.session_state.get('patient_table_selection', {}).get('selection', {}).get('rows'):
        st.info("Lütfen bir hasta seçin.")
