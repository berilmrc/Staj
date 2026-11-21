import cv2
import numpy as np

def nothing(x):
    pass

dosya_adi = "ornek.jpg"
image = cv2.imread(dosya_adi)
if image is None:
    print(f"HATA: '{dosya_adi}' dosyası bulunamadı!")
    exit()

image = cv2.resize(image, (800, 600), interpolation=cv2.INTER_AREA)
display_base = image.copy()
gray = cv2.cvtColor(display_base, cv2.COLOR_BGR2GRAY)

# Hafif gürültü temizliği (kenarları bozmadan)
denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

# Otsu ile otomatik referans eşik
oto_esik, _ = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

cv2.namedWindow('Panel', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Panel', 450, 260)
cv2.createTrackbar("Hassasiyet (%)", "Panel", 85, 120, nothing)   # Otsu'yu esnetir
cv2.createTrackbar("Kapama_Gucu", "Panel", 3, 15, nothing)        # kopuk sınırları birleştirir
cv2.createTrackbar("Min_Alan", "Panel", 30, 500, nothing)         # küçük benekleri siler

while True:
    tolerans = cv2.getTrackbarPos("Hassasiyet (%)", "Panel") / 100.0
    kapama_gucu = cv2.getTrackbarPos("Kapama_Gucu", "Panel")
    min_alan = cv2.getTrackbarPos("Min_Alan", "Panel")

    dinamik_esik = int(np.clip(oto_esik * tolerans, 1, 254))
    _, raw_mask = cv2.threshold(denoised, dinamik_esik, 255, cv2.THRESH_BINARY)

    # 1. Kopuk tane sınırlarını kapatmak için GÜÇLÜ morfolojik kapama
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kapama_gucu*2+1, kapama_gucu*2+1))
    closed = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, k_close)

    # 2. Ufak gürültü beneklerini alan bazlı temizle (connected components)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(closed, connectivity=8)
    clean_mask = np.zeros_like(closed)
    for i in range(1, num_labels):
        if stats[i, cv2.CC_STAT_AREA] >= min_alan:
            clean_mask[labels == i] = 255

    toplam_piksel = clean_mask.shape[0] * clean_mask.shape[1]
    beyaz_piksel = cv2.countNonZero(clean_mask)
    faz_orani = (beyaz_piksel / toplam_piksel) * 100

    segmented_overlay = display_base.copy()
    mask_bolgesi = (clean_mask == 255)
    if np.any(mask_bolgesi):
        segmented_overlay[mask_bolgesi, 0] = (segmented_overlay[mask_bolgesi, 0] * 0.4).astype(np.uint8)
        segmented_overlay[mask_bolgesi, 1] = (segmented_overlay[mask_bolgesi, 1] * 0.4).astype(np.uint8)
        segmented_overlay[mask_bolgesi, 2] = np.clip(
            segmented_overlay[mask_bolgesi, 2] * 0.6 + 150, 0, 255
        ).astype(np.uint8)

    cv2.putText(segmented_overlay, f"Esik:{dinamik_esik} Oran:%{faz_orani:.2f}",
                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

    cv2.imshow("1 - Segmentasyon", segmented_overlay)
    cv2.imshow("2 - Maske", clean_mask)

    if cv2.waitKey(20) & 0xFF == ord('q'):
        print(f"\nFaz Orani: %{faz_orani:.2f}")
        break

cv2.destroyAllWindows()