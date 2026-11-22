/*
  Kilit solenoid sürücüsü · Kontrol yazılımı (Arduino Nano / ATmega328P)

  D9 HIGH  -> Q1 (IRLZ44N) iletimde -> solenoid çeker
  D9 LOW   -> solenoid bırakır

  TETİK BUTONU (asıl kullanım):
    Buton 5V ile D2 arasında, D2'de harici 10 kΩ pull-down (+100 nF). Basılı = HIGH.
    Butona basınca BUTON SÜRESİ kadar (başlangıç 50 ms) tek darbe atar.
    Tetikleme sürerken tekrar basılırsa durdurur.
    Basılı tutmak tekrar tetiklemez; her basış tek tetikleme.

  İKİ AYRI SÜRE VAR:
    Buton süresi  (BSURE)  -> sadece fiziksel buton kullanır, tek darbe.
    Arayüz süresi (SURE)   -> sadece arayüzdeki TETİKLE kullanır,
                              TEKRAR ve ARALIK ile birlikte.
  Biri değişince diğeri etkilenmez. İkisi de kalıcı kaydedilir;
  elektrik kesilse de buton kendi süresiyle çalışmaya devam eder.

  Bilgisayar gerekmez. Buton süresini değiştirmek için USB ile bağlanıp
  arayüzden (solenoid_arayuz.html, Chrome / Edge) yeni süre girilir.

  Komutlar (her komut bir satır, sonunda Enter):
    BSURE <ms>       Buton tetikleme süresi, ms (tek darbe)
    SURE <ms>        Arayüzden tetikleme (açık kalma) süresi, ms
    TEKRAR <adet>    Bir tetiklemede kaç darbe atılacağı (1 = tek darbe)
    ARALIK <ms>      İki darbe arasındaki bekleme süresi, ms
    TETIKLE          Arayüz süresi/tekrar/aralık ile tetikle
    DURDUR           Solenoidi hemen bırak, devam eden tetiklemeyi iptal et
    DURUM            Ayarları ve durumu yaz
    KAYDET           Ayarları kalıcı belleğe yaz (ayarlar zaten otomatik kaydedilir)

  Cevaplar:
    OK ... / HATA ... / DURUM ... / ACIK <n> / KAPALI <n> / BITTI / IPTAL / HAZIR
    BUTON  (butonla tetiklendi; ardından ACIK 1 gelir)
*/

#include <EEPROM.h>

// ---------- Ayarlanabilir sınırlar ----------
const uint8_t  SOLENOID_PIN   = 9;
const uint8_t  BUTON_PIN      = 2;       // buton 5V - D2 arası, D2'de 10 kΩ pull-down
const uint16_t BUTON_SABIT_MS = 30;      // ark/titreşim süzme (debounce)
const uint32_t SURE_MIN_MS    = 10;      // en kısa açık kalma
const uint32_t SURE_MAX_MS    = 5000;    // en uzun açık kalma (solenoid ve Q1 ısınmasın)
const uint32_t ARALIK_MIN_MS  = 100;     // iki darbe arası en kısa bekleme
const uint32_t ARALIK_MAX_MS  = 60000;
const uint16_t TEKRAR_MAX     = 1000;

// ---------- Ayarlar ----------
struct Ayarlar {
  uint16_t imza;
  uint32_t sureMs;
  uint16_t tekrar;
  uint32_t aralikMs;
  uint32_t butonSureMs;
};
const uint16_t IMZA = 0x5D03;
// başlangıç: arayüz 50 ms tek darbe, buton 50 ms
Ayarlar ayar = { IMZA, 50, 1, 1000, 50 };

// ---------- Durum ----------
bool     calisiyor   = false;   // tetikleme dizisi devam ediyor mu
bool     acik        = false;   // solenoid şu an çekili mi
uint16_t darbeNo     = 0;       // kaçıncı darbe
uint32_t sonGecis    = 0;       // son aç/kapa anı (millis)
uint32_t aktifSure   = 50;      // çalışan dizinin darbe süresi
uint16_t aktifTekrar = 1;       // çalışan dizinin darbe sayısı

// Buton
bool     butonOkunan   = LOW;   // ham okuma
bool     butonKararli  = LOW;   // süzülmüş durum (LOW = basılı değil)
uint32_t butonDegisim  = 0;

