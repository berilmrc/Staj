"""
ADIM 1 - BAGLANTI TESTI
========================
Bu script SADECE Kepware'e baglanip 3 tag'i okuyup ekrana basar.
Amac: node ID'lerin ve endpoint'in dogru oldugunu dogrulamak.
Gorsel isleme / ROI ile hicbir ilgisi yok, once bunu calistir.

Kurulum:
    pip install opcua
"""

from opcua import Client

# ============================================================
# OPC UA sunucu ve tag ayarlari (Kepware simulasyon cihazi)
# ============================================================

# Kepware'in calistigi makinenin IP'si + OPC UA portu (varsayilan 49320)
OPC_ENDPOINT = "opc.tcp://127.0.0.1:49320"

# Kepware Quick Client / UaExpert ile bulacagin GERCEK node ID'ler.
# Asagidakiler ORNEKTIR, kendi projenin Channel/Device/Tag isimleriyle degistir.
NODE_ID_GENISLIK = "ns=2;s=Sim.SimDev.SonucSol"
NODE_ID_BOY = "ns=2;s=Sim.SimDev.SonucSol"
NODE_ID_KALINLIK = "ns=2;s=Sim.SimDev.SlabWidth"


def read_slab_measurements(client):
    """Kepware'den anlik en/boy/kalinlik degerlerini okur."""
    genislik = client.get_node(NODE_ID_GENISLIK).get_value()
    boy = client.get_node(NODE_ID_BOY).get_value()
    kalinlik = client.get_node(NODE_ID_KALINLIK).get_value()
    return genislik, boy, kalinlik


if __name__ == "__main__":
    client = Client(OPC_ENDPOINT)
    try:
        client.connect()
        print(f"[OK] Kepware'e baglanildi: {OPC_ENDPOINT}")

        genislik, boy, kalinlik = read_slab_measurements(client)
        print(f"Genislik : {genislik}")
        print(f"Boy      : {boy}")
        print(f"Kalinlik : {kalinlik}")

    except Exception as e:
        print(f"[HATA] Baglanti veya okuma basarisiz: {e}")
        print("Kontrol et: IP/port dogru mu, Kepware UA sunucusu acik mi, "
              "node ID'ler Kepware Quick Client'taki ile birebir ayni mi?")

    finally:
        try:
            client.disconnect()
        except Exception:
            pass