# dosya: modules/patient_dash/subpages/dosage_optimization.py

import streamlit as st
import pandas as pd
import plotly.express as px

def render_dosage_optimization_page(selected_patient, detailed_patient_data):
    """
    Doz Optimizasyonu sayfasını render eder.
    Tedavi şemaları ve doz ayarlamaları verilerini tablo ve grafik halinde gösterir.
    """
    st.title("Doz Optimizasyonu")
    st.subheader(f"Hasta: {selected_patient.first_name} {selected_patient.last_name}")

    if selected_patient and detailed_patient_data:
        # Tedavi şemaları verilerini çek
        regimens_df = detailed_patient_data.get('Tedavi Şemaları', pd.DataFrame())
        
        # Doz ayarlamaları verilerini çek
        dose_adjustments_df = detailed_patient_data.get('Doz Ayarlamaları', pd.DataFrame())

        # --- Tedavi Şemaları Tablosu ---
        if not regimens_df.empty:
            st.subheader("Tedavi Şemaları")
            display_regimens_df = regimens_df[['RegimenName', 'StartDate', 'EndDate', 'ProtocolDescription', 'CurrentStatus']].copy()
            display_regimens_df.columns = ['Şema Adı', 'Başlangıç Tarihi', 'Bitiş Tarihi', 'Protokol Açıklaması', 'Durum']
            for col in ['Başlangıç Tarihi', 'Bitiş Tarihi']:
                display_regimens_df[col] = pd.to_datetime(display_regimens_df[col]).dt.strftime('%d-%m-%Y')
            st.dataframe(display_regimens_df, use_container_width=True, hide_index=True)
        else:
            st.info("Bu hastaya ait kayıtlı bir tedavi şeması bulunamadı.")

        st.markdown("---")

        # --- Doz Ayarlama Geçmişi (Grafik ve Tablo) ---
        if not dose_adjustments_df.empty:
            st.subheader("Doz Ayarlama Geçmişi")
            
            medications = dose_adjustments_df['MedicationName'].unique()
            
            # Seçilen ilacı burada belirliyoruz
            selected_medication = st.selectbox(
                "Görüntülemek istediğiniz ilacı seçin:",
                options=medications,
                key="dos_opt_graph_med_select"
            )

            # Grafiği çağırırken seçilen ilacı gönderiyoruz
            render_dose_adjustment_graph(dose_adjustments_df, selected_medication)
            
            st.markdown("---")
            
            # Tabloyu çağırırken seçilen ilacı gönderiyoruz
            render_dose_adjustment_history(dose_adjustments_df, selected_medication)
            
        else:
            st.info("Bu hastaya ait herhangi bir doz ayarlama kaydı bulunamadı.")
            
    else:
        st.warning("Lütfen sol menüden bir hasta seçin veya detaylı verilerin mevcut olduğundan emin olun.")

# --- Yardımcı Fonksiyonlar ---

def render_dose_adjustment_graph(dose_adjustments_df, selected_medication):
    """
    Doz ayarlamalarını zaman içinde grafiksel olarak gösterir.
    """
    plot_df = dose_adjustments_df.copy()
    plot_df['AdjustmentDate'] = pd.to_datetime(plot_df['AdjustmentDate'])
    
    # Seçilen ilaca göre veriyi filtrele
    filtered_df = plot_df[plot_df['MedicationName'] == selected_medication].sort_values('AdjustmentDate')

    if filtered_df.empty:
        st.warning("Seçilen ilaç için doz ayarlama verisi bulunamadı.")
        return

    melted_df = filtered_df.melt(
        id_vars=['AdjustmentDate', 'CycleNumber'], 
        value_vars=['OriginalDose_mg_per_m2', 'AdjustedDose_mg_per_m2'],
        var_name='DoseType', 
        value_name='Doz (mg/m²)'
    )
    
    fig = px.line(
        melted_df,
        x="AdjustmentDate",
        y="Doz (mg/m²)",
        color="DoseType",
        title=f"{selected_medication} Doz Değişimi",
        markers=True,
        labels={
            "AdjustmentDate": "Ayarlama Tarihi",
            "Doz (mg/m²)": "Doz (mg/m²)",
            "DoseType": "Doz Tipi"
        },
        hover_data={'DoseType': False, 'Doz (mg/m²)': ':.2f', 'CycleNumber': True}
    )
    fig.update_layout(xaxis_title="Ayarlama Tarihi", yaxis_title="Doz (mg/m²)", title_x=0.5)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(tickformat="%b %d, %Y")

    st.plotly_chart(fig, use_container_width=True, key="dos_opt_plotly_chart")

def render_dose_adjustment_history(dose_adjustments_df, selected_medication):
    """
    Doz ayarlama geçmişini tablo ve detaylarıyla birlikte gösterir.
    """
    # Seçilen ilaca göre veriyi filtrele
    filtered_df = dose_adjustments_df[dose_adjustments_df['MedicationName'] == selected_medication].sort_values('AdjustmentDate').copy()

    if filtered_df.empty:
        st.info("Seçilen ilaç için doz ayarlama geçmişi bulunamadı.")
        return

    # Tablo başlıkları için sütunları tanımla
    header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 1, 1, 1, 1, 0.5])
    
    header_col1.markdown('**Kür No**')
    header_col2.markdown('**Ayarlama Tarihi**')
    header_col3.markdown('**İlaç Adı**')
    header_col4.markdown('**Orijinal Doz**')
    header_col5.markdown('**Ayarlanmış Doz**')
    header_col6.markdown('**Detaylar**')
    
    st.markdown("---")
    
    # Her satır için döngü oluştur
    for index, row in filtered_df.iterrows():
        row_col1, row_col2, row_col3, row_col4, row_col5, row_col6 = st.columns([1, 1, 1, 1, 1, 0.5])
        
        row_col1.write(row['CycleNumber'])
        row_col2.write(row['AdjustmentDate'].strftime('%d-%m-%Y'))
        row_col3.write(row['MedicationName'])
        row_col4.write(f"{row['OriginalDose_mg_per_m2']} mg/m²")
        row_col5.write(f"{row['AdjustedDose_mg_per_m2']} mg/m²")

        with row_col6:
            if st.button("Detaylar", key=f"btn_{row['AdjustmentID']}_dos_opt"):
                st.session_state.selected_adjustment_opt = row.to_dict()
                
    st.markdown("---")

    # Eğer bir buton tıklandıysa, detayları göster
    if 'selected_adjustment_opt' in st.session_state and st.session_state.selected_adjustment_opt:
        selected_data = st.session_state.selected_adjustment_opt
        
        st.subheader("Seçilen Doz Ayarlaması Detayları")
        
        st.markdown(f"**Ayarlama ID:** `{selected_data['AdjustmentID']}`")
        st.markdown(f"**Ayarlama Nedeni:** {selected_data['AdjustmentReason']}")
        st.markdown(f"**Yan Etki:** {selected_data['Symptom']}")
        st.markdown(f"**Laboratuvar Sonuçları:** {selected_data['LabResults']}")
        st.markdown(f"**ECOG Performans Durumu:** {selected_data['ECOG_PerformanceStatus']}")
    else:
        st.info("Detayları görmek için 'Detaylar' butonuna tıklayın.")