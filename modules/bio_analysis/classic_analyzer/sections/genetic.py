import streamlit as st
import pandas as pd
from ..utils.styling import highlight_positive_results

def render_genetic_markers(patient_id, selected_visit_date, detailed_patient_data):
    """Genetik biyobelirteç sonuçlarını kategorilere göre filtreleyerek gösterir."""
    st.subheader("Genetik Biyobelirteçler")
    genetik_df = detailed_patient_data.get('Genetik Biyobelirteçler', pd.DataFrame())

    if genetik_df.empty:
        st.info("Genetik biyobelirteç verisi bulunmamaktadır.")
        return

    # Kategori tanımlamaları
    categories = {
        "Tüm Biyobelirteçler": genetik_df['Biyobelirteç'].tolist(),
        "Akciğer Kanserinde Hedefe Yönelik Tedavi": ["EGFR", "ALK", "ROS1", "BRAF", "KRAS", "HER2"],
        "Akciğer Kanserinde İmmünoterapi": ["PD-L1", "TMB", "MSI"],
        "Genel Kanser Gelişimi": ["TP53"],
        "Diğer Kanserlerle İlişkili": ["BRCA1", "BRCA2", "PIK3CA", "IDH1", "IDH2"]
    }

    # Dropdown menüsü oluştur
    selected_category = st.selectbox(
        "Görüntülenecek Kategori:",
        options=list(categories.keys()),
        key=f"genetic_category_{patient_id}_{selected_visit_date}"
    )

    # Seçilen kategoriye göre veriyi filtrele
    markers_to_show = categories.get(selected_category, [])
    filtered_df = genetik_df[genetik_df['Biyobelirteç'].isin(markers_to_show)]

    # Anormal sonuçları filtreleme checkbox'ı
    show_positive_only = st.checkbox(
        "Sadece Pozitif Biyobelirteçleri Göster",
        key=f"genetik_positive_{patient_id}_{selected_visit_date}"
    )
    
    if show_positive_only:
        filtered_df = filtered_df[filtered_df['Result'] == 'Pozitif']

    # Filtrelenmiş DataFrame'i göster
    if filtered_df.empty:
        st.info("Bu kategori için gösterilecek veri bulunmamaktadır.")
    else:
        st.dataframe(filtered_df.style.apply(highlight_positive_results, axis=1), use_container_width=True)