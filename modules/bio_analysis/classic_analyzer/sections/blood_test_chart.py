# modules/bio_analysis/classic_analyzer/sections/blood_test_chart.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# Yardımcı fonksiyon: Referans aralığını sayısal değerlere çevirir
def parse_reference_range(range_str):
    if not isinstance(range_str, str):
        return None, None
        
    range_str = range_str.strip()

    # '2.3-4.2' gibi aralıkları yakala
    match = re.match(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", range_str)
    if match:
        lower = float(match.group(1))
        upper = float(match.group(2))
        return lower, upper

    # '>5.4' gibi büyük değerleri yakala
    match = re.match(r">\s*(\d+\.?\d*)", range_str)
    if match:
        lower = float(match.group(1))
        return lower, None

    # '<4.0' gibi küçük değerleri yakala
    match = re.match(r"<\s*(\d+\.?\d*)", range_str)
    if match:
        upper = float(match.group(1))
        return None, upper
    
    # "Normal", "Negatif" gibi metinleri ve diğer sayıları işle
    try:
        val = float(range_str)
        return val, val
    except (ValueError, TypeError):
        return None, None

class BloodTestChart:
    def __init__(self, patient_id, all_blood_tests_df):
        self.patient_id = patient_id
        self.all_blood_tests_df = all_blood_tests_df

    def render(self):
        """Kan değerleri değişim grafiği bölümünü açılır kapanır bir şekilde render eder."""
        
        # İçeriği bir expander içine alın
        with st.expander("Kan Değerleri Değişim Grafiğini Göster", expanded=False):
            if self.all_blood_tests_df.empty:
                st.info("Grafik oluşturmak için hasta geçmişine ait kan testi verisi yok.")
                return

            all_test_names = self.all_blood_tests_df['Test Adı'].unique()
            selected_test = st.selectbox(
                "Grafikte Gösterilecek Kan Değerini Seçin:",
                options=all_test_names,
                key=f"chart_select_{self.patient_id}"
            )

            if selected_test:
                test_history_df = self.all_blood_tests_df[self.all_blood_tests_df['Test Adı'] == selected_test].copy()
                
                if not test_history_df.empty:
                    test_history_df['Sonuç'] = pd.to_numeric(test_history_df['Sonuç'], errors='coerce')
                    test_history_df['Tarih'] = pd.to_datetime(test_history_df['Tarih'])
                    test_history_df.dropna(subset=['Sonuç'], inplace=True)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=test_history_df['Tarih'],
                        y=test_history_df['Sonuç'],
                        mode='lines+markers',
                        name='Sonuç Değeri',
                        marker=dict(color='royalblue', size=8),
                        line=dict(width=2)
                    ))

                    ref_range_str = test_history_df['Referans aralığı'].iloc[0]
                    lower_bound, upper_bound = parse_reference_range(ref_range_str)

                    if lower_bound is not None and upper_bound is not None:
                        fig.add_hrect(
                            y0=lower_bound, 
                            y1=upper_bound, 
                            fillcolor="lightgreen", 
                            opacity=0.3, 
                            line_width=0, 
                            annotation_text="Normal Aralık", 
                            annotation_position="top left"
                        )
                    elif lower_bound is not None:
                        fig.add_hrect(
                            y0=lower_bound,
                            y1=test_history_df['Sonuç'].max() + (test_history_df['Sonuç'].max() - lower_bound) * 0.1,
                            fillcolor="lightcoral",
                            opacity=0.3,
                            line_width=0,
                            annotation_text=f"Normal Aralık > {lower_bound}",
                            annotation_position="top left"
                        )
                    elif upper_bound is not None:
                        fig.add_hrect(
                            y0=test_history_df['Sonuç'].min() - (upper_bound - test_history_df['Sonuç'].min()) * 0.1,
                            y1=upper_bound,
                            fillcolor="lightcoral",
                            opacity=0.3,
                            line_width=0,
                            annotation_text=f"Normal Aralık < {upper_bound}",
                            annotation_position="top left"
                        )
                    
                    fig.update_layout(
                        title=f"{selected_test} Değerinin Zaman İçindeki Değişimi",
                        xaxis_title="Ziyaret Tarihi",
                        yaxis_title="Değer",
                        title_x=0.5
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"'{selected_test}' testine ait geçmiş veri bulunamadı.")