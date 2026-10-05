# modules/pipeline.py

import torch
import os
from PIL import Image

# Kardeş modülleri doğru şekilde import et
from .resnet import MultiLayerMaskedResNet, analyze_image as analyze_with_resnet, CLASS_NAMES
from .unet import AttentionUNet, analyze_image_with_unet
from .pointnet import PointNetAutoencoder, analyze_mask_with_pointnet
from .hsi_analiz import analyze_hsi_for_hypoxia

class BronkoVisionPipeline:
    def __init__(self, resnet_path, unet_path, pointnet_path):
        """
        Başlangıçta tüm modelleri bir kez yükler ve hafızada hazır tutar.
        """
        print("BronkoVision Pipeline Başlatılıyor: Modeller Yükleniyor...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            self.resnet_model = MultiLayerMaskedResNet(num_classes=len(CLASS_NAMES))
            self.resnet_model.load_state_dict(torch.load(resnet_path, map_location=self.device))
            self.resnet_model.to(self.device).eval()

            self.unet_model = AttentionUNet()
            self.unet_model.load_state_dict(torch.load(unet_path, map_location=self.device))
            self.unet_model.to(self.device).eval()

            self.pointnet_model = PointNetAutoencoder(num_points=2048)
            self.pointnet_model.load_state_dict(torch.load(pointnet_path, map_location=self.device))
            self.pointnet_model.to(self.device).eval()
            
            print("Tüm ana modeller başarıyla yüklendi ve hazır.")
        
        except Exception as e:
            print(f"HATA: Modeller yüklenirken bir sorun oluştu: {e}")
            raise

    # --- YENİ MODÜLER FONKSİYONLAR ---

    def run_resnet_analysis(self, image_path):
        """Aşama 1: Sadece ResNet analizini çalıştırır."""
        try:
            pred_class, conf_score, heatmap = analyze_with_resnet(self.resnet_model, image_path, CLASS_NAMES)
            return {
                'resnet_report': {'tahmin_sinif': pred_class, 'guven_skoru': conf_score},
                'heatmap_gorsel': heatmap
            }
        except Exception as e:
            return {'hata_resnet': f"ResNet analizi başarısız: {e}"}

    def run_unet_analysis(self, image_path):
        """Aşama 2: Sadece U-Net analizini çalıştırır."""
        try:
            unet_results = analyze_image_with_unet(self.unet_model, image_path)
            # U-Net'in kendi raporunu 'unet_report' anahtarı altına al
            unet_report = unet_results.pop('report', {})
            # Görselleri ve raporu tek bir sözlükte birleştir
            final_unet_results = {'unet_report': unet_report}
            final_unet_results.update(unet_results)
            return final_unet_results
        except Exception as e:
            return {'hata_unet': f"U-Net analizi başarısız: {e}"}

    def run_pointnet_analysis(self, mask_image):
        """Aşama 3: Sadece PointNet analizini çalıştırır."""
        try:
            if mask_image and mask_image.getbbox():
                pointnet_results = analyze_mask_with_pointnet(mask_image, self.pointnet_model)
                return {
                    'pointnet_report': pointnet_results.pop('rapor_3d', {}),
                    **pointnet_results  # Geriye kalan gorsel_3d gibi anahtarları ekler
                }
            else:
                 return {'pointnet_report': {"tespit_3d": "Analiz için geçerli maske bulunamadı."}}
        except Exception as e:
            return {'hata_pointnet': f"PointNet++ analizi başarısız: {e}"}
            
    def run_hypoxia_analysis(self, tumor_npz_content, healthy_npz_content):
        """Aşama 4: HSI analizini çalıştırır."""
        try:
            print("\nAşama 4: HSI ile Hipoksi Analizi Başlatılıyor...")
            hsi_results = analyze_hsi_for_hypoxia(tumor_npz_content, healthy_npz_content)
            # Streamlit'te kolay göstermek için sonucu bir anahtar altına alalım
            return {'hsi_results': hsi_results}
        except Exception as e:
            return {'hsi_results': {'hata_hsi': f"HSI analizi başarısız oldu: {e}"}}