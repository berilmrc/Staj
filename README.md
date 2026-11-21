<div align="center">

<h1>🎓 Staj Çalışmaları</h1>

<p><b>Elektronik temellerinden STM32 ile haberleşmeye, hafta hafta staj sürecim ve staj projelerim</b></p>

<img alt="Süreç" src="https://img.shields.io/badge/S%C3%BCre%C3%A7-Haz%C4%B1rl%C4%B1k%20%2B%204%20hafta-6f42c1?style=for-the-badge"> <img alt="Platform" src="https://img.shields.io/badge/Platform-STM32-0969da?style=for-the-badge">

</div>

Bu klasör, staj programım kapsamında gerçekleştirdiğim görevleri, projeleri ve teknik dokümantasyonları içermektedir.
Toplam süreç; çalışma ortamına ve kullanılacak teknolojilere aşinalık kazanmak amacıyla tamamlanan bir hazırlık haftası ve onu takip eden 4 haftalık ana staj döneminden oluşmaktadır.

---

## 🗓️ Haftalık Zaman Çizelgesi

<table>
<tr>
<td align="center" width="22%"><h1>🔋</h1><b>Hazırlık Haftası</b><br><sub>2 – 6 Eylül</sub></td>
<td width="78%"><b>Elektronik temelleri</b><br>Ohm kanunu, direnç, kapasitör ve bobin; seri ve paralel bağlantı. Falstad'da gerilim bölücü (voltage divider) ile LED uygulaması.<br><br>📄 <a href="Hazirlik_haftalari/00_On_Hazirlik/On_Hazirlik_Rapor.docx">Rapor</a> &nbsp;·&nbsp; 📁 <a href="Hazirlik_haftalari/00_On_Hazirlik">Klasör</a></td>
</tr>
<tr>
<td align="center" width="22%"><h1>📐</h1><b>1. Hafta</b><br><sub>7 – 13 Eylül</sub></td>
<td width="78%"><b>Şematik okuma · Dijital mantık · C'ye giriş</b><br>LED ve transistörlü sürme devrelerini yorumlama, AND / OR / NOT / XOR lojik kapıları, Falstad'da lojik devre uygulaması ve GitHub hesabını kullanmaya başlama.<br><br>📄 <a href="Hazirlik_haftalari/01_Hafta_1/Hafta_1_Rapor.docx">Rapor</a> &nbsp;·&nbsp; 📁 <a href="Hazirlik_haftalari/01_Hafta_1">Klasör</a></td>
</tr>
<tr>
<td align="center" width="22%"><h1>💻</h1><b>2. Hafta</b><br><sub>14 – 20 Eylül</sub></td>
<td width="78%"><b>C derinleşme · Mikrodenetleyici · Wokwi</b><br>Pointer, struct ve bitwise işlemler; sahte register üzerinde bit set / clear / toggle. Wokwi'de STM32 Blue Pill ile blink ve buton + LED projesi.<br><br>📄 <a href="Hazirlik_haftalari/02_Hafta_2/Hafta_2_Rapor.docx">Rapor</a> &nbsp;·&nbsp; 🧪 <a href="Hazirlik_haftalari/02_Hafta_2/simulasyon">Simülasyon</a> &nbsp;·&nbsp; 📁 <a href="Hazirlik_haftalari/02_Hafta_2">Klasör</a></td>
</tr>
<tr>
<td align="center" width="22%"><h1>📡</h1><b>3. Hafta</b><br><sub>21 – 24 Eylül</sub></td>
<td width="78%"><b>UART haberleşme · ADC ile analog okuma</b><br>Seri ve paralel haberleşme, USART / UART ve baud rate. Buton sayacını UART ile gönderen proje ve NUCLEO-C031C6 üzerinde potansiyometreyi ADC ile okuma.<br><br>📄 <a href="Staj_haftalari/03_Hafta_3/Hafta_3_Rapor.docx">Rapor</a> &nbsp;·&nbsp; 🧪 <a href="Staj_haftalari/03_Hafta_3/simulasyon">Simülasyon</a> &nbsp;·&nbsp; 📁 <a href="Staj_haftalari/03_Hafta_3">Klasör</a></td>
</tr>
<tr>
<td align="center" width="22%"><h1>🧭</h1><b>4. Hafta</b><br><sub>28 Eylül haftası</sub></td>
<td width="78%"><b>Kavramsal tasarım</b><br>Mühendislik tasarım fazları: gereksinim belirleme, kavramsal tasarım, blok diyagramı, ön ve detaylı tasarım, prototipleme, doğrulama. V modeli ile ürün geliştirme.<br><br>📄 <a href="Staj_haftalari/04_Hafta_4/Hafta_4_Kavramsal_Tasarim.docx">Kavramsal Tasarım</a> &nbsp;·&nbsp; 📁 <a href="Staj_haftalari/04_Hafta_4">Klasör</a></td>
</tr>
</table>

---

## 🛠️ Staj Projeleri

| Proje | Açıklama | Durum |
|---|---|---|
| [Yaz Stajı · Görüntü İşleme](Yaz_Staji_Goruntu_Isleme/) | Slab kenar eğriliği tespiti ve mikroyapı faz analizi (OpenCV) | Tamamlandı |
| [Basınç Test Düzeneği](Basinc_Test_Duzenegi/) | Basınç üretip referans sensörle ölçen test düzeneğinin ilk prototipi: sensör entegrasyonu (RS485 / Modbus RTU), PWM pompa kontrolü, otomatik test ve sonuç analizi | Devam ediyor |

İlgili repolar: 🔑 [Keywords](https://github.com/berilmrc/Keywords) (staj sürecinde karşılaştığım teknik terimler) · 🗂️ [Projeler](https://github.com/berilmrc/Projeler) (tüm projelerim)

---

## 📂 Klasör Yapısı

Her haftanın kendi alt klasörü içerisinde, o döneme ait kaynak kodlar, projeler ve oluşturulan raporlar yer almaktadır. İlgili haftanın detaylarını incelemek için dizinlere göz atabilirsiniz.

```
📁 Hazirlik_haftalari
 ├── 00_On_Hazirlik          Hazırlık haftası
 ├── 01_Hafta_1               1. hafta
 └── 02_Hafta_2               2. hafta + Wokwi simülasyonları
📁 Staj_haftalari
 ├── 03_Hafta_3               3. hafta + Wokwi simülasyonları
 └── 04_Hafta_4               4. hafta
📁 Basinc_Test_Duzenegi       Staj projesi: basınç test düzeneği
📁 Yaz_Staji_Goruntu_Isleme   Yaz stajı: görüntü işleme projeleri
```

---

<div align="center"><sub>⬅️ <a href="https://github.com/berilmrc">Profile dön</a></sub></div>
