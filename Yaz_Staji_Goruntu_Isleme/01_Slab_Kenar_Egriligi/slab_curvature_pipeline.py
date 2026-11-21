import cv2
import numpy as np

# ==========================================
# GÖRÜNTÜ İŞLEME SABİTLERİ (slab tipinden bağımsız, ortak)
# ==========================================
CANNY_MIN = 0
CANNY_MAX = 74
CLOSE_ITER = 5
ALPHA = 3.0
BETA = 50

A_THR = 1.25
RMS_THR = 5.5

# Otomasyondan gelen slab bilgisiyle EŞLEŞEN ROI tablosu.
# Yeni bir slab tipi/boyutu çıktığında sadece buraya bir satır eklenecek.
# y0/y1/x0/x1 değerleri, resize edilmiş (960x540) görüntü üzerinde ORAN (0-1) olarak tutulur.
SLAB_ROI_CONFIG = {
    "TIP_1": {"y0": 0.47, "y1": 0.58, "x0": 0.27, "x1": 0.73},   # dar/kucuk slab
    "TIP_2": {"y0": 0.47, "y1": 0.58, "x0": 0.15, "x1": 0.85},   # genis/buyuk slab
}

# Otomasyon beklenmedik bir tip gönderirse (veya eşleşme bulunamazsa) kullanılacak
# güvenli varsayılan. Sistem çökmesin diye TIP_2'yi (orijinal/varsayılan) baz aldık.
DEFAULT_ROI_KEY = "TIP_2"


def get_roi_for_slab(slab_info):
    """
    Otomasyondan gelen slab bilgisini SLAB_ROI_CONFIG'teki bir ROI'ye eşler.

    slab_info: şimdilik basit bir string/kod bekleniyor (örn. "TIP_1", "TIP_2").
    Otomasyonun gönderdiği gerçek formatı netleştikçe (ölçü, id, vs.)
    bu fonksiyonun içini güncellemek yeterli olacak; pipeline'ın geri kalanı değişmez.
    """
    key = str(slab_info).strip().upper()
    if key in SLAB_ROI_CONFIG:
        return key, SLAB_ROI_CONFIG[key]

    print(f"[UYARI] Bilinmeyen slab tipi: '{slab_info}'. "
          f"Varsayılan ROI ({DEFAULT_ROI_KEY}) kullanılacak.")
    return DEFAULT_ROI_KEY, SLAB_ROI_CONFIG[DEFAULT_ROI_KEY]


# ==========================================
# KARAR FONKSİYONU (değişmedi)
# ==========================================
def decide_curvature(a2, rms, side, a_thr=A_THR, rms_thr=RMS_THR):
    if abs(a2) < a_thr and rms < rms_thr:
        return "duz"
    if side == 'left':
        return "disbukey" if a2 > 0 else "icbukey"
    else:
        return "icbukey" if a2 > 0 else "disbukey"