char     satir[48];
uint8_t  satirUzunluk = 0;

void solenoidKapat() {
  digitalWrite(SOLENOID_PIN, LOW);
  acik = false;
}

void solenoidAc() {
  digitalWrite(SOLENOID_PIN, HIGH);
  acik = true;
}

void durumYaz() {
  Serial.print(F("DURUM sure="));   Serial.print(ayar.sureMs);
  Serial.print(F(" tekrar="));      Serial.print(ayar.tekrar);
  Serial.print(F(" aralik="));      Serial.print(ayar.aralikMs);
  Serial.print(F(" bsure="));       Serial.print(ayar.butonSureMs);
  Serial.print(F(" calisiyor="));   Serial.print(calisiyor ? 1 : 0);
  Serial.print(F(" acik="));        Serial.print(acik ? 1 : 0);
  Serial.print(F(" min="));         Serial.print(SURE_MIN_MS);
  Serial.print(F(" max="));         Serial.print(SURE_MAX_MS);
  Serial.print(F(" aralikmin="));   Serial.println(ARALIK_MIN_MS);
}

void ayarYukle() {
  Ayarlar a;
  EEPROM.get(0, a);
  if (a.imza == IMZA &&
      a.sureMs >= SURE_MIN_MS && a.sureMs <= SURE_MAX_MS &&
      a.tekrar >= 1 && a.tekrar <= TEKRAR_MAX &&
      a.aralikMs >= ARALIK_MIN_MS && a.aralikMs <= ARALIK_MAX_MS &&
      a.butonSureMs >= SURE_MIN_MS && a.butonSureMs <= SURE_MAX_MS) {
    ayar = a;
  }
}

// EEPROM.put sadece değişen baytları yazar; aynı değer tekrar gelirse bellek yıpranmaz
void ayarKaydet() {
  ayar.imza = IMZA;
  EEPROM.put(0, ayar);
}

void tetikle(uint32_t sure, uint16_t tekrar) {
  aktifSure = sure; aktifTekrar = tekrar;
  calisiyor = true; darbeNo = 1; sonGecis = millis();
  solenoidAc();
  Serial.print(F("ACIK ")); Serial.println(darbeNo);
}

void durdur() {
  bool vardi = calisiyor || acik;
  solenoidKapat(); calisiyor = false;
  Serial.println(vardi ? F("IPTAL") : F("OK durdu"));
}

// Buton: basılma anında (kenar) bir kez çalışır, basılı tutmak tekrar tetiklemez
void butonKontrol() {
  bool okunan = digitalRead(BUTON_PIN);
  uint32_t simdi = millis();
  if (okunan != butonOkunan) { butonOkunan = okunan; butonDegisim = simdi; }
  if (simdi - butonDegisim >= BUTON_SABIT_MS && butonKararli != butonOkunan) {
    butonKararli = butonOkunan;
    if (butonKararli == HIGH) {           // yeni basıldı
      if (calisiyor) { durdur(); }
      else { Serial.println(F("BUTON")); tetikle(ayar.butonSureMs, 1); }
    }
  }
}

bool sayiOku(const char *s, uint32_t &deger) {
  while (*s == ' ') s++;
  if (*s < '0' || *s > '9') return false;
  uint32_t v = 0;
  while (*s >= '0' && *s <= '9') {
    v = v * 10 + (*s - '0');
    if (v > 10000000UL) return false;
    s++;
  }
  while (*s == ' ') s++;
  if (*s != '\0') return false;
  deger = v;
  return true;
}

bool basliyorMu(const char *s, const char *onek) {
  while (*onek) { if (*s++ != *onek++) return false; }
  return *s == '\0' || *s == ' ';
}

