import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageChops
import os
import numpy as np
from pytorch_grad_cam import LayerCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image
import matplotlib.pyplot as plt

# =============================================================================
# 1. TEMEL AYARLAR VE YARDIMCI SINIFLAR
# =============================================================================

CLASS_NAMES = ['Lung_cancer', 'Non_lung_cancer']

class SmartCrop:
    """Görüntüdeki siyah çerçeveleri otomatik olarak kırpar."""
    def __call__(self, img):
        bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
        if bbox: return img.crop(bbox)
        return img

class MultiLayerMaskedResNet(nn.Module):
    """Eğitimde kullandığımız özel model sınıfının AYNISI."""
    def __init__(self, num_classes=2, dropout_rate=0.5, mask_ratio=0.3):
        super(MultiLayerMaskedResNet, self).__init__()
        self.original_model = models.resnet152(weights=None)
        self.mask_ratio = mask_ratio
        num_ftrs = self.original_model.fc.in_features
        self.original_model.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512), nn.ReLU(),
            nn.Dropout(dropout_rate), nn.Linear(512, num_classes)
        )
    def forward(self, x):
        x = self.original_model.conv1(x); x = self.original_model.bn1(x); x = self.original_model.relu(x); x = self.original_model.maxpool(x)
        x = self.original_model.layer1(x)
        features_l2 = self.original_model.layer2(x)
        masked_features_l2 = self._mask_features(features_l2)
        features_l3 = self.original_model.layer3(masked_features_l2)
        masked_features_l3 = self._mask_features(features_l3)
        x = self.original_model.layer4(masked_features_l3)
        x = self.original_model.avgpool(x); x = torch.flatten(x, 1); x = self.original_model.fc(x)
        return x
    def _mask_features(self, features):
        masked_features = features.clone()
        _, _, h, w = masked_features.shape
        h_margin = int(h * self.mask_ratio); w_margin = int(w * self.mask_ratio)
        masked_features[:, :, :h_margin, :] = 0; masked_features[:, :, h-h_margin:, :] = 0
        masked_features[:, :, :, :w_margin] = 0; masked_features[:, :, :, w-w_margin:] = 0
        return masked_features

# =============================================================================
# 2. YENİ BİRLEŞTİRİLMİŞ ANALİZ FONKSİYONU
# =============================================================================
def analyze_image(model, image_path, class_names):
    """
    Tek bir görüntüyü sınıflandırır, ısı haritasını oluşturur ve
    sonuçları değişken olarak döndürür.
    
    Returns:
        tuple: (predicted_class, confidence_score, heatmap_pil_image)
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # --- GÖRÜNTÜYÜ HAZIRLA ---
    preprocess = transforms.Compose([
        SmartCrop(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image_pil = Image.open(image_path).convert('RGB')
    input_tensor = preprocess(image_pil).unsqueeze(0).to(device)

    # --- SINIFLANDIRMA YAP ---
    with torch.no_grad():
        output = model(input_tensor)
    probabilities = torch.nn.functional.softmax(output[0], dim=0)
    confidence, predicted_idx = torch.max(probabilities, 0)
    predicted_class = class_names[predicted_idx.item()]
    confidence_score = confidence.item()

    # --- ISI HARİTASI OLUŞTUR ---
    target_layers = [model.original_model.layer4[-1]]
    targets = [ClassifierOutputTarget(predicted_idx.item())]
    
    with LayerCAM(model=model, target_layers=target_layers) as cam:
        grayscale_cam = cam(input_tensor=input_tensor, targets=targets)[0, :]
    
    transform_for_viz = transforms.Compose([SmartCrop(), transforms.Resize((224, 224))])
    img_for_viz = transform_for_viz(image_pil)
    rgb_img = np.array(img_for_viz) / 255.0
    
    visualization_np = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)
    heatmap_pil_image = Image.fromarray(visualization_np)

    # --- Sonuçları döndür ---
    return predicted_class, confidence_score, heatmap_pil_image

# =============================================================================
# 3. ANA ÇALIŞTIRMA BÖLÜMÜ
# =============================================================================
if __name__ == "__main__":
    # --- KULLANICI AYARLARI ---
    IMAGE_TO_TEST_PATH = 'C:/GUNDAR/akademi/OnkoNixAi/Bronkovision/models/test_kanser.png'
    MODEL_WEIGHTS_PATH = 'C:/GUNDAR/akademi/OnkoNixAi/Bronkovision/models/best_model_resnet.pth'
    
    print("="*50)
    print("BronkoVision: Tek Görüntü Analiz ve Sınıflandırma")
    print("="*50)

    if not os.path.exists(IMAGE_TO_TEST_PATH):
        print(f"\nHATA: Test edilecek görüntü yolu bulunamadı: {IMAGE_TO_TEST_PATH}")
    else:
        try:
            # 1. Modeli bir kez yükle
            print("Model yükleniyor...")
            model = MultiLayerMaskedResNet(num_classes=len(CLASS_NAMES))
            model.load_state_dict(torch.load(MODEL_WEIGHTS_PATH, map_location=torch.device('cpu')))
            print(f"Model ağırlıkları başarıyla yüklendi: {MODEL_WEIGHTS_PATH}")

            # 2. Analiz fonksiyonunu çağır ve tüm sonuçları al
            print(f"\nAnaliz ediliyor: {IMAGE_TO_TEST_PATH}")
            pred_class, conf_score, heatmap_variable = analyze_image(model, IMAGE_TO_TEST_PATH, CLASS_NAMES)
            
            # 3. Sonuçları terminale yazdır
            print("\n--- SINIFLANDIRMA SONUCU ---")
            print(f"Tahmin Edilen Sınıf: {pred_class.upper()}")
            print(f"Güven Skoru: %{conf_score * 100:.2f}")
            print("----------------------------")

            # 4. Isı haritasının değişkende tutulduğunu onayla ve göster
            print("\nIsı haritası başarıyla oluşturuldu ve bir değişkende saklanıyor.")
            print("Bu 'heatmap_variable' değişkenini artık başka bir yerde kullanabilirsiniz.")
            
            # Değişkeni kullanarak ısı haritasını ekranda gösterelim
            plt.imshow(heatmap_variable)
            plt.axis('off')
            plt.show()

        except Exception as e:
            print(f"\nBir hata oluştu: {e}")