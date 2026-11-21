import os, csv, cv2
import numpy as np

IMAGE_PATH = "slab_01.jpg"
SAVE_DIR = "out"
CSV_PATH = os.path.join(SAVE_DIR, "results.csv")
STAGES_DIR = os.path.join(SAVE_DIR, "stages")

CANNY_MIN = 0
CANNY_MAX = 74
CLOSE_ITER = 5
ALPHA = 3.0
BETA = 50

ROI_Y0 = 0.47
ROI_Y1 = 0.58
ROI_X0 = 0.15
ROI_X1 = 0.85

A_THR = 1.25
RMS_THR = 5.5

#FONKSİYNLAR:
#----

def nothing(x):
    pass

#---

def decide_curvature(a2, rms, side, a_thr=A_THR, rms_thr=RMS_THR):
    #-
    #a2~0 ve RMS küçükse: düz
    if abs(a2) < a_thr and rms < rms_thr:
        return "duz"
    if side == 'left':
        # sol kenar: a2>0 => sağa açılır => içbükey
        return "disbukey" if a2 > 0 else "icbukey"
    else:
        #sağ kenar: a2>0 => sağa açılır => dışbükey
        return "icbukey" if a2 > 0 else "disbukey"

def save_stage(stage_dir, name, img):
    if stage_dir is None:
        return
    os.makedirs(stage_dir, exist_ok=True)
    cv2.imwrite(os.path.join(stage_dir, f"{name}.jpg"), img)

def analyze_frame_with_your_pipeline(img_bgr, stage_dir=None):
    img = cv2.resize(img_bgr, (960,540))
    save_stage(stage_dir, "01_resized", img)

    adjusted = cv2.convertScaleAbs(img, alpha=ALPHA, beta=BETA)
    save_stage(stage_dir, "02_adjusted", adjusted)

    gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    save_stage(stage_dir, "03_gray", gray)

    blur = cv2.GaussianBlur(gray, (5,3), 0)
    save_stage(stage_dir, "04_blur", blur)

    edges = cv2.Canny(blur, CANNY_MIN, CANNY_MAX)
    save_stage(stage_dir, "05_edges_canny", edges)

    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3,3), np.uint8), iterations=CLOSE_ITER)
    save_stage(stage_dir, "06_edges_closed", edges)

    #beyaz çizgi siyah zemin
    mask = cv2.bitwise_not(edges)
    save_stage(stage_dir, "07_mask_inverted", mask)

    #orta bölge filtresi
    H, W = mask.shape
    y0, y1 = int(H*ROI_Y0), int(H*ROI_Y1)
    x0, x1 = int(W*ROI_X0), int(W*ROI_X1)

    roi = mask[y0:y1, x0:x1].copy()
    save_stage(stage_dir, "08_roi_raw", roi)

    roi = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, np.ones((5,5), np.uint8), iterations=2)
    save_stage(stage_dir, "09_roi_closed", roi)

    #en büyük bağlı bileşenin seçimi
    num, labels, stats, _ = cv2.connectedComponentsWithStats(roi, connectivity=8)

    if num > 1:
        idx = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
        largest = (labels == idx).astype(np.uint8) * 255
    else:
        largest = roi
    save_stage(stage_dir, "10_largest_component", largest)

    mask_big = np.zeros_like(mask)
    mask_big[y0:y1, x0:x1] = largest # tam görüntü boyutuna geri koy
    save_stage(stage_dir, "11_mask_big", mask_big)

    #5 tanw Y satırı (y0 ve y1 dahil)
    y_samples = np.linspace(y0, y1, 6, dtype=int)

    x_left, x_right, y_used = [], [], []

    for y in y_samples:
        row = mask_big[y, x0:x1]
        xs = np.where(row > 0)[0] # beyazların x indeksleri (yerel)
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

    if y_used.size >= 3: # en az 3 nokta olmalı (2.dereceden)
        #sayısal kararlılık için y'yi 0..1 aralığına normalizasyon
        yN = (y_used - y_used.min()) / (y_used.max() - y_used.min() + 1e-9)

        #sol kenar
        bL, cL = np.polyfit(yN, x_left, 1)
        a2L, b2L, c2L = np.polyfit(yN, x_left, 2)
        rmsL = float(np.sqrt(np.mean((x_left - (bL * yN + cL)) ** 2)))

        #sağ kenar
        bR, cR = np.polyfit(yN, x_right, 1)
        a2R, b2R, c2R = np.polyfit(yN, x_right, 2)
        rmsR = float(np.sqrt(np.mean((x_right - (bR * yN + cR)) ** 2)))

        #karar
        decL = decide_curvature(a2L, rmsL, side='left')
        decR = decide_curvature(a2R, rmsR, side='right')

        #seçilen 5 noktayı çiz
        for y, x in zip(y_used.astype(int), x_left.astype(int)):
            cv2.circle(overlay, (x, y), 3, (0, 255, 255), -1) # sol: sarı
        for y, x in zip(y_used.astype(int), x_right.astype(int)):
            cv2.circle(overlay, (x, y), 3, (0, 0, 255), -1) # sağ: kırmızı

        info = f"Sol: {decL} | a={a2L:.3f}, RMS={rmsL:.1f}px   Sag: {decR} | a={a2R:.3f}, RMS={rmsR:.1f}px"
        cv2.putText(overlay, info, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 3, cv2.LINE_AA)
        cv2.putText(overlay, info, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)
        save_stage(stage_dir, "12_overlay_final", overlay)

        return True, overlay, {"left": {"label": decL, "a2": float(a2L), "rms": float(rmsL)},
                               "right":{"label": decR, "a2": float(a2R), "rms": float(rmsR)},
                               "info": info}
    else:
        cv2.putText(overlay, "5 satir icin yeterli piksel yok", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        save_stage(stage_dir, "12_overlay_final", overlay)
        return False, overlay, {"info":"yetersiz nokta"}

#--

def read_image(path):
    img = cv2.imread("slab_1.jpeg")
    if img is None:
        raise RuntimeError(f"Resim acilamadi: {path}")
    return img

#KAYIT-
def append_csv(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    write_header = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if write_header: w.writeheader()
        w.writerow(row)

#ANA AKIŞ (tek fotoğraf)
def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    frame = read_image(IMAGE_PATH)

    ok, overlay, res = analyze_frame_with_your_pipeline(frame, stage_dir=STAGES_DIR)

    base = os.path.splitext(os.path.basename(IMAGE_PATH))[0]
    jpg = os.path.join(SAVE_DIR, f"overlay_{base}.jpg")
    cv2.imwrite(jpg, overlay)

    row = {
        "image": IMAGE_PATH,
        "left_label": (res["left"]["label"] if ok else ""),
        "left_a2": (f'{res["left"]["a2"]:.6f}' if ok else ""),
        "left_rms": (f'{res["left"]["rms"]:.3f}' if ok else ""),
        "right_label": (res["right"]["label"] if ok else ""),
        "right_a2": (f'{res["right"]["a2"]:.6f}' if ok else ""),
        "right_rms": (f'{res["right"]["rms"]:.3f}' if ok else ""),
        "info": res["info"],
        "overlay_path": jpg
    }
    append_csv(CSV_PATH, row)
    print(f"{res['info']} | {jpg}")
    print(f"Ara asama ciktilari: {STAGES_DIR}")

#Kodu çalıştırma---
if __name__ == "__main__":
    main()