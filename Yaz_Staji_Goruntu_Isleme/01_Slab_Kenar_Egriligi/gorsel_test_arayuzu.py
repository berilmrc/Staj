import cv2
import numpy as np

# ==========================================
# GÖRÜNTÜ İŞLEME VE KARAR SABİTLERİ
# ==========================================
CANNY_MIN = 20
CANNY_MAX = 74
CLOSE_ITER = 5
ALPHA = 3.0
BETA = 50

ROI_Y0 = 0.47
ROI_Y1 = 0.56
ROI_X0 = 0.15
ROI_X1 = 0.85

A_THR = 1.25
RMS_THR = 5.5


# ==========================================
# KARAR FONKSİYONU
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
# ==========================================
def analyze_frame_with_your_pipeline(img_bgr):
    img = cv2.resize(img_bgr, (960, 540))
    adjusted = cv2.convertScaleAbs(img, alpha=ALPHA, beta=BETA)
    gray = cv2.cvtColor(adjusted, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 3), 0)

    # Ara çıktıları alabilmek için değişkenleri ayırdık
    canny_edges = cv2.Canny(blur, CANNY_MIN, CANNY_MAX)
    closed_edges = cv2.morphologyEx(canny_edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=CLOSE_ITER)

    mask = cv2.bitwise_not(closed_edges)

    H, W = mask.shape
    y0, y1 = int(H * ROI_Y0), int(H * ROI_Y1)
    x0, x1 = int(W * ROI_X0), int(W * ROI_X1)

    roi = mask[y0:y1, x0:x1].copy()
    roi_closed = cv2.morphologyEx(roi, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8), iterations=2)

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

    # Ara çıktıları sözlükte toplama
    debug_frames = {
        "1_Orijinal": img,
        "2_Parlaklik_Kontrast": adjusted,
        "3_Gri_Format": gray,
        "4_Gaussian_Blur": blur,
        "5_Canny_Kenar": canny_edges,
        "6_Morph_Close": closed_edges,
        "7_Ters_Maske": mask,
        "8_ROI_Kesimi": roi_closed,
        "9_En_Buyuk_Alan": largest,
        "10_Tam_Boyut_Maske": mask_big
    }

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

        debug_frames["11_Nihai_Sonuc"] = overlay
        return True, overlay, {"info": info, "debug": debug_frames}
    else:
        cv2.putText(overlay, "5 satir icin yeterli piksel yok", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        debug_frames["11_Nihai_Sonuc"] = overlay
        return False, overlay, {"info": "yetersiz nokta", "debug": debug_frames}


# ==========================================
# ÇALIŞTIRMA VE GÖRSELLEŞTİRME BÖLÜMÜ
# ==========================================
def preview(image, text, target_width=420, target_height=236):
    """Ara çıktıları standart boyuta getirir ve ismini yazar"""
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    height, width = image.shape[:2]
    scale = min(target_width / width, target_height / height)
    new_w, new_h = max(1, int(width * scale)), max(1, int(height * scale))

    resized = cv2.resize(image, (new_w, new_h))
    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)

    x_off, y_off = (target_width - new_w) // 2, (target_height - new_h) // 2
    canvas[y_off:y_off + new_h, x_off:x_off + new_w] = resized

    cv2.putText(canvas, text, (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
    return canvas


if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    image_path = filedialog.askopenfilename(title="Fotoğraf Seç", filetypes=[("Resimler", "*.jpg *.jpeg *.png")])
    root.destroy()

    if image_path:
        img = cv2.imread(image_path)
        if img is not None:
            success, final_img, data = analyze_frame_with_your_pipeline(img)

            # Ara çıktıları grid üzerinde birleştirme
            df = data["debug"]
            r1 = np.hstack(
                (preview(df["1_Orijinal"], "1-Orijinal"), preview(df["2_Parlaklik_Kontrast"], "2-Parlaklik/Kontrast"),
                 preview(df["3_Gri_Format"], "3-Gri Goruntu"), preview(df["4_Gaussian_Blur"], "4-Gaussian Blur")))
            r2 = np.hstack(
                (preview(df["5_Canny_Kenar"], "5-Canny Kenar"), preview(df["6_Morph_Close"], "6-Morph Close"),
                 preview(df["7_Ters_Maske"], "7-Ters Maske"), preview(df["8_ROI_Kesimi"], "8-ROI Kesimi")))
            r3 = np.hstack((preview(df["9_En_Buyuk_Alan"], "9-En Buyuk Alan"),
                            preview(df["10_Tam_Boyut_Maske"], "10-Tam Boyut Maske"),
                            preview(df["11_Nihai_Sonuc"], "11-Nihai Sonuc"),
                            np.zeros_like(preview(df["1_Orijinal"], ""))))

            grid = np.vstack((r1, r2, r3))

            print(data["info"])
            cv2.imshow("Algoritma Ara Cikti Analizi", grid)
            cv2.waitKey(0)
            cv2.destroyAllWindows()