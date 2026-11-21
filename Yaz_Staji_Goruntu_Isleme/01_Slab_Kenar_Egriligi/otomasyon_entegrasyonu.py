import time
import os
from datetime import datetime
import cv2
from opcua import Client, ua
from openpyxl import Workbook, load_workbook

from slab_curvature_pipeline import process_slab

# ============================================================
# KEPWARE VE AYARLAR
# ============================================================
OPC_ENDPOINT = "opc.tcp://127.0.0.1:49320"
NODE_ID_GENISLIK = "ns=2;s=sim.SimDev.SlabWidth"
NODE_ID_SONUC_SOL = "ns=2;s=sim.SimDev.SonucSol"
NODE_ID_SONUC_SAG = "ns=2;s=sim.SimDev.SonucSag"
NODE_ID_TRIGGER = "ns=2;s=sim.SimDev.VideoSecond"

POLL_INTERVAL_SEC = 0.5

TEST_IMAGES = {
    "TIP_1": "slab_1.jpeg",
    "TIP_2": "slab3.jpeg",
}


def capture_frame(slab_type):
    path = TEST_IMAGES.get(slab_type)
    if path is None:
        print(f"[UYARI] '{slab_type}' icin tanimli test gorseli yok.")
        return None
    return cv2.imread(path)


def classify_slab_type(genislik):
    if 850 <= genislik <= 935:
        return "TIP_1"
    elif 936 <= genislik <= 1320:
        return "TIP_2"
    else:
        return "Tip Bilinmiyor"


def read_slab_data(client):
    genislik = client.get_node(NODE_ID_GENISLIK).get_value()
    trigger = client.get_node(NODE_ID_TRIGGER).get_value()
    return genislik, trigger


CURVATURE_CODE = {
    "duz": 0,
    "icbukey": 1,
    "disbukey": 2,
}


def _write_int16(node, value):
    dv = ua.DataValue(ua.Variant(value, ua.VariantType.Int16))
    dv.SourceTimestamp = None
    dv.ServerTimestamp = None
    node.set_attribute(ua.AttributeIds.Value, dv)


def write_result_to_kepware(client, decL, decR):
    sol_code = CURVATURE_CODE.get(decL, -1)
    sag_code = CURVATURE_CODE.get(decR, -1)

    node_sol = client.get_node(NODE_ID_SONUC_SOL)
    node_sag = client.get_node(NODE_ID_SONUC_SAG)

    _write_int16(node_sol, sol_code)
    _write_int16(node_sag, sag_code)

    print(f"  -> Kepware'e yazildi: SonucSol={sol_code} ({decL}), SonucSag={sag_code} ({decR})")
    return sol_code, sag_code


EXCEL_LOG_PATH = "slab_sonuclari.xlsx"
EXCEL_HEADERS = [
    "Tarih/Saat", "Genislik", "Slab Tipi",
    "Sol Sonuc", "Sol a2", "Sol RMS",
    "Sag Sonuc", "Sag a2", "Sag RMS",
    "Kod Sol", "Kod Sag",
]


def log_result_to_excel(genislik, slab_type, result, sol_code, sag_code):
    try:
        if os.path.exists(EXCEL_LOG_PATH):
            wb = load_workbook(EXCEL_LOG_PATH)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Sonuclar"
            ws.append(EXCEL_HEADERS)

        ws.append([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            genislik,
            slab_type,
            result["left"], result["a2_left"], result["rms_left"],
            result["right"], result["a2_right"], result["rms_right"],
            sol_code, sag_code,
        ])
        wb.save(EXCEL_LOG_PATH)
        print(f"  -> Excel'e kaydedildi: {EXCEL_LOG_PATH}")
    except Exception as e:
        print(f"  [UYARI] Excel kayit hatasi: {e}")


def main():
    client = Client(OPC_ENDPOINT)
    client.connect()
    print(f"[OK] Kepware'e baglanildi: {OPC_ENDPOINT}")

    _, last_trigger = read_slab_data(client)
    print(f"[BILGI] Sistem dinlemede. Mevcut VideoSecond: {last_trigger}")

    # Görselleştirme pencerelerini baştan oluşturuyoruz
    cv2.namedWindow("1. Ham Goruntu", cv2.WINDOW_NORMAL)
    cv2.namedWindow("2. Kavis Analiz Sonucu", cv2.WINDOW_NORMAL)

    try:
        while True:
            genislik, current_trigger = read_slab_data(client)

            if current_trigger != last_trigger and current_trigger not in (None, 0):
                last_trigger = current_trigger
                print(f"\n--- YENİ TETİKLEME ALINDI (VideoSecond: {current_trigger}) ---")

                if genislik in (None, 0):
                    print("  [UYARI] Genislik degeri gecersiz.")
                    continue

                slab_type = classify_slab_type(genislik)
                print(f"  Okunan Genislik: {genislik} mm -> Tip: {slab_type}")

                if slab_type == "Tip Bilinmiyor":
                    print("  [UYARI] Genislik aralik disinda, analiz yapilmiyor.")
                    continue

                # Adım 1: Ham Görüntüyü Al ve Göster
                img = capture_frame(slab_type)
                if img is None:
                    print("[HATA] Goruntu alinamadi.")
                    continue

                cv2.imshow("1. Ham Goruntu", img)
                cv2.waitKey(500)  # Görüntünün ekrana gelmesi için kısa bir bekleme

                # Adım 2: Kavis Analizi Pipeline'ını Çalıştır
                success, overlay, result = process_slab(img, slab_type)
                print(f"  Sonuc: {result['info']} (ROI: {result.get('roi_key_used')})")

                if success:
                    # Adım 3: İşlenmiş Sonuç Görselini Ekrana Bas
                    cv2.imshow("2. Kavis Analiz Sonucu", overlay)
                    cv2.waitKey(1000)  # Sonucun incelenmesi için 1 saniye beklet

                    cv2.imwrite("son_sonuc.png", overlay)
                    sol_code, sag_code = write_result_to_kepware(client, result["left"], result["right"])
                    log_result_to_excel(genislik, slab_type, result, sol_code, sag_code)
                else:
                    print("  [UYARI] Analiz basarisiz.")

            # OpenCV pencerelerinin donmaması için her döngüde kısa bir tuş kontrolü
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(POLL_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("\nDurduruldu.")
    finally:
        client.disconnect()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()