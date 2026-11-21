import os
import csv
import cv2
import numpy as np


# ===================== AYARLAR =====================

IMAGE_PATH = "slab_01.jpg"

SAVE_DIR = "out"
CSV_PATH = os.path.join(SAVE_DIR, "results.csv")

# Düz kabul eşiği
A_THR = 1.25
RMS_THR = 5.5

SHOW_WINDOW = True

# ====================================================


def decide_curvature(a2, rms, side, a_thr=A_THR, rms_thr=RMS_THR):
    if abs(a2) < a_thr and rms < rms_thr:
        return "duz"

    if side == "left":
        return "disbukey" if a2 > 0 else "icbukey"

    return "icbukey" if a2 > 0 else "disbukey"


def create_hot_slab_mask(image):
    """
    Canny ile arka plan seçmek yerine sıcak slabın kırmızı/pembe
    renk bilgisini kullanarak maske üretir.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    b, g, r = cv2.split(image)

    # HSV'de kırmızı, turuncu ve pembe sıcak tonları
    lower_red_orange = cv2.inRange(
        hsv,
        np.array([0, 35, 50]),
        np.array([35, 255, 255])
    )

    upper_pink_red = cv2.inRange(
        hsv,
        np.array([155, 35, 50]),
        np.array([179, 255, 255])
    )

    # RGB'de kırmızı bileşeni baskın sıcak alanlar
    red_dominant = (
        (r.astype(np.int16) > g.astype(np.int16) + 15)
        & (r.astype(np.int16) > b.astype(np.int16) + 5)
        & (v > 60)
    )

    red_dominant = np.where(red_dominant, 255, 0).astype(np.uint8)

    mask = cv2.bitwise_or(lower_red_orange, upper_pink_red)
    mask = cv2.bitwise_or(mask, red_dominant)

    height, width = mask.shape

    # Küçük kopuk sıcak bölgeleri birleştirir
    kernel_width = max(9, int(width * 0.015))
    kernel_height = max(5, int(height * 0.01))

    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT,
        (kernel_width, kernel_height)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=2
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        np.ones((3, 3), np.uint8),
        iterations=1
    )

    return mask


def select_slab_component(color_mask):
    """
    Sıcak renk maskesindeki adaylar arasından:
    - geniş,
    - yeterince büyük,
    - görüntü merkezine yakın
    olan bileşeni slab olarak seçer.
    """
    height, width = color_mask.shape

    count, labels, stats, _ = cv2.connectedComponentsWithStats(
        color_mask,
        connectivity=8
    )

    candidates = []

    for index in range(1, count):
        x, y, w, h, area = stats[index]

        if area < width * height * 0.002:
            continue

        if w < width * 0.15:
            continue

        if h < height * 0.03:
            continue

        aspect_ratio = w / max(h, 1)

        center_x = (x + w / 2) / width
        center_y = (y + h / 2) / height

        # Slab çoğunlukla görüntünün yatay merkezinde bulunur.
        horizontal_score = max(0.0, 1.0 - abs(center_x - 0.5) / 0.5)

        # Görüntünün tamamen üst/altındaki küçük sıcak nesneleri elemek için.
        vertical_score = max(0.0, 1.0 - abs(center_y - 0.52) / 0.55)

        # Geniş yatay yapı slab için daha olasıdır.
        shape_score = min(aspect_ratio, 8.0)

        score = area * shape_score * (
            0.3 + horizontal_score
        ) * (
            0.3 + vertical_score
        )

        candidates.append((score, index))

    if not candidates:
        raise RuntimeError(
            "Slab bulunamadı. HSV renk eşiklerini fotoğrafınıza göre ayarlayın."
        )

    selected_index = max(candidates)[1]

    slab_mask = np.where(
        labels == selected_index,
        255,
        0
    ).astype(np.uint8)

    # Maskedeki küçük delikleri doldur
    contours, _ = cv2.findContours(
        slab_mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    filled_mask = np.zeros_like(slab_mask)

    cv2.drawContours(
        filled_mask,
        contours,
        -1,
        255,
        thickness=cv2.FILLED
    )

    return filled_mask


def get_left_right_points(slab_mask):
    """
    Arka plan yerine yalnız seçilmiş slab maskesi üzerinde çalışır.

    Her yatay satırda:
    - en sol slab pikseli = sol kenar
    - en sağ slab pikseli = sağ kenar
    """
    ys, xs = np.where(slab_mask > 0)

    if len(xs) == 0:
        raise RuntimeError("Seçilen slab maskesi boş.")

    x_min = int(xs.min())
    x_max = int(xs.max())
    y_min = int(ys.min())
    y_max = int(ys.max())

    slab_height = y_max - y_min

    # Üst ve alt köşe bölgelerini dışarıda bırakır.
    sample_y_start = int(y_min + slab_height * 0.10)
    sample_y_end = int(y_max - slab_height * 0.10)

    y_samples = np.linspace(
        sample_y_start,
        sample_y_end,
        8,
        dtype=int
    )

    x_left = []
    x_right = []
    y_used = []

    for y in y_samples:
        row = np.where(slab_mask[y, :] > 0)[0]

        if row.size > 0:
            x_left.append(row.min())
            x_right.append(row.max())
            y_used.append(y)

    if len(y_used) < 3:
        raise RuntimeError("Polinom hesabı için yeterli slab kenar noktası yok.")

    return (
        np.array(x_left, dtype=np.float32),
        np.array(x_right, dtype=np.float32),
        np.array(y_used, dtype=np.float32),
        (x_min, y_min, x_max, y_max)
    )


def analyze_image(image):
    resized = cv2.resize(image, (960, 540))

    # 1. Sıcak bölgeleri çıkar
    color_mask = create_hot_slab_mask(resized)

    # 2. Arka planı değil, slab adayını seç
    slab_mask = select_slab_component(color_mask)

    # 3. Seçilen slab maskesinden sol-sağ kenar noktalarını al
    x_left, x_right, y_used, bbox = get_left_right_points(slab_mask)

    x_min, y_min, x_max, y_max = bbox

    # 4. Polinom hesabı
    y_normalized = (y_used - y_used.min()) / (
        y_used.max() - y_used.min() + 1e-9
    )

    # Sol kenar
    b_left, c_left = np.polyfit(y_normalized, x_left, 1)
    a2_left, b2_left, c2_left = np.polyfit(y_normalized, x_left, 2)

    rms_left = float(
        np.sqrt(
            np.mean(
                (x_left - (b_left * y_normalized + c_left)) ** 2
            )
        )
    )

    # Sağ kenar
    b_right, c_right = np.polyfit(y_normalized, x_right, 1)
    a2_right, b2_right, c2_right = np.polyfit(y_normalized, x_right, 2)

    rms_right = float(
        np.sqrt(
            np.mean(
                (x_right - (b_right * y_normalized + c_right)) ** 2
            )
        )
    )

    decision_left = decide_curvature(
        a2_left,
        rms_left,
        "left"
    )

    decision_right = decide_curvature(
        a2_right,
        rms_right,
        "right"
    )

    # =================== GÖRSEL ÇIKTI ===================

    overlay = resized.copy()

    # Yeşil kutu: Algoritmanın slab kabul ettiği alan
    cv2.rectangle(
        overlay,
        (x_min, y_min),
        (x_max, y_max),
        (0, 255, 0),
        2
    )

    cv2.putText(
        overlay,
        "Secilen slab alani",
        (x_min, max(25, y_min - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 255, 0),
        2
    )

    # Sarı noktalar: sol slab kenarı
    for y, x in zip(y_used.astype(int), x_left.astype(int)):
        cv2.circle(
            overlay,
            (x, y),
            5,
            (0, 255, 255),
            -1
        )

    # Kırmızı noktalar: sağ slab kenarı
    for y, x in zip(y_used.astype(int), x_right.astype(int)):
        cv2.circle(
            overlay,
            (x, y),
            5,
            (0, 0, 255),
            -1
        )

    # Polinom eğrilerini çiz
    y_draw = np.linspace(y_used.min(), y_used.max(), 100)

    y_draw_normalized = (y_draw - y_used.min()) / (
        y_used.max() - y_used.min() + 1e-9
    )

    x_draw_left = (
        a2_left * y_draw_normalized ** 2
        + b2_left * y_draw_normalized
        + c2_left
    )

    x_draw_right = (
        a2_right * y_draw_normalized ** 2
        + b2_right * y_draw_normalized
        + c2_right
    )

    left_curve = np.column_stack(
        [x_draw_left.astype(int), y_draw.astype(int)]
    ).reshape(-1, 1, 2)

    right_curve = np.column_stack(
        [x_draw_right.astype(int), y_draw.astype(int)]
    ).reshape(-1, 1, 2)

    # Camgöbeği: sol polinom
    cv2.polylines(
        overlay,
        [left_curve],
        False,
        (255, 255, 0),
        2
    )

    # Mor: sağ polinom
    cv2.polylines(
        overlay,
        [right_curve],
        False,
        (255, 0, 255),
        2
    )

    info_1 = (
        f"Sol: {decision_left} | "
        f"a2={a2_left:.3f}, RMS={rms_left:.1f}px"
    )

    info_2 = (
        f"Sag: {decision_right} | "
        f"a2={a2_right:.3f}, RMS={rms_right:.1f}px"
    )

    info_3 = "Sari: sol | Kirmizi: sag | Yesil: slab alani"

    for index, text in enumerate([info_1, info_2, info_3]):
        text_y = 30 + index * 30

        cv2.putText(
            overlay,
            text,
            (20, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (0, 0, 0),
            3,
            cv2.LINE_AA
        )

        cv2.putText(
            overlay,
            text,
            (20, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.62,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    result = {
        "left_label": decision_left,
        "left_a2": float(a2_left),
        "left_rms": float(rms_left),
        "right_label": decision_right,
        "right_a2": float(a2_right),
        "right_rms": float(rms_right),
        "bbox": [x_min, y_min, x_max, y_max]
    }

    return overlay, color_mask, slab_mask, result


def append_csv(path, row):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    header_needed = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=row.keys())

        if header_needed:
            writer.writeheader()

        writer.writerow(row)


def main():
    os.makedirs(SAVE_DIR, exist_ok=True)

    image = cv2.imread(IMAGE_PATH)

    if image is None:
        raise RuntimeError(
            f"Fotoğraf okunamadı: {IMAGE_PATH}\n"
            "IMAGE_PATH değerini doğru fotoğraf yoluyla değiştirin."
        )

    overlay, color_mask, slab_mask, result = analyze_image(image)

    overlay_path = os.path.join(SAVE_DIR, "overlay.jpg")
    raw_mask_path = os.path.join(SAVE_DIR, "sicak_renk_maskesi.jpg")
    slab_mask_path = os.path.join(SAVE_DIR, "secilen_slab_maskesi.jpg")

    cv2.imwrite(overlay_path, overlay)
    cv2.imwrite(raw_mask_path, color_mask)
    cv2.imwrite(slab_mask_path, slab_mask)

    append_csv(
        CSV_PATH,
        {
            "image_path": IMAGE_PATH,
            "left_label": result["left_label"],
            "left_a2": f'{result["left_a2"]:.6f}',
            "left_rms": f'{result["left_rms"]:.3f}',
            "right_label": result["right_label"],
            "right_a2": f'{result["right_a2"]:.6f}',
            "right_rms": f'{result["right_rms"]:.3f}',
            "bbox": result["bbox"],
            "overlay_path": overlay_path
        }
    )

    # Kontrol için üç görüntüyü yan yana göster
    color_mask_bgr = cv2.cvtColor(color_mask, cv2.COLOR_GRAY2BGR)
    slab_mask_bgr = cv2.cvtColor(slab_mask, cv2.COLOR_GRAY2BGR)

    debug_view = np.hstack((
        overlay,
        color_mask_bgr,
        slab_mask_bgr
    ))

    cv2.putText(
        debug_view,
        "SOL: Sonuc | ORTA: Sicak renk maskesi | SAG: Secilen slab",
        (20, debug_view.shape[0] - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (0, 255, 255),
        2
    )

    print(result)
    print("Pencereyi kapatmak icin herhangi bir tusa basin.")

    if SHOW_WINDOW:
        cv2.imshow("Slab Algilama Kontrolu", debug_view)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()