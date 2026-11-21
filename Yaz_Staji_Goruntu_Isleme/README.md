# Yaz Stajı · Görüntü İşleme ile Kalite Kontrol

**Yaz stajı · Ağustos–Eylül 2026**

Bir üretim hattında kalite kontrolü desteklemek için OpenCV tabanlı iki görüntü işleme aracı geliştirdim:

1. **Slab kenar eğriliği tespiti:** Kameradan alınan görüntüde slabın sol ve sağ kenarlarını bulup her kenarı *düz*, *iç bükey* veya *dış bükey* olarak sınıflandırır.
2. **Mikroyapı faz analizi:** Metal mikroyapı görüntülerinde renk / parlaklık farkına göre fazları ayırır ve her fazın alan oranını yüzde olarak hesaplar.

> Şirkete ait görüntüler, veri setleri ve belgeler bu repoda yer almaz. Kodlar kendi görüntülerinizle çalıştırılabilir.

## 1. Slab kenar eğriliği tespiti

[`01_Slab_Kenar_Egriligi/`](01_Slab_Kenar_Egriligi)

**Yöntem**

1. Görüntü yeniden boyutlandırılır ve slab gövdesine denk gelen bir ilgi alanı (ROI) seçilir.
2. Slab bölgesi maskelenir: sıcak slabın renk bilgisiyle (HSV) ya da Canny kenar bulma + morfolojik kapama ile.
3. Maskenin sol ve sağ sınırlarından kenar noktaları örneklenir.
4. Her kenara ikinci derece polinom uydurulur (`np.polyfit`). Eğrilik katsayısı `a2` ve uyum hatası `RMS` hesaplanır.
5. Karar: `|a2|` ve `RMS` eşiklerin altındaysa kenar **düz**, değilse `a2`'nin işaretine göre **iç bükey / dış bükey**.
6. Sonuçlar CSV'ye yazılır, ara aşama görüntüleri `out/stages/` klasörüne kaydedilir.

**Öğrendiğim önemli nokta:** Sabit bir ROI, farklı genişlikteki slablarda hatalı sonuç veriyordu. ROI slabın altındaki merdanelere taşınca morfolojik kapama slabı gürültüyle birleştiriyor ve kenarlar yanlış bulunuyordu. Çözüm olarak her slab tipi için ayrı ROI tanımlanan bir yapı kurdum. Doğrulamada kenar uyum hatası 0,5 pikselin altına indi.

| Dosya | Açıklama |
|---|---|
| `egrilik_renk_maskesi.py` | Sıcak slabı HSV renk maskesiyle ayıran sürüm |
| `egrilik_canny_roi.py` | Canny + ROI + polinom uydurma ile çalışan sürüm |

## 2. Mikroyapı faz analizi

[`02_Mikroyapi_Faz_Analizi/`](02_Mikroyapi_Faz_Analizi)

**Yöntem**

1. Görüntü HSV renk uzayına çevrilir.
2. Seçilen faz için renk merkezi (H), tolerans ve S/V alt sınırlarıyla ham maske oluşturulur.
3. Morfolojik açma (gürültü silme) ve kapama (boşluk doldurma) ile maske temizlenir.
4. Faz piksellerinin toplam piksele oranı **faz yüzdesi** olarak verilir. Sonuç renkli bir bindirme (overlay) olarak gösterilir.

| Dosya | Açıklama |
|---|---|
| `faz_ayristirma_arayuz.py` | Tkinter arayüzü: fotoğraf aç, kaydırıcılarla eşikleri ayarla, oranı anlık gör |
| `faz_ayristirma_toplu.py` | Klasördeki görüntülerden rastgele seçip analiz eden ve tüm ara aşamaları kaydeden sürüm |
| `otsu_esikleme.py` | Otsu eşiğini referans alıp ayarlanabilir hassasiyetle tane sınırlarını ayıran deneme |
| `hsv_oranlama.py` | HSV kaydırıcılarıyla maske çıkarıp alan oranı hesaplayan ilk sürüm |

## Çalıştırma

```bash
pip install -r requirements.txt
python 02_Mikroyapi_Faz_Analizi/faz_ayristirma_arayuz.py
```

Slab betiklerinde `IMAGE_PATH` değişkenini kendi görüntünüzün yoluyla değiştirin.

## Kullanılan teknolojiler

Python · OpenCV · NumPy · Tkinter · Pillow · HSV renk uzayı · Morfolojik işlemler · Otsu eşikleme · Polinom uydurma
