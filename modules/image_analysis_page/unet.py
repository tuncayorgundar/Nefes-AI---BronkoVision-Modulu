import torch
import torch.nn as nn
from torchvision import transforms
from PIL import Image, ImageChops
import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from skimage.feature import graycomatrix, graycoprops
import io

# =============================================================================
# 1. YARDIMCI SINIFLAR VE MİMARİ (Değişiklik yok)
# =============================================================================
# ... (SmartCrop, ConvBlock, AttentionBlock, AttentionUNet sınıfları öncekiyle aynı) ...
class SmartCrop:
    def __call__(self, img):
        bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
        if bbox: return img.crop(bbox)
        return img
class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.conv = nn.Sequential(nn.Conv2d(in_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),nn.Conv2d(out_ch, out_ch, 3, padding=1, bias=False), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True))
    def forward(self, x): return self.conv(x)
class AttentionBlock(nn.Module):
    def __init__(self, F_g, F_l, F_int):
        super().__init__()
        self.W_g = nn.Sequential(nn.Conv2d(F_g, F_int, 1), nn.BatchNorm2d(F_int))
        self.W_x = nn.Sequential(nn.Conv2d(F_l, F_int, 1), nn.BatchNorm2d(F_int))
        self.psi = nn.Sequential(nn.Conv2d(F_int, 1, 1), nn.BatchNorm2d(1), nn.Sigmoid())
        self.relu = nn.ReLU(inplace=True)
    def forward(self, g, x):
        g1 = self.W_g(g); x1 = self.W_x(x);
        psi = self.relu(g1 + x1); psi = self.psi(psi)
        return x * psi
class AttentionUNet(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super().__init__()
        self.MaxPool = nn.MaxPool2d(2, stride=2)
        self.Conv1 = ConvBlock(n_channels, 64); self.Conv2 = ConvBlock(64, 128)
        self.Conv3 = ConvBlock(128, 256); self.Conv4 = ConvBlock(256, 512); self.Conv5 = ConvBlock(512, 1024)
        self.Up5 = nn.ConvTranspose2d(1024, 512, 2, stride=2); self.Att5 = AttentionBlock(512, 512, 256); self.UpConv5 = ConvBlock(1024, 512)
        self.Up4 = nn.ConvTranspose2d(512, 256, 2, stride=2); self.Att4 = AttentionBlock(256, 256, 128); self.UpConv4 = ConvBlock(512, 256)
        self.Up3 = nn.ConvTranspose2d(256, 128, 2, stride=2); self.Att3 = AttentionBlock(128, 128, 64); self.UpConv3 = ConvBlock(256, 128)
        self.Up2 = nn.ConvTranspose2d(128, 64, 2, stride=2); self.Att2 = AttentionBlock(64, 64, 32); self.UpConv2 = ConvBlock(128, 64)
        self.Conv_1x1 = nn.Conv2d(64, n_classes, 1)
    def forward(self, x):
        e1=self.Conv1(x);e2=self.MaxPool(e1);e2=self.Conv2(e2);e3=self.MaxPool(e2);e3=self.Conv3(e3);e4=self.MaxPool(e3);e4=self.Conv4(e4);e5=self.MaxPool(e4);e5=self.Conv5(e5)
        d5=self.Up5(e5);x4=self.Att5(g=d5,x=e4);d5=torch.cat((x4,d5),dim=1);d5=self.UpConv5(d5)
        d4=self.Up4(d5);x3=self.Att4(g=d4,x=e3);d4=torch.cat((x3,d4),dim=1);d4=self.UpConv4(d4)
        d3=self.Up3(d4);x2=self.Att3(g=d3,x=e2);d3=torch.cat((x2,d3),dim=1);d3=self.UpConv3(d3)
        d2=self.Up2(d3);x1=self.Att2(g=d2,x=e1);d2=torch.cat((x1,d2),dim=1);d2=self.UpConv2(d2)
        return self.Conv_1x1(d2)

# =============================================================================
# 2. GÜNCELLENMİŞ ANALİZ FONKSİYONU
# =============================================================================
def analyze_tumor_properties(mask_np, original_image_np):
    """
    Maskeyi analiz eder ve her metrik için ayrı anahtarlar içeren
    bir sözlük döndürür.
    """
    report = {}
    
    if np.sum(mask_np) < 50:
        report["tespit"] = "Tümör tespit edilmedi."
        return report

    report["tespit"] = "Tümör tespit edildi."
    
    total_pixels = mask_np.shape[0] * mask_np.shape[1]
    tumor_pixels = np.sum(mask_np > 0)
    report["boyut_piksel"] = int(tumor_pixels)
    report["boyut_yuzde"] = (tumor_pixels / total_pixels) * 100

    contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    main_contour = max(contours, key=cv2.contourArea)
    M = cv2.moments(main_contour)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"]); cY = int(M["m01"] / M["m00"])
        report["konum_merkez"] = (cX, cY)

    area = cv2.contourArea(main_contour); perimeter = cv2.arcLength(main_contour, True)
    x, y, w, h = cv2.boundingRect(main_contour)
    
    if perimeter > 0: report["sekil_yuvarlaklik"] = (4 * np.pi * area) / (perimeter ** 2)
    if h > 0: report["sekil_en_boy_orani"] = float(w) / h
    if (w * h) > 0: report["sekil_uzanti"] = area / (w * h)

    pixels_in_mask = original_image_np[mask_np > 0]
    mean_color = np.mean(pixels_in_mask, axis=0)
    report["renk_ortalama_rgb"] = tuple(mean_color)
    
    gray_image = cv2.cvtColor(original_image_np, cv2.COLOR_RGB2GRAY)
    gray_pixels_in_mask = gray_image[mask_np > 0]
    report["doku_ortalama_parlaklik"] = np.mean(gray_pixels_in_mask)
    
    if len(gray_pixels_in_mask) > 1:
        glcm_img = np.zeros_like(gray_image); glcm_img[mask_np > 0] = gray_pixels_in_mask
        glcm = graycomatrix(glcm_img, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
        report["doku_kontrast"] = graycoprops(glcm, 'contrast')[0, 0]
        report["doku_homojenlik"] = graycoprops(glcm, 'homogeneity')[0, 0]
        
    return report

# =============================================================================
# 3. GÜNCELLENMİŞ ANA ANALİZ FONKSİYONU
# =============================================================================
def analyze_image_with_unet(model, image_path): # Artık 'model_path' yerine 'model' alıyor
    """
    Tek bir görüntüyü U-Net ile analiz eder ve tüm çıktıları döndürür.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Model zaten yüklü ve doğru cihazda olduğu için tekrar yüklemeye gerek yok
    model.eval() 
    
    preprocess = transforms.Compose([
        SmartCrop(), transforms.Resize((224, 224)), transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image_pil = Image.open(image_path).convert("RGB")
    input_tensor = preprocess(image_pil).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
    probs = torch.sigmoid(output.squeeze(0))
    pred_mask_np = (probs > 0.5).cpu().numpy().squeeze().astype(np.uint8)
    
    original_image_transformed_pil = transforms.Compose([SmartCrop(), transforms.Resize((224, 224))])(image_pil)
    original_image_np = np.array(original_image_transformed_pil)
    mask_pil = Image.fromarray(pred_mask_np * 255)

    # --- DEĞİŞİKLİK BURADA: Raporu al ve ana sözlüğe entegre et ---
    analysis_report = analyze_tumor_properties(pred_mask_np, original_image_np)

    fig, ax = plt.subplots(); ax.imshow(original_image_np); ax.imshow(pred_mask_np, cmap='jet', alpha=0.4); ax.axis('off')
    buf = io.BytesIO(); fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0); plt.close(fig)
    buf.seek(0); overlay_pil = Image.open(buf)

    results = {
        "report": analysis_report, # Sayısal raporu 'report' anahtarı altına al
        "original_image": original_image_transformed_pil,
        "mask_image": mask_pil,
        "overlay_image": overlay_pil
    }
    return results

# =============================================================================
# 4. ANA ÇALIŞTIRMA BÖLÜMÜ (ÖRNEK KULLANIM)
# =============================================================================
if __name__ == "__main__":
    IMAGE_TO_TEST_PATH = 'test_kanser.png'
    MODEL_WEIGHTS_PATH = 'best_model_unet.pth'
    
    if not os.path.exists(IMAGE_TO_TEST_PATH):
        print(f"HATA: Test edilecek görüntü bulunamadı -> {IMAGE_TO_TEST_PATH}")
    else:
        try:
            print("U-Net ile segmentasyon ve analiz başlatılıyor...")
            analysis_results = analyze_image_with_unet(MODEL_WEIGHTS_PATH, IMAGE_TO_TEST_PATH)
            print("Analiz tamamlandı.")

            # --- GÜNCELLENMİŞ RAPOR YAZDIRMA ---
            print("\n" + "="*30)
            print("   TÜMÖR ANALİZ RAPORU")
            print("="*30)
            # Artık 'report' alt anahtarına gerek yok, doğrudan erişim
            print(f"{'Tespit':<25}: {analysis_results.get('tespit', 'N/A')}")
            if analysis_results.get('tespit') == "Tümör tespit edildi.":
                print(f"{'Boyut (Piksel)':<25}: {analysis_results.get('boyut_piksel', 'N/A')}")
                print(f"{'Boyut (Yüzde)':<25}: {analysis_results.get('boyut_yuzde', 0):.2f}%")
                print(f"{'Konum (Merkez)':<25}: {analysis_results.get('konum_merkez', 'N/A')}")
                print(f"{'Şekil (Yuvarlaklık)':<25}: {analysis_results.get('sekil_yuvarlaklik', 0):.4f}")
                print(f"{'Şekil (En-Boy Oranı)':<25}: {analysis_results.get('sekil_en_boy_orani', 0):.4f}")
                print(f"{'Şekil (Uzantı)':<25}: {analysis_results.get('sekil_uzanti', 0):.4f}")
                print(f"{'Renk (Ortalama RGB)':<25}: ({analysis_results.get('renk_ortalama_rgb', (0,0,0))[0]:.1f}, {analysis_results.get('renk_ortalama_rgb', (0,0,0))[1]:.1f}, {analysis_results.get('renk_ortalama_rgb', (0,0,0))[2]:.1f})")
                print(f"{'Doku (Ortalama Parlaklık)':<25}: {analysis_results.get('doku_ortalama_parlaklik', 0):.2f}")
                print(f"{'Doku (Kontrast)':<25}: {analysis_results.get('doku_kontrast', 0):.4f}")
                print(f"{'Doku (Homojenlik)':<25}: {analysis_results.get('doku_homojenlik', 0):.4f}")
            print("="*30)

            # Görselleri ayrı değişkenlere al
            original_img = analysis_results["original_image"]
            mask_img = analysis_results["mask_image"]
            overlay_img = analysis_results["overlay_image"]

            # Görselleri ayrı pencerelerde göster
            plt.figure(1); plt.imshow(original_img); plt.title("Orijinal Görüntü"); plt.axis('off')
            plt.figure(2); plt.imshow(mask_img, cmap='gray'); plt.title("Tahmin Edilen Maske"); plt.axis('off')
            plt.figure(3); plt.imshow(overlay_img); plt.title("Segmentasyon Sonucu"); plt.axis('off')
            plt.show()

        except Exception as e:
            print(f"Bir hata oluştu: {e}")