void komutIsle(char *k) {
  for (char *p = k; *p; p++) if (*p >= 'a' && *p <= 'z') *p -= 32;   // büyük harfe çevir
  uint32_t v;

  if (basliyorMu(k, "BSURE")) {
    if (!sayiOku(k + 5, v)) { Serial.println(F("HATA bsure sayi olmali")); return; }
    if (v < SURE_MIN_MS || v > SURE_MAX_MS) {
      Serial.print(F("HATA bsure ")); Serial.print(SURE_MIN_MS); Serial.print(F("-"));
      Serial.print(SURE_MAX_MS); Serial.println(F(" ms arasinda olmali")); return;
    }
    ayar.butonSureMs = v; ayarKaydet(); Serial.print(F("OK bsure=")); Serial.println(v);
  } else if (basliyorMu(k, "SURE")) {
    if (!sayiOku(k + 4, v)) { Serial.println(F("HATA sure sayi olmali")); return; }
    if (v < SURE_MIN_MS || v > SURE_MAX_MS) {
      Serial.print(F("HATA sure ")); Serial.print(SURE_MIN_MS); Serial.print(F("-"));
      Serial.print(SURE_MAX_MS); Serial.println(F(" ms arasinda olmali")); return;
    }
    ayar.sureMs = v; ayarKaydet(); Serial.print(F("OK sure=")); Serial.println(v);
  } else if (basliyorMu(k, "TEKRAR")) {
    if (!sayiOku(k + 6, v) || v < 1 || v > TEKRAR_MAX) {
      Serial.print(F("HATA tekrar 1-")); Serial.print(TEKRAR_MAX); Serial.println(F(" arasinda olmali")); return;
    }
    ayar.tekrar = (uint16_t)v; ayarKaydet(); Serial.print(F("OK tekrar=")); Serial.println(v);
  } else if (basliyorMu(k, "ARALIK")) {
    if (!sayiOku(k + 6, v) || v < ARALIK_MIN_MS || v > ARALIK_MAX_MS) {
      Serial.print(F("HATA aralik ")); Serial.print(ARALIK_MIN_MS); Serial.print(F("-"));
      Serial.print(ARALIK_MAX_MS); Serial.println(F(" ms arasinda olmali")); return;
    }
    ayar.aralikMs = v; ayarKaydet(); Serial.print(F("OK aralik=")); Serial.println(v);
  } else if (basliyorMu(k, "TETIKLE")) {
    if (calisiyor) { Serial.println(F("HATA zaten calisiyor")); return; }
    tetikle(ayar.sureMs, ayar.tekrar);
  } else if (basliyorMu(k, "DURDUR")) {
    durdur();
  } else if (basliyorMu(k, "DURUM")) {
    durumYaz();
  } else if (basliyorMu(k, "KAYDET")) {
    ayarKaydet(); Serial.println(F("OK kaydedildi"));
  } else if (k[0] != '\0') {
    Serial.println(F("HATA bilinmeyen komut"));
  }
}

void setup() {
  pinMode(SOLENOID_PIN, OUTPUT);
  solenoidKapat();                 // açılışta solenoid kesinlikle kapalı
  pinMode(BUTON_PIN, INPUT);          // harici pull-down var
  butonOkunan = butonKararli = digitalRead(BUTON_PIN);  // açılışta basılıysa tetikleme
  Serial.begin(115200);
  ayarYukle();
  Serial.println(F("HAZIR KILIT-SOL"));
  durumYaz();
}

void loop() {
  // 1) Seri porttan gelen komutları oku
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      satir[satirUzunluk] = '\0';
      komutIsle(satir);
      satirUzunluk = 0;
    } else if (satirUzunluk < sizeof(satir) - 1) {
      satir[satirUzunluk++] = c;
    }
  }

  // 2) Buton
  butonKontrol();

  // 3) Zamanlama (bekletmeden, millis ile)
  if (calisiyor) {
    uint32_t simdi = millis();
    if (acik && simdi - sonGecis >= aktifSure) {
      solenoidKapat(); sonGecis = simdi;
      Serial.print(F("KAPALI ")); Serial.println(darbeNo);
      if (darbeNo >= aktifTekrar) { calisiyor = false; Serial.println(F("BITTI")); }
    } else if (!acik && simdi - sonGecis >= ayar.aralikMs) {
      darbeNo++; solenoidAc(); sonGecis = simdi;
      Serial.print(F("ACIK ")); Serial.println(darbeNo);
    }
  }

  // 4) Güvenlik: hiçbir durumda SURE_MAX_MS'den uzun açık kalmasın
  if (acik && millis() - sonGecis > SURE_MAX_MS + 50) {
    solenoidKapat(); calisiyor = false; Serial.println(F("IPTAL zaman asimi"));
  }
}
