# modules/image_analysis.py
from datetime import datetime
import streamlit as st
from PIL import Image
import os
import tempfile
import shutil
from .pipeline import BronkoVisionPipeline
import streamlit.components.v1 as components


# --- YOL TANIMLAMALARI (Değişiklik yok) ---
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(MODULES_DIR, "models")
RESNET_PATH = os.path.join(MODELS_DIR, 'best_model_resnet.pth')
UNET_PATH = os.path.join(MODELS_DIR, 'best_model_unet.pth')
POINTNET_PATH = os.path.join(MODELS_DIR, 'pointnet_autoencoder_final.pth')

@st.cache_resource
def load_pipeline():
    """Pipeline nesnesini modellerle birlikte bir kez yükler."""
    pipeline = BronkoVisionPipeline(RESNET_PATH, UNET_PATH, POINTNET_PATH)
    return pipeline

def analysis_workflow_page(user_role, selected_patient, detailed_patient_data):

    patient_name = f"{selected_patient.first_name} {selected_patient.last_name}"
    patient_id = selected_patient.patient_id
    st.write(f"**{patient_name}** için akciğer röntgeni veya BT görüntülerinin yapay zeka destekli analizini yapın.")
    
    pipeline = load_pipeline()
    
    TARGET_IMAGE_WIDTH = 350
        
    image_history = []
    if detailed_patient_data:
        for visit_date_str, visit_data in detailed_patient_data.items():
            try:
                datetime.strptime(visit_date_str, '%Y-%m-%d')
                
                if 'Görüntü Analizleri' in visit_data and not visit_data['Görüntü Analizleri'].empty:
                    for index, row in visit_data['Görüntü Analizleri'].iterrows():
                        sketchfab_url = row.get('sketchfab_model_url', '3D görüntüleme eklenecektir.')
                        diagnosis_notes = row.get('diagnosis_notes', 'Analiz notu bulunamadı.')
                        
                        image_history.append({
                            'Tarih': datetime.strptime(visit_date_str, '%Y-%m-%d').strftime('%d.%m.%Y'),
                            'Analiz Notları': diagnosis_notes,
                            'Analiz Sonuçları': {
                                'Tespit Edilen Anomaliler': row.get('anomalies_detected', 'N/A'),
                                'Tümör Boyut ve Hacim Ölçümleri': row.get('tumor_size_and_volume', 'N/A'),
                                'Zaman Serisi Analizi': row.get('time_series_analysis', 'N/A'),
                                'Risk Derecelendirmesi': row.get('risk_rating', 'N/A'),
                                '3D Görüntüleme': sketchfab_url
                            }
                        })
            except ValueError:
                continue

    
    if user_role in ["Doktor", "Yönetici", "Radyoloji Uzmanı"]:
        
        st.subheader("Geçmiş Analizleri İncele")
        if image_history:
            history_options = [f"{item['Tarih']}" for item in image_history]
            
            selected_history = st.selectbox(
                "Geçmiş Bir Analiz Seçin:",
                history_options,
                key=f"image_history_select_{patient_id}_{len(history_options)}"
            )
            
            if selected_history:
                selected_item_index = history_options.index(selected_history)
                selected_item = image_history[selected_item_index]
                
                with st.expander(f"**Rapor Tarihi: {selected_item['Tarih']}**", expanded=True):
                    
                    st.subheader("Analiz Sonuçları")
                    
                    report_data = {
                        "Tespit": "Tümör tespit edildi.",
                        "Boyut (Piksel)": "2111",
                        "Boyut (Yüzde)": "4.21%",
                        "Konum (Merkez)": "( 123, 456 )",
                        "Şekil (Yuvarlaklık)": "0.7487",
                        "Şekil (En-Boy Oranı)": "0.7627",
                        "Şekil (Uzantı)": "0.7637",
                        "Renk (Ortalama RGB)": "(46.2, 62.8, 111.5)",
                        "Doku (Ortalama Parlaklık)": "63.37",
                        "Doku (Kontrast)": "14.6701",
                        "Doku (Homojenlik)": "0.9670"
                    }

                    cols = st.columns(2)
                    col_index = 0
                    for key, value in report_data.items():
                        with cols[col_index % 2]:
                            st.markdown(f"**{key}:** {value}")
                        col_index += 1

                    st.markdown("---")
                    
                    sketchfab_url_to_embed = selected_item['Analiz Sonuçları']['3D Görüntüleme']
                    
                    st.markdown("### Görsel Analiz Özeti")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        with st.container(border=True):
                            st.write("**1. Aşama: Sınıflandırma Sonucu**")  
                            st.image("assets/image_analysis/resnet.png", caption="ResNet Dikkat Haritası", use_container_width=True)
                            st.markdown("**Tespit:** Lung cancer")
                            st.markdown("**Güven Skoru:** %99.94")
                            with st.expander("Detaylar"):
                                for key, value in report_data.items():
                                    if "Tespit" in key or "Boyut" in key:
                                        st.markdown(f"**{key}:** {value}")
                    with col2:
                        with st.container(border=True):
                            st.write("**2D Segmentasyon**")
                            st.image("assets/image_analysis/unet.png", caption="U-Net Segmentasyon Sonucu", use_container_width=True)
                            
                            with st.expander("Detaylar", expanded=False):
                                # Boyut ve Konum için tek sütun
                                st.markdown("### Boyut ve Konum")
                                st.markdown("**Piksel:** 2111")
                                st.markdown("**Yüzde:** 4.21%")
                                st.markdown("**Merkez:** (123, 456)")

                                # Şekil ve Renk özelliklerini iki sütuna ayırma
                                col_shape, col_color = st.columns(2)
                                
                                with col_shape:
                                    st.markdown("### Şekil Özellikleri")
                                    st.markdown("**Yuvarlaklık:** 0.7487")
                                    st.markdown("**En-Boy Oranı:** 0.7627")
                                    st.markdown("**Uzantı:** 0.7637")
                                    
                                with col_color:
                                    st.markdown("### Renk ve Doku")
                                    r, g, b = 46, 62, 111
                                    color_box_html = f"<div style='display:inline-block; width:20px; height:20px; background-color:rgb({r},{g},{b}); border:1px solid #444; border-radius:3px;'></div>"
                                    st.markdown(f"**Ortalama Renk:** {color_box_html} `({r}, {g}, {b})`", unsafe_allow_html=True)
                                    st.markdown("**Parlaklık:** 63.37")
                                    st.markdown("**Kontrast:** 14.67")
                                    st.markdown("**Homojenlik:** 0.9670")
                    with col3:
                        with st.container(border=True):
                            st.write("**3D Yapısal Analiz**")
                            st.image("assets/image_analysis/pointnet.png", caption="ResNet Dikkat Haritası", use_container_width=True)
                            st.write("3D Görüntüleme aşağıda:")
                            sketchfab_url_to_embed = selected_item['Analiz Sonuçları']['3D Görüntüleme']
                            if "https://" in sketchfab_url_to_embed:
                                sketchfab_html = f"""
                                <div class="sketchfab-embed-wrapper" style="width: 100%; height: 250px;">
                                    <iframe src="{sketchfab_url_to_embed}" frameborder="0" allowfullscreen style="width: 100%; height: 100%;"></iframe>
                                </div>
                                """
                                components.html(sketchfab_html, height=250, scrolling=False)
                            with st.expander("Detaylar"):
                                st.markdown("**Hacim:** 0.1643 birim³")
                                    

        else:
            st.info("Bu hasta için geçmiş analiz kaydı bulunmamaktadır.")

        st.markdown("---")
        

    def resize_image(image, target_width):
        if image is None: return None
        w_percent = (target_width / float(image.size[0]))
        h_size = int((float(image.size[1]) * float(w_percent)))
        return image.resize((target_width, h_size), Image.Resampling.LANCZOS)

    # --- SESSION STATE, YÜKLEME ALANLARI VE ANALİZ DÖNGÜSÜ (Bu kısımlarda değişiklik yok) ---
    if 'analysis_stage' not in st.session_state: st.session_state.analysis_stage = 'ready'
    if 'results' not in st.session_state: st.session_state.results = {}
    if 'temp_file_path' not in st.session_state: st.session_state.temp_file_path = None
    if 'hsi_files' not in st.session_state: st.session_state.hsi_files = {}

    # "Nasıl Kullanılır" BÖLÜMÜ KALDIRILDI

    st.subheader("Yeni Bronkoskopi Görüntüsü Yükle (Aşama 1-2-3)")
    uploaded_bronch_file = st.file_uploader("Bronkoskopi Görüntüsü", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    st.subheader("Hiperspektral (HSI) Verileri Yükle (Aşama 4)")
    col1, col2 = st.columns(2)
    with col1:
        uploaded_tumor_npz = st.file_uploader("TÜMÖRLÜ ROI (.npz)", type=['npz'], key="hsi_t")
    with col2:
        uploaded_healthy_npz = st.file_uploader("SAĞLIKLI ROI (.npz)", type=['npz'], key="hsi_nt")

    if st.button("TÜM ANALİZLERİ BAŞLAT", type="primary", use_container_width=True, disabled=(st.session_state.analysis_stage == 'running')):
        # ... (Bu blok aynı kalıyor)
        st.session_state.results = {}; st.session_state.analysis_stage = 'running'
        if uploaded_bronch_file:
            temp_dir = tempfile.mkdtemp()
            st.session_state.temp_file_path = os.path.join(temp_dir, uploaded_bronch_file.name)
            with open(st.session_state.temp_file_path, "wb") as f: f.write(uploaded_bronch_file.getbuffer())
        else: st.session_state.temp_file_path = None
        if uploaded_tumor_npz and uploaded_healthy_npz:
            st.session_state.hsi_files['tumor'] = uploaded_tumor_npz.getvalue()
            st.session_state.hsi_files['healthy'] = uploaded_healthy_npz.getvalue()
        else: st.session_state.hsi_files = {}
        st.rerun()

    if st.session_state.analysis_stage == 'running':
        # ... (Bu blok aynı kalıyor)
        if 'resnet_report' not in st.session_state.results and st.session_state.temp_file_path:
            with st.spinner("Aşama 1..."): res = pipeline.run_resnet_analysis(st.session_state.temp_file_path); st.session_state.results.update(res)
            st.success("Aşama 1 tamamlandı!"); st.rerun()
        if 'unet_report' not in st.session_state.results and st.session_state.results.get('resnet_report', {}).get('tahmin_sinif') == 'Lung_cancer':
            with st.spinner("Aşama 2..."): res = pipeline.run_unet_analysis(st.session_state.temp_file_path); st.session_state.results.update(res)
            st.success("Aşama 2 tamamlandı!"); st.rerun()
        if 'pointnet_report' not in st.session_state.results and 'mask_image' in st.session_state.results:
            with st.spinner("Aşama 3..."): res = pipeline.run_pointnet_analysis(st.session_state.results.get('mask_image')); st.session_state.results.update(res)
            st.success("Aşama 3 tamamlandı!"); st.rerun()
        if 'hsi_results' not in st.session_state.results and 'tumor' in st.session_state.hsi_files:
            with st.spinner("Aşama 4..."): res = pipeline.run_hypoxia_analysis(st.session_state.hsi_files['tumor'], st.session_state.hsi_files['healthy']); st.session_state.results.update(res)
            st.success("Aşama 4 tamamlandı!"); st.rerun()
        st.session_state.analysis_stage = 'finished'
        if st.session_state.temp_file_path: shutil.rmtree(os.path.dirname(st.session_state.temp_file_path)); st.session_state.temp_file_path = None
        st.success("Tüm analizler tamamlandı!"); st.balloons(); st.rerun()

    # --- YENİ VE GELİŞMİŞ SONUÇ GÖSTERME BÖLÜMÜ ---
    results = st.session_state.results
    if results:
        st.header("Bütüncül Analiz Raporu")

        # RESNET SONUCU (Değişiklik yok)
        if 'resnet_report' in results:
            with st.expander("Aşama 1: Sınıflandırma Sonucu", expanded=True):
                # ... (Bu bölüm aynı)
                col1, col2 = st.columns([1, 2]); resnet_rep = results['resnet_report']
                with col1:
                    st.metric("Tespit", resnet_rep.get('tahmin_sinif', 'N/A').replace('_', ' '))
                    st.metric("Güven Skoru", f"{resnet_rep.get('guven_skoru', 0)*100:.2f}%")
                with col2:
                    heatmap_img = resize_image(results.get('heatmap_gorsel'), TARGET_IMAGE_WIDTH)
                    if heatmap_img: st.image(heatmap_img, caption="ResNet Dikkat Haritası")
        
        # U-NET SONUCU (TAMAMEN YENİLENDİ)
        if 'unet_report' in results:
            with st.expander("Aşama 2: 2D Segmentasyon ve Kantitatif Analiz", expanded=True):
                 col1, col2 = st.columns([2, 1.5]) # Sağ sütuna daha fazla yer
                 with col1: 
                     overlay_img_unet = resize_image(results.get('overlay_image'), TARGET_IMAGE_WIDTH)
                     if overlay_img_unet: st.image(overlay_img_unet, caption="U-Net Segmentasyon Sonucu")
                 with col2:
                     unet_rep = results['unet_report']
                     if unet_rep.get("tespit") == "Tümör tespit edildi.":
                         st.write("**2D Analiz Raporu:**")
                         
                         # --- Boyut ve Konum Metrikleri ---
                         st.markdown("##### Boyut ve Konum")
                         row1_cols = st.columns(3)
                         row1_cols[0].metric(label="Piksel", value=f"{unet_rep.get('boyut_piksel', 'N/A')}")
                         row1_cols[1].metric(label="Yüzde", value=f"{unet_rep.get('boyut_yuzde', 0):.2f}%")
                         konum_str = f"({unet_rep.get('konum_merkez', ('?','?'))[0]}, {unet_rep.get('konum_merkez', ('?','?'))[1]})"
                         row1_cols[2].metric(label="Merkez", value=konum_str)
                         st.divider()

                         # --- Şekil Metrikleri ---
                         st.markdown("##### Şekil Özellikleri")
                         row2_cols = st.columns(3)
                         row2_cols[0].metric(label="Yuvarlaklık", value=f"{unet_rep.get('sekil_yuvarlaklik', 0):.3f}")
                         row2_cols[1].metric(label="En-Boy Oranı", value=f"{unet_rep.get('sekil_en_boy_orani', 0):.3f}")
                         row2_cols[2].metric(label="Uzantı", value=f"{unet_rep.get('sekil_uzanti', 0):.3f}")
                         st.divider()

                         # --- Renk ve Doku Metrikleri ---
                         st.markdown("##### Renk ve Doku")
                         rgb_tuple = unet_rep.get('renk_ortalama_rgb', (0,0,0))
                         r, g, b = int(rgb_tuple[0]), int(rgb_tuple[1]), int(rgb_tuple[2])
                         color_box_html = f"<div style='display: inline-block; width: 20px; height: 20px; background-color: rgb({r},{g},{b}); border: 1px solid #444; border-radius: 3px; vertical-align: middle;'></div>"
                         st.markdown(f"**Ortalama Renk:** {color_box_html} `({r}, {g}, {b})`", unsafe_allow_html=True)
                         
                         row3_cols = st.columns(3)
                         row3_cols[0].metric(label="Parlaklık", value=f"{unet_rep.get('doku_ortalama_parlaklik', 0):.2f}")
                         row3_cols[1].metric(label="Kontrast", value=f"{unet_rep.get('doku_kontrast', 0):.2f}")
                         row3_cols[2].metric(label="Homojenlik", value=f"{unet_rep.get('doku_homojenlik', 0):.3f}")

                     else: 
                         st.info(unet_rep.get("tespit", "2D analizde tümör bulunamadı."))

        # POINTNET++ SONUCU (Değişiklik yok, mevcut hali temiz)
        if 'pointnet_report' in results:
            with st.expander("Aşama 3: 3D Yapısal Analiz Sonucu", expanded=True):
                # ... (Bu bölüm aynı kalıyor)
                col1, col2 = st.columns([2, 1]); pointnet_rep = results['pointnet_report']
                with col1: 
                    img_3d = resize_image(results.get('gorsel_3d'), TARGET_IMAGE_WIDTH)
                    if img_3d: st.image(img_3d, caption="3D Model")
                with col2:
                    if pointnet_rep.get("tespit_3d") == "3D Tümör Yapısı Analiz Edildi.":
                        st.write("**3D Analiz Raporu:**")
                        st.metric(label="Hacim (Convex Hull)", value=f"{pointnet_rep.get('hacim_convex_hull', 0):.4f} birim³")
                        st.metric(label="Yüzey Alanı (Convex Hull)", value=f"{pointnet_rep.get('yuzey_alani_convex_hull', 0):.4f} birim²")
                        st.metric(label="Şekil (Küresellik)", value=f"{pointnet_rep.get('sekil_kuresellik_3d', 0):.4f}", help="1.0 değeri mükemmel bir küreyi ifade eder.")
                    else: 
                        st.info(pointnet_rep.get("tespit_3d", "3D analizde yapı bulunamadı."))
        
        # HSI SONUCU (Değişiklik yok)
        if 'hsi_results' in results:
            with st.expander("Aşama 4: Hipoksi Analizi Sonucu", expanded=True):
                # ... (Bu bölüm aynı kalıyor)
                hsi_res = results['hsi_results']
                if 'hata_hsi' in hsi_res: st.error(hsi_res['hata_hsi'])
                else:
                    hsi_col1, hsi_col2 = st.columns(2)
                    with hsi_col1: st.image(hsi_res.get('signature_plot'), caption="Spektral İmza Karşılaştırması", use_container_width=True)
                    with hsi_col2: st.image(hsi_res.get('overlay_image'), caption="Hipoksi Haritası", use_container_width=True)