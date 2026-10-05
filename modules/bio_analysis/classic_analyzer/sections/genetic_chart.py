# modules/classic_analyzer/sections/genetic_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px

class GeneticChart:
    def __init__(self, patient_id, all_genetic_markers_df):
        self.patient_id = patient_id
        self.all_genetic_markers_df = all_genetic_markers_df.copy()

    def render(self):
        """Genetik biyobelirteç sonuçlarının zaman içindeki değişimini gösteren bir grafik oluşturur."""
        
        # 'Değer' sütununu sayısal bir türe dönüştür
        self.all_genetic_markers_df['Değer'] = pd.to_numeric(self.all_genetic_markers_df['Değer'], errors='coerce')
        
        # Sadece sayısal değere sahip olanları filtrele
        df_for_charting = self.all_genetic_markers_df.dropna(subset=['Değer'])

        if df_for_charting.empty:
            st.info("Grafik oluşturmak için sayısal genetik biyobelirteç verisi bulunmamaktadır.")
            return

        # Grafikte gösterilecek biyobelirteçleri seçmek için dropdown menüsü
        # Sadece sayısal değere sahip olanları göster
        all_test_names = sorted(df_for_charting['Biyobelirteç'].unique())
        selected_test = st.selectbox(
            "Zaman İçinde Takip Edilecek Genetik Biyobelirteci Seçin:",
            options=all_test_names,
            key=f"genetic_chart_select_{self.patient_id}"
        )

        if selected_test:
            # Seçilen testin tüm zamanlardaki verilerini filtrele
            test_history_df = df_for_charting[df_for_charting['Biyobelirteç'] == selected_test].copy()
            
            if not test_history_df.empty:
                # Veri tiplerini doğru formata dönüştür
                test_history_df['Tarih'] = pd.to_datetime(test_history_df['Tarih'])
                
                # Plotly Express ile çizgi grafiği oluştur
                fig = px.line(
                    test_history_df,
                    x='Tarih',
                    y='Değer',
                    title=f"{selected_test} Biyobelirtecinin Zaman İçindeki Değişimi",
                    markers=True,  # Veri noktalarını göster
                )
                
                fig.update_layout(
                    xaxis_title="Ziyaret Tarihi",
                    yaxis_title="Değer",
                    title_x=0.5
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"'{selected_test}' biyobelirtecine ait sayısal veri bulunamadı.")