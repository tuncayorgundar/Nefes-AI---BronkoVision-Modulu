# Nefes AI - BronkoVision Modülü

## Proje Genel Özeti
Nefes AI, akciğer kanseri teşhis ve tedavi süreçlerinde multimodal veri entegrasyonu ve derin öğrenme teknolojileri kullanarak kişiselleştirilmiş tedavi optimizasyonu sağlayan entegre bir yapay zeka platformudur. Proje; bronkoskopi görüntüleri, sıvı biyopsi verileri ve biyobelirteçlerin sinerjistik analizini gerçekleştirerek onkoloji protokollerine modern bir yaklaşım getirmeyi hedeflemektedir.

## BronkoVision Modülü Özeti
BronkoVision, akciğer kanserinin çok modlu görüntü verilerini (yüksek çözünürlüklü bronkoskopi - HD-B ve optik spektral görüntüleme - OSI) işleyen bütüncül bir analiz platformudur. Modül, derin öğrenme algoritmaları aracılığıyla insan gözüyle fark edilemeyen sub-vizüel özellikleri çıkararak kantitatif karar destek metrikleri üretir. Tümörün morfolojik karakteristiklerini, histolojik alt tiplerini ve mikroçevresel özelliklerini analiz ederek tedavi planlamasına nesnel bir zemin hazırlar.

## Kullanılan Teknolojiler
* **Derin Öğrenme ve Backend:** Python (TensorFlow / PyTorch), FastAPI framework.
* **Tümör Tespiti ve Sınıflandırma:** ResNet-152 mimarisi tabanlı Evrişimli Sinir Ağları (CNN).
* **Mikroçevre Segmentasyonu:** Attention U-Net (Dikkat Mekanizmalı U-Net).
* **3D Modelleme:** PointNet++ mimarisi ile nokta bulutu tabanlı 3B rekonstrüksiyon.
* **Fonksiyonel Analiz:** Spektral görüntüleme analizleri.
* **Veri Standartları:** DICOM uyumlu görüntü işleme.

## Modül Mimarisi ve İş Akışı
BronkoVision modülü, hata yönetimi ve veri bütünlüğü kontrolleri açısından `try-catch` blokları ile sağlamlaştırılmış bir yazılım mimarisine sahiptir. Herhangi bir veri eksikliği durumunda sistem dinamik olarak çalışmaya devam ederek iş akışının sekteye uğramasını engeller.

1. **Görüntü Ön İşleme:** HD-B ve spektral görüntü verilerinin analiz için hazırlanması.
2. **Tümör Segmentasyonu ve Karakterizasyonu:** ResNet-152 ile tümör lezyonlarının otomatik tespiti ve sınıflandırılması. Eş zamanlı olarak Attention U-Net ile tümör mikroçevresindeki immün hücre infiltrasyonu ve vasküler yapıların piksel düzeyinde segmentasyonu.
3. **3D Rekonstrüksiyon ve Volumetrik Analiz:** İki boyutlu kesitlerin PointNet++ mimarisi ile üç boyutlu topolojik bir modele dönüştürülerek hacim ve invazivlik potansiyelinin hesaplanması.
4. **Fonksiyonel Analiz:** Spektral analizler ile tedaviye dirençli hipoksik bölgelerin haritalandırılması.

## Temel Özellikler
* **Otomatik Lezyon Analizi:** Tümör lezyonlarını yüksek doğrulukla saptar ve histolojik alt tiplerine (adenokarsinom, skuamöz hücreli karsinom vb.) göre sınıflandırır.
* **Hassas Mikroçevre Segmentasyonu:** Fibroblast aktivitesi, tümör infiltre eden lenfositler (TILs) ve vaskülarizasyon paternlerini piksel düzeyinde analiz ederek immünoterapi yanıtı için mekânsal biyobelirteçler oluşturur.
* **Kantitatif Morfolojik Metrikler:** Tümör hacmi, yüzey özellikleri ve küresellikten sapma gibi invazivlik göstergelerini objektif olarak hesaplar.
* **Hipoksi Haritalama:** Tedaviye dirençli bölgeleri in situ tespit ederek kişiselleştirilmiş tedavi stratejilerine girdi sağlar.
* **Entegre Karar Desteği:** Çıktılar, tedavi protokollerinin optimizasyonu için doğrudan diğer sistem bileşenleriyle (DozOptimize) paylaşılır.
