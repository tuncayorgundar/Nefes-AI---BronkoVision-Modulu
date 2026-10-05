# prototip/ui_components/sidebar.py

import streamlit as st
import base64
import pandas as pd
import re


def render_sidebar(all_patients, logo_path):
    """
    Kenar çubuğunu render eder ve kullanıcı seçimlerini alır.
    patient_data artık bir DataFrame değil, hasta nesnelerinin listesidir.
    """
    with st.sidebar:
        # Logonun base64 verisini alarak HTML içinde ortala
        try:
            with open(logo_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode()

            # Tıklanabilir logo için HTML kodu
            logo_html = f"""
            <div style='text-align: center;'>
                <a href="?page=main" target="_self">
                    <img src='data:image/png;base64,{encoded_string}' width='120' style='cursor: pointer;'>
                </a>
            </div>
            """
            st.markdown(logo_html, unsafe_allow_html=True)
        except FileNotFoundError:
            st.error("Logo dosyası bulunamadı.")
            st.image(logo_path, width=120)

        st.markdown("---")

        st.subheader("Hasta Arama")
        search_term = st.text_input("Hasta adı veya ID girin:", key="patient_search_input")

        # Hasta nesnelerinden DataFrame oluştur
        if not all_patients:
            st.warning("Veritabanında hiç hasta bulunamadı.")
            return None, None

        patient_df = pd.DataFrame([
            {
                'id': p.patient_id,
                'Adı Soyadı': f"{p.first_name} {p.last_name}"
            } for p in all_patients
        ])

        filtered_patients_df = patient_df
        if search_term:
            filtered_patients_df = patient_df[
                patient_df['Adı Soyadı'].str.contains(search_term, case=False) |
                patient_df['id'].astype(str).str.contains(search_term, case=False)
            ]

        if filtered_patients_df.empty:
            st.warning("Eşleşen hasta bulunamadı.")
            return None, None

        filtered_patients_df['Görüntüleme Adı'] = (
            filtered_patients_df['id'].astype(str) + ' - ' + filtered_patients_df['Adı Soyadı']
        )

        # Eğer st.session_state'te bir hasta seçilmişse, bu değeri bul
        selected_index = 0
        if "patient_selected_id" in st.session_state and st.session_state.patient_selected_id is not None:
            try:
                selected_index = filtered_patients_df[
                    filtered_patients_df['id'] == st.session_state.patient_selected_id
                ].index[0]
                selected_index = filtered_patients_df.reset_index().loc[selected_index]['index']
            except IndexError:
                selected_index = 0

        # Hasta seçimi
        selected_patient_view = st.selectbox(
            "Hasta Seçin:",
            filtered_patients_df['Görüntüleme Adı'],
            index=int(selected_index),
            key='patient_selectbox'
        )

        if selected_patient_view:
            selected_patient_id = filtered_patients_df[
                filtered_patients_df['Görüntüleme Adı'] == selected_patient_view
            ]['id'].iloc[0]
        else:
            selected_patient_id = None

        st.markdown("---")

        user_role = st.selectbox(
            "Rolünüzü Seçin:",
            ["Doktor", "Yönetici", "Laboratuvar Uzmanı", "Radyoloji Uzmanı"],
            key="user_role_selectbox"
        )

        # --- Genişletilebilir Bildirimler Bölümü ---
        st.markdown("---")

        # Sahte bildirimleri session_state'e ekleyin
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
            st.session_state.notifications.append({
                "type": "Yeni Sonuç",
                "message": "Hasta ID: 101 - Mehmet Yılmaz için kan tahlili sonuçları geldi."
            })
            st.session_state.notifications.append({
                "type": "Sistem Duyurusu",
                "message": "Sistem bakımı bu akşam 21:00'da başlayacaktır."
            })
            st.session_state.notifications.append({
                "type": "Randevu",
                "message": "Hasta ID: 105 - Ali Yildiz için yarın 14:00'da randevu hatırlatması."
            })

        num_new_notifications = len(st.session_state.notifications)

        # Genişletici başlığını ayarla
        if num_new_notifications > 0:
            expander_title = f"🔔 Bildirimler ({num_new_notifications} Yeni)"
        else:
            expander_title = "🔔 Bildirimler (Güncel)"

        # Bildirimleri göster
        with st.expander(expander_title):
            if st.session_state.notifications:
                for i, notif in enumerate(reversed(st.session_state.notifications)):
                    notif_text = f"**{notif['type']}**: {notif['message']}"

                    if st.button(notif_text, key=f"notif_{i}"):
                        # Mesajdan hasta ID'sini çek
                        match = re.search(r"Hasta ID:\s*(\d+)", notif['message'])
                        if match:
                            st.session_state.patient_selected_id = int(match.group(1))
                            st.rerun()  # Yeni API
            else:
                st.info("Şu an yeni bildiriminiz yok.")

    return user_role, selected_patient_id
