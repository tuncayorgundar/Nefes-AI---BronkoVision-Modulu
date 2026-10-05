import streamlit as st

def render_demo_presentation():
    """
    Uygulamanın demosu ve ana konseptini anlatan sayfayı render eder.
    """

    # CSS ile arka plan iframe ekle
    st.markdown(
        """
        <style>
        .stApp {
            background: transparent;
        }
        .background-iframe {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1; /* arkada dursun */
            border: none;
            opacity: 0.6;
        }
        </style>
        <iframe class="background-iframe"
            src="https://sketchfab.com/models/0e74fa30e33143f08403d5e14f9252ac/embed?autospin=1&autostart=1"
            allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true"
            allow="autoplay; fullscreen; xr-spatial-tracking">
        </iframe>
        """,
        unsafe_allow_html=True
    )

    # Asıl içerik
    st.title("NefesAI'ye Hoş Geldiniz! 👋")
    st.markdown("""
        Sağlık hizmetlerinde yapay zeka destekli çözümler sunan **NefesAI**, doktorlar, laboratuvar ve radyoloji uzmanları için geliştirilmiştir.
        Bu uygulama ile hastalarınızın verilerini kolayca yönetebilir, biyoanaliz ve görüntü analizi sonuçlarını inceleyebilir ve tedavi süreçlerini takip edebilirsiniz.
        
        **Temel Özellikler:**
        - **Hasta Yönetimi:** Hastaları listeleme, arama ve seçme.
        - **Biyoanaliz:** Kan testleri ve genetik biyobelirteç sonuçlarını, trend analizlerini ve anormallikleri takip etme.
        - **Görüntü Analizi:** Yapay zeka destekli görüntü analizi ve geçmiş sonuçların incelenmesi.
        - **Tedavi Planı:** Hastalar için tedavi planları oluşturma ve yönetme.
        
        Uygulamayı kullanmaya başlamak için kenar çubuğundan bir hasta seçebilir veya farklı roller arasında geçiş yapabilirsiniz.
    """)