# ==========================================
# ANA GÖRÜNTÜ İŞLEME ALGORİTMASI
# (tek fark: ROI artık sabit değil, parametre olarak geliyor)
# ==========================================
def analyze_frame_with_your_pipeline(img_bgr, roi):
    """
    roi: {"y0":.., "y1":.., "x0":.., "x1":..} formatında, 0-1 arası oranlar.
    get_roi_for_slab(...) çağrısından dönen ikinci eleman doğrudan buraya verilebilir.
    """
    img = cv2.resize(img_bgr, (960, 540))
    adjusted = cv2.convertScaleAbs(img, alpha=ALPHA, beta=BETA)
    gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 3), 0)

    canny_edges = cv2.Canny(blur, CANNY_MIN, CANNY_MAX)
    closed_edges = cv2.morphologyEx(canny_edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=CLOSE_ITER)

    mask = cv2.bitwise_not(closed_edges)

    H, W = mask.shape
    y0, y1 = int(H * roi["y0"]), int(H * roi["y1"])
    x0, x1 = int(W * roi["x0"]), int(W * roi["x1"])

    roi_img = mask[y0:y1, x0:x1].copy()
    roi_closed = cv2.morphologyEx(roi_img, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)

    num, labels, stats, _ = cv2.connectedComponentsWithStats(roi_closed, connectivity=8)

    if num > 1:
        idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        largest = (labels == idx).astype(np.uint8) * 255
    else:
        largest = roi_closed

    mask_big = np.zeros_like(mask)
    mask_big[y0:y1, x0:x1] = largest

    y_samples = np.linspace(y0, y1, 6, dtype=int)
    x_left, x_right, y_used = [], [], []

    for y in y_samples:
        row = mask_big[y, x0:x1]
        xs = np.where(row > 0)[0]
        if xs.size:
            xL = x0 + xs.min()
            xR = x0 + xs.max()
            y_used.append(y)
            x_left.append(int(xL))
            x_right.append(int(xR))

    y_used = np.array(y_used, dtype=np.float32)
    x_left = np.array(x_left, dtype=np.float32)
    x_right = np.array(x_right, dtype=np.float32)

    overlay = img.copy()
    cv2.rectangle(overlay, (x0, y0), (x1, y1), (0, 255, 0), 1)  # ROI kutusu (görsel kontrol için)

    if y_used.size >= 3:
        yN = (y_used - y_used.min()) / (y_used.max() - y_used.min() + 1e-9)

        bL, cL = np.polyfit(yN, x_left, 1)
        a2L, b2L, c2L = np.polyfit(yN, x_left, 2)
        rmsL = float(np.sqrt(np.mean((x_left - (bL * yN + cL)) ** 2)))

        bR, cR = np.polyfit(yN, x_right, 1)
        a2R, b2R, c2R = np.polyfit(yN, x_right, 2)
        rmsR = float(np.sqrt(np.mean((x_right - (bR * yN + cR)) ** 2)))

        decL = decide_curvature(a2L, rmsL, side='left')
        decR = decide_curvature(a2R, rmsR, side='right')

        for y, x in zip(y_used.astype(int), x_left.astype(int)):
            cv2.circle(overlay, (x, y), 3, (0, 255, 255), -1)
        for y, x in zip(y_used.astype(int), x_right.astype(int)):
            cv2.circle(overlay, (x, y), 3, (0, 0, 255), -1)

        info = f"Sol: {decL} | a={a2L:.3f}, RMS={rmsL:.1f}px   Sag: {decR} | a={a2R:.3f}, RMS={rmsR:.1f}px"
        cv2.putText(overlay, info, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(overlay, info, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

        return True, overlay, {"info": info, "left": decL, "right": decR,
                                "a2_left": a2L, "rms_left": rmsL,
                                "a2_right": a2R, "rms_right": rmsR}
    else:
        cv2.putText(overlay, "5 satir icin yeterli piksel yok", (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return False, overlay, {"info": "yetersiz nokta"}


# ==========================================
# OTOMASYONDAN GELEN slab_info İLE ÇAĞRILACAK ANA FONKSİYON
# ==========================================
def process_slab(img_bgr, slab_info):
    """
    Otomasyon bu fonksiyonu çağıracak: process_slab(görüntü, slab_info)
    slab_info şimdilik "TIP_1" / "TIP_2" gibi bir kod bekleniyor (geçici).
    """
    roi_key, roi = get_roi_for_slab(slab_info)
    success, overlay, result = analyze_frame_with_your_pipeline(img_bgr, roi)
    result["roi_key_used"] = roi_key
    result["roi"] = roi
    return success, overlay, result

# ==========================================
# HIZLI TEST (elimizdeki 2 örnek görüntüyle)
# ==========================================
if __name__ == "__main__":
    tests = [
        ("slab_1.jpeg", "TIP_1"),
        ("slab3.jpeg", "TIP_2"),
    ]
    for path, slab_info in tests:
        img = cv2.imread(path)
        if img is None:
            print(f"[ATLANDI] {path} bulunamadi")
            continue
        ok, overlay, result = process_slab(img, slab_info)
        print(f"{path} (slab_info={slab_info}, kullanilan_roi={result.get('roi_key_used')}): {result['info']}")
        out_name = f"sonuc_{path.rsplit('.',1)[0]}.png"
        cv2.imwrite(out_name, overlay)

        print(f"  -> {out_name} kaydedildi")