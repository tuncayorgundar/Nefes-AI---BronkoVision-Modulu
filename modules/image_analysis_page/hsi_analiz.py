# modules/hsi_analiz.py

import spectral
import numpy as np
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
from PIL import Image
import io

def load_hsi_from_npz_content(npz_file_content):
    """
    Kullanıcının yüklediği .npz dosyasının içeriğinden (bytes) HSI veri küpünü
    ve dalga boylarını yükler.
    """
    try:
        # Bellekteki bytes verisini bir dosya benzeri nesne olarak aç
        with io.BytesIO(npz_file_content) as f:
            data = np.load(f)
            # 'prepare_hsi_for_web.py' betiğinde kaydettiğimiz anahtarlarla verileri çek
            cube = data['cube']
            wavelengths = data['wavelengths']
        print(f"Optimize edilmiş NPZ verisi başarıyla yüklendi. Küp boyutu: {cube.shape}")
        return cube, wavelengths
    except Exception as e:
        print(f"HATA: .npz dosyası okunurken bir sorun oluştu: {e}")
        return None, None


# ... (Diğer tüm fonksiyonlar: get_signature_from_center, calculate_similarity, 
#      create_similarity_heatmap, analyze_hsi_for_hypoxia önceki kodla aynı kalabilir)
def get_signature_from_center(cube):
    h, w, _ = cube.shape
    center_patch = cube[h//2-5:h//2+5, w//2-5:w//2+5, :]
    return np.mean(center_patch, axis=(0, 1))

def calculate_similarity(spectrum1, spectrum2):
    dot_product = np.dot(spectrum1, spectrum2)
    norm_1 = np.linalg.norm(spectrum1)
    norm_2 = np.linalg.norm(spectrum2)
    return dot_product / (norm_1 * norm_2) if norm_1 > 0 and norm_2 > 0 else 0

def create_similarity_heatmap(spectral_image, reference_signature):
    height, width, _ = spectral_image.shape
    heatmap = np.zeros((height, width))
    for r in tqdm(range(height), desc="Hipoksi Haritası Oluşturuluyor"):
        for c in range(width):
            heatmap[r, c] = calculate_similarity(spectral_image[r, c, :], reference_signature)
    return heatmap

def analyze_hsi_for_hypoxia(tumor_npz_content, healthy_npz_content):
    """
    İki HSI .npz dosyasının içeriğini alır, analiz eder ve tüm çıktıları
    bir sözlük olarak döndürür.
    """
    results = {}
    
    # 1. Verileri .npz içeriklerinden yükle
    tumor_cube, wavelengths = load_hsi_from_npz_content(tumor_npz_content)
    healthy_cube, _ = load_hsi_from_npz_content(healthy_npz_content)

    if tumor_cube is None or healthy_cube is None:
        results["hata"] = "HSI .npz verileri yüklenemediği için analiz yapılamadı."
        return results

    # --- DÜZELTME BAŞLANGICI ---
    # float16 verisini, daha sonraki işlemler için standart float32'ye çevirelim.
    # Bu, uyumluluk sorunlarını önler.
    tumor_cube = tumor_cube.astype(np.float32)
    healthy_cube = healthy_cube.astype(np.float32)
    # --- DÜZELTME BİTTİ ---

    # Geri kalan analiz ve görselleştirme mantığı tamamen aynı
    hypoxia_signature = get_signature_from_center(tumor_cube)
    healthy_signature = get_signature_from_center(healthy_cube)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(wavelengths, hypoxia_signature, label='Tümör / Hipoksik Doku İmzası', color='crimson')
    ax.plot(wavelengths, healthy_signature, label='Sağlıklı Doku İmzası', color='royalblue')
    ax.set_title("Tümörlü ve Sağlıklı Dokuların Spektral Karşılaştırması")
    ax.set_xlabel("Dalga Boyu (nm)"); ax.set_ylabel("Normalize Edilmiş Yansıma")
    ax.legend(); ax.grid(True)
    buf = io.BytesIO(); fig.savefig(buf, format='png'); plt.close(fig); buf.seek(0)
    results["signature_plot"] = Image.open(buf)
    
    hypoxia_heatmap = create_similarity_heatmap(tumor_cube, hypoxia_signature)
    
    # Yaklaşık RGB görüntüyü optimize edilmiş küpten oluştur
    num_bands = tumor_cube.shape[2]
    pseudo_rgb_np = tumor_cube[:, :, [int(num_bands*0.25), int(num_bands*0.5), int(num_bands*0.75)]]
    
    # Görüntüyü PIL'e vermeden önce normalize edip 0-255 arasına getirelim
    pseudo_rgb_np = (pseudo_rgb_np - np.min(pseudo_rgb_np)) / (np.max(pseudo_rgb_np) - np.min(pseudo_rgb_np) + 1e-8)
    pseudo_rgb_pil = Image.fromarray((pseudo_rgb_np * 255).astype(np.uint8))
    
    # Bindirilmiş görseli oluştur
    fig, ax = plt.subplots(); ax.imshow(pseudo_rgb_pil); ax.imshow(hypoxia_heatmap, cmap='jet', alpha=0.6); ax.axis('off')
    buf = io.BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig); buf.seek(0)
    results["overlay_image"] = Image.open(buf)
    
    return results
# =============================================================================
# 3. ANA ÇALIŞTIRMA BÖLÜMÜ (ÖRNEK KULLANIM)
# =============================================================================
if __name__ == '__main__':
    TUMOR_ROI_PATH = 'C:/GUNDAR/akademi/OnkoNixAi/Bronkovision/models/Hipoksi_dataset/ROI_01_C02_T'
    HEALTHY_ROI_PATH = 'C:/GUNDAR/akademi/OnkoNixAi/Bronkovision/models/Hipoksi_dataset/ROI_02_C18_NT'
    
    try:
        # 1. Ana analiz fonksiyonunu çağır ve tüm sonuçları al
        print("Hipoksi analizi başlatılıyor...")
        hsi_results = analyze_hsi_for_hypoxia(TUMOR_ROI_PATH, HEALTHY_ROI_PATH)
        print("Analiz tamamlandı.")

        # 2. Dönen sözlükten istediğin veriye eriş
        if "hata" in hsi_results:
            print(f"\nHATA: {hsi_results['hata']}")
        else:
            print("\nTüm analiz sonuçları ve görseller değişkenlerde saklanıyor.")
            
            # Örneğin, spektral karşılaştırma grafiğini göster
            signature_plot = hsi_results.get("signature_plot")
            if signature_plot:
                print("Spektral imza grafiği gösteriliyor...")
                signature_plot.show(title="Spektral İmza Karşılaştırması")
            
            # Örneğin, bindirilmiş sonucu göster
            overlay_image = hsi_results.get("overlay_image")
            if overlay_image:
                print("Hipoksi haritası sonucu gösteriliyor...")
                overlay_image.show(title="Analiz Sonucu: Hipoksik Bölgeler")
                
            # Sayısal verilere de erişebiliriz
            tumor_sig_data = hsi_results.get("tumor_signature")
            if tumor_sig_data is not None:
                # Örneğin, 550nm'ye en yakın dalga boyundaki yansıma değerini bulalım
                wavelengths = hsi_results["wavelengths"]
                idx_550nm = np.argmin(np.abs(wavelengths - 550))
                reflectance_at_550nm = tumor_sig_data[idx_550nm]
                print(f"\nTümör imzasının ~550nm'deki yansıma değeri: {reflectance_at_550nm:.4f}")

    except Exception as e:
        print(f"\nGenel bir hata oluştu: {e}")