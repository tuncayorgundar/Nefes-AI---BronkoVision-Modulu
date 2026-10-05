import torch
import torch.nn as nn
import numpy as np
import os
from scipy.spatial import ConvexHull
import open3d as o3d
from PIL import Image, ImageChops
import cv2
import matplotlib.pyplot as plt
import io

# =============================================================================
# 1. MİMARİ SINIFLARI VE YARDIMCI FONKSİYONLAR (Değişiklik yok)
# =============================================================================
# ... (PointNetEncoder, PointNetDecoder, PointNetAutoencoder, 
#      generate_point_cloud_from_mask, analyze_3d_properties, 
#      visualize_point_clouds_to_image sınıfları ve fonksiyonları
#      önceki kodla birebir aynı olduğu için buraya eklemiyorum.
#      Aşağıdaki kodun çalışması için bu tanımlamaların kodun başında
#      olduğundan emin olun.)
class PointNetEncoder(nn.Module):
    def __init__(self, latent_dim=256):
        super(PointNetEncoder, self).__init__()
        self.conv1 = nn.Conv1d(3, 64, 1); self.bn1 = nn.BatchNorm1d(64)
        self.conv2 = nn.Conv1d(64, 128, 1); self.bn2 = nn.BatchNorm1d(128)
        self.conv3 = nn.Conv1d(128, latent_dim, 1); self.bn3 = nn.BatchNorm1d(latent_dim)
    def forward(self, x):
        x = x.transpose(2, 1)
        x = nn.functional.relu(self.bn1(self.conv1(x)))
        x = nn.functional.relu(self.bn2(self.conv2(x)))
        x = self.bn3(self.conv3(x))
        x = torch.max(x, 2, keepdim=True)[0]
        x = x.view(-1, 256)
        return x

class PointNetDecoder(nn.Module):
    def __init__(self, num_points=2048, latent_dim=256):
        super(PointNetDecoder, self).__init__()
        self.num_points = num_points
        self.fc1 = nn.Linear(latent_dim, 512); self.bn1 = nn.BatchNorm1d(512)
        self.fc2 = nn.Linear(512, 1024); self.bn2 = nn.BatchNorm1d(1024)
        self.fc3 = nn.Linear(1024, self.num_points * 3)
    def forward(self, x):
        x = nn.functional.relu(self.bn1(self.fc1(x)))
        x = nn.functional.relu(self.bn2(self.fc2(x)))
        x = self.fc3(x)
        x = x.view(-1, self.num_points, 3)
        return x

class PointNetAutoencoder(nn.Module):
    def __init__(self, num_points=2048, latent_dim=256):
        super(PointNetAutoencoder, self).__init__()
        self.encoder = PointNetEncoder(latent_dim=latent_dim)
        self.decoder = PointNetDecoder(num_points=num_points, latent_dim=latent_dim)
    def forward(self, x):
        return self.decoder(self.encoder(x))
        
def generate_point_cloud_from_mask(mask_pil, depth_factor=0.3):
    try:
        mask = np.array(mask_pil.convert("L"))
        if np.sum(mask) < 50: return None
        dist_transform = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
        if np.max(dist_transform) > 0:
            depth_map = dist_transform / np.max(dist_transform)
        else:
            depth_map = dist_transform
        y_coords, x_coords = np.where(mask > 0)
        z_coords = depth_map[y_coords, x_coords] * depth_factor
        point_cloud = np.stack((x_coords, y_coords, z_coords), axis=1)
        return point_cloud
    except Exception as e:
        print(f"HATA: Nokta bulutu oluşturulurken sorun oluştu: {e}")
        return None

def analyze_3d_properties(point_cloud):
    report = {}
    if point_cloud is None or len(point_cloud) < 50:
        report["tespit_3d"] = "Analiz için yetersiz 3D nokta."
        return report
    try:
        hull = ConvexHull(point_cloud)
        report["tespit_3d"] = "3D Tümör Yapısı Analiz Edildi."
        report["hacim_convex_hull"] = hull.volume
        report["yuzey_alani_convex_hull"] = hull.area
        if hull.volume > 0 and hull.area > 0:
            sphericity = (np.pi**(1/3) * (6 * hull.volume)**(2/3)) / hull.area
            report["sekil_kuresellik_3d"] = sphericity
    except Exception as e:
        report["analiz_hatasi_3d"] = f"Convex Hull oluşturulamadı: {e}"
    return report

def visualize_point_clouds_to_image(original_pc, reconstructed_pc):
    try:
        pcd_original = o3d.geometry.PointCloud(); pcd_original.points = o3d.utility.Vector3dVector(original_pc); pcd_original.paint_uniform_color([0, 0.651, 0.929])
        pcd_reconstructed = o3d.geometry.PointCloud(); pcd_reconstructed.points = o3d.utility.Vector3dVector(reconstructed_pc); pcd_reconstructed.paint_uniform_color([1, 0.706, 0])
        pcd_reconstructed.translate((np.max(original_pc[:,0]) * 1.5, 0, 0))

        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False, width=800, height=600)
        vis.add_geometry(pcd_original); vis.add_geometry(pcd_reconstructed)
        vis.get_render_option().background_color = np.asarray([0, 0, 0])
        vis.poll_events(); vis.update_renderer()
        
        image = vis.capture_screen_float_buffer(False)
        vis.destroy_window()
        
        return Image.fromarray((np.asarray(image) * 255).astype(np.uint8))
    except Exception as e:
        print(f"HATA: 3D görselleştirme oluşturulamadı: {e}")
        return None
# =============================================================================
# 2. ANA ANALİZ FONKSİYONU (Değişiklik yok)
# =============================================================================
def analyze_mask_with_pointnet(mask_pil_image, model, num_points=2048):
    """
    Bir 2D maske alır, 3D'ye çevirir, PointNet++ ile analiz eder ve
    sonuçları doğru formatta döndürür.
    """
    # ... (Fonksiyonun başındaki tüm hesaplama kodları aynı kalacak)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device); model.eval()
    
    results = {}
    original_pc_raw = generate_point_cloud_from_mask(mask_pil_image)
    if original_pc_raw is None:
        results["rapor_3d"] = {"tespit_3d": "Geçerli 2D maske bulunamadığı için 3D analiz yapılamadı."}
        return results

    if len(original_pc_raw) > num_points:
        choice = np.random.choice(len(original_pc_raw), num_points, replace=False)
        pc_sampled = original_pc_raw[choice, :]
    else:
        choice = np.random.choice(len(original_pc_raw), num_points, replace=True)
        pc_sampled = original_pc_raw[choice, :]

    pc_tensor = torch.from_numpy(pc_sampled).float()
    centroid = torch.mean(pc_tensor, dim=0)
    pc_normalized = pc_tensor - centroid
    furthest_distance = torch.max(torch.sqrt(torch.sum(pc_normalized ** 2, dim=1)))
    if furthest_distance > 0:
        pc_normalized = pc_normalized / furthest_distance
    
    input_tensor = pc_normalized.unsqueeze(0).to(device)

    with torch.no_grad():
        reconstructed_pc_tensor = model(input_tensor)

    original_pc_np = pc_normalized.cpu().numpy()
    reconstructed_pc_np = reconstructed_pc_tensor.squeeze(0).cpu().numpy()
    
    analysis_3d_report = analyze_3d_properties(reconstructed_pc_np)
    gorsel_3d = visualize_point_clouds_to_image(original_pc_np, reconstructed_pc_np)
    
    # --- DÜZELTME BURADA ---
    # Sonuçları, pipeline'ın beklediği gibi, raporu ayrı bir anahtar altına alarak döndür.
    results = {
        "rapor_3d": analysis_3d_report, # Sayısal raporu 'rapor_3d' anahtarı altına al
        "gorsel_3d": gorsel_3d
    }
    return results

# =============================================================================
# 3. ANA ÇALIŞTIRMA BÖLÜMÜ (ODAKLANMIŞ ÇIKTI İÇİN GÜNCELLENDİ)
# =============================================================================
if __name__ == "__main__":
    
    # --- AYARLAR ---
    UNET_MODEL_PATH = 'best_model_unet.pth'
    POINTNET_MODEL_PATH = 'pointnet_autoencoder_final.pth'
    IMAGE_TO_TEST_PATH = 'test_kanser.png'
    NUM_POINTS_FOR_POINTNET = 2048

    mask_variable = None # Başlangıçta maske yok
    
    try:
        # --- ARKA PLAN ADIMI: U-Net ile maske al ---
        from entegre_sistem.modules.unet import analyze_image_with_unet 
        print("U-Net modülünden 2D maske alınıyor...")
        # U-Net'in tüm sonuçlarını almak yerine sadece maskeyi alıyoruz
        mask_variable = analyze_image_with_unet(UNET_MODEL_PATH, IMAGE_TO_TEST_PATH).get('mask_image')
        print("Maske başarıyla alındı.")

    except ImportError:
        print("UYARI: 'attention_unet.py' bulunamadı. Test için basit bir maske oluşturuluyor.")
        mask_variable = Image.new("L", (224, 224), 0)
        mask_np = np.array(mask_variable); cv2.circle(mask_np, (112, 112), 40, 255, -1); mask_variable = Image.fromarray(mask_np)
    except Exception as e:
        print(f"U-Net analizi sırasında bir hata oluştu: {e}")

    # --- ANA ADIM: POINTNET++ İLE 3D ANALİZ ---
    if mask_variable:
        try:
            print("\nPointNet++ Autoencoder modeli yükleniyor...")
            pointnet_model = PointNetAutoencoder(num_points=NUM_POINTS_FOR_POINTNET)
            pointnet_model.load_state_dict(torch.load(POINTNET_MODEL_PATH, map_location=torch.device('cpu')))
            
            print("PointNet++ ile 3D analiz başlatılıyor...")
            pointnet_results = analyze_mask_with_pointnet(mask_variable, pointnet_model, num_points=NUM_POINTS_FOR_POINTNET)
            print("3D Analiz başarıyla tamamlandı.")

            # --- ODAKLANMIŞ FİNAL RAPORU ---
            print("\n" + "="*40)
            print("   3D TÜMÖR YAPI ANALİZ RAPORU")
            print("="*40)
            print(f"{'Tespit':<28}: {pointnet_results.get('tespit_3d', 'N/A')}")
            if pointnet_results.get('tespit_3d') == "3D Tümör Yapısı Analiz Edildi.":
                print(f"{'Hacim (Convex Hull)':<28}: {pointnet_results.get('hacim_convex_hull', 0):.4f} birim^3")
                print(f"{'Yüzey Alanı (Convex Hull)':<28}: {pointnet_results.get('yuzey_alani_convex_hull', 0):.4f} birim^2")
                print(f"{'Şekil (Küresellik)':<28}: {pointnet_results.get('sekil_kuresellik_3d', 0):.4f} (1.0 = Küre)")
            print("="*40)
            
            # --- ODAKLANMIŞ FİNAL GÖRSELİ ---
            gorsel_3d_variable = pointnet_results.get("gorsel_3d")
            if gorsel_3d_variable:
                print("\n3D görsel bir değişkende saklanıyor. Şimdi gösteriliyor...")
                gorsel_3d_variable.show(title="3D Model: Orijinal (Mavi) vs. PointNet++ (Turuncu)")
            else:
                print("\n3D görsel oluşturulamadı.")

        except Exception as e:
            print(f"PointNet++ analizi sırasında bir hata oluştu: {e}")
    else:
        print("\nGeçerli bir 2D maske olmadığı için 3D analiz adımı atlandı.")