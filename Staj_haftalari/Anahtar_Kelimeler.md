# Anahtar Kelimeler

Obsidian kasası (`BerilMercanVault`) içindeki proje ve günlük notlarından derlenmiştir: kavram sözlükleri, etiketler (tags) ve not başlıkları.

## 1. Statik Port Projesi – Kavramlar

- Basınç
- Mutlak basınç (absolute)
- Gösterge basıncı (gauge)
- Vakum
- kPa / bar / mbar dönüşümleri
- Kapalı çevrim kontrol
- Setpoint (hedef değer)
- Histerezis
- Piezorezistif sensör
- Tam skala (FS) ve %FS
- Doğruluk (accuracy)
- Çözünürlük (resolution)
- Toplam hata bandı (TEB)
- RS485
- Half-duplex / full-duplex
- Diferansiyel sinyal
- UART / baud rate
- ADC (analog-dijital çevirici)
- H-köprüsü
- PWM / duty cycle
- Flyback diyot
- MOSFET / R_DS(on)
- Lojik seviye MOSFET
- Düşük / yüksek taraf anahtarlama
- Pull-down direnci
- Kalkış akımı (inrush)
- Brown-out (gerilim çökmesi reseti)
- Yıldız topraklama
- Dekuplaj / bulk kondansatör
- Statik vs dinamik basınç
- Çek valf
- Seri / paralel pompa bağlantısı
- Basınç oranı (sıkıştırma oranı)
- Aşım (overshoot)
- Regülatör (lineer)
- Sigorta
- Eşik gerilimi V_GS(th)
- Gate direnci / gate kapasitesi
- Schottky diyot
- TO-220 kılıf
- Delikli plaket / PCB
- Solenoid valf
- NC / NO (normalde kapalı / açık)
- Direkt etkili vs pilot kumandalı valf
- Orifis
- Interlock (kilitleme)
- Röle (COM / NO / NC kontak)
- Aktif-LOW / aktif-HIGH giriş
- Jumper (ENA/ENB, 5V)
- Nihai vakum (ultimate vacuum)
- Debi (akış hızı)

## 2. STM32 Öğrenme – Kavramlar

- ADC (Analog-to-Digital Converter)
- ARR (Auto-Reload Register)
- Bare Metal
- Bit
- Blink
- Breakpoint
- CCR (Capture/Compare Register)
- Clock
- Context Switch
- CubeMX
- DMA (Direct Memory Access)
- Debug
- Duty Cycle
- EXTI (External Interrupt)
- Flash
- FreeRTOS
- FSM (Finite State Machine)
- GPIO (General Purpose Input/Output)
- GND
- HAL (Hardware Abstraction Layer)
- Hertz (Hz)
- IDE (Integrated Development Environment)
- Interrupt (Kesme)
- ISR (Interrupt Service Routine)
- IWDG (Independent Watchdog)
- Kesme
- Kristal (Crystal Oscillator)
- LD (LED)
- LL (Low Level Driver)
- MCU (Microcontroller Unit)
- MODER (Mode Register)
- Mutex (Mutual Exclusion)
- NVIC (Nested Vectored Interrupt Controller)
- ODR (Output Data Register)
- OpenOCD
- PWM (Pulse Width Modulation)
- Prescaler
- RAM (Random Access Memory)
- RCC (Reset and Clock Control)
- Register
- RTC (Real Time Clock)
- Semaphore (Semafor)
- SPI (Serial Peripheral Interface)
- SWD (Serial Wire Debug)
- SysTick
- Task
- TIM (Timer)
- UART (Universal Asynchronous Receiver Transmitter)
- VDD / VSS
- Watchdog
- While(1)
- XTAL / Crystal

## 3. Etiketler (Tags)

`#ActiveCellBalancing`, `#Adım-1`, `#Adım-2`, `#aktüatör`, `#arduino`, `#ARM`, `#asama-1`, `#asama-2`, `#asama-3`, `#Asenkron`, `#baglanti-semasi`, `#BAP`, `#basinc-kontrol`, `#basınç-sensoru`, `#bağlantı`, `#Başlangıç`, `#Bellek`, `#BOM`, `#Button`, `#C-Temelleri`, `#CellBalancing`, `#Checklist`, `#CubeMX`, `#datasheet`, `#Debounce`, `#Debug`, `#Detaylı`, `#devre`, `#Dokümantasyon`, `#elektrik`, `#Embedded`, `#EXTI`, `#FPGA`, `#gereksinim`, `#GPIO`, `#Günlük`, `#güç`, `#haberleşme`, `#Hazırlık`, `#IDE`, `#Interrupt`, `#ISR`, `#kablolama`, `#karar`, `#Kavramlar`, `#keller`, `#keller-33x`, `#Kesme`, `#Kod-Değişiklikleri`, `#Kod-Yapısı`, `#Kontrol-Sistemi`, `#Kurulum`, `#Macro`, `#Main-Function`, `#main.c`, `#malzeme-listesi`, `#MATLAB`, `#Mikrodenetleyici`, `#mimari`, `#modbus`, `#montaj`, `#Nereye-Yazacaksın`, `#ozet`, `#Pin-Mapping`, `#Pointer`, `#pompa`, `#Pratik`, `#Programcı`, `#Progression`, `#Projeler`, `#protokol`, `#Prototypes`, `#PWM`, `#Referans`, `#Register`, `#rs485`, `#sensor-kati`, `#sensör`, `#Setup`, `#Simulink`, `#Sistem-Tasarımı`, `#SoC`, `#soru-hazirlik`, `#Sorun-Çözme`, `#State`, `#StatikPort`, `#STM32`, `#STM32-Özel`, `#sunum`, `#Sözlük`, `#sürücü`, `#Tam-Kod`, `#Temel`, `#Terimler`, `#test-sistemi`, `#Toggle`, `#turkce`, `#User-Code`, `#valf`, `#Volatile`, `#yazilim`, `#Öğrenme`, `#Öğrenme-Yolu`

## 4. Not Başlıkları

### Statik Port

- Kavram Sözlüğü
- Neden-Sonuç Günlüğü
- Project-Overview
- 01 Problem Tanımı ve Gereksinimler
- 02 Temel Kavramlar
- 03 Sistem Mimarisi
- Blok Diyagram
- İki Pompa - Seri mi Paralel mi
- 04 Donanım
- Arduino Mega 2560 Datasheet İnceleme
- IRLZ44N Sürücü Devresi
- Keller PAA-33X Datasheet İnceleme
- L298N Datasheet İnceleme
- MAX485 Datasheet İnceleme
- Malzeme Listesi (BOM)
- Malzeme Listesi - Detayli (Klemens-Rakor-Adaptör)
- Pompa Sürücü Seçimi
- Sistem Düzeneği ve Güç Dağıtımı
- Solenoid Valf
- Sürücü Bağlantıları (L298N + Röle)
- Vakum Pompası 12V 80kPa Datasheet İnceleme
- 05 Sensör Okuma ve Kalibrasyon
- 06 Kontrol Algoritması
- 07 Yazılım
- 08 Test ve Doğrulama
- 09 Raporlama
- Sunum Hazırlık Rehberi
- 99 Kaynaklar
- 00-Test_Sistemi_Ana_Sayfa
- 01-Asama1_Tanksiz_Tek_Valf
- 02-Asama2_Tankli_Tek_Valf
- 03-Asama3_Otomatik_Sistem
- 04-Malzeme_Listesi
- 05-Elektrik_Baglanti_Semasi
- 06-Yazilim_Gereksinimleri
- 06-Yazilim_Gereksinimleri_Ozet
- 07-Montaj_Plani
- 08-Montaj_Yerlesim_Plani
- 09-Kablolama_Plani
- 10-Yazilim_Mimarisi
- 11-Katman1_Sensor_Plani
- KELLER_X-Line_Communication_Protocol
- KELLER_X-Line_Iletisim_Protokolu
- Keller_33X_Datasheet_Calisma_Notu
- Keller_33X_Datasheet_Turkce
- Keller_Protokol_Arduino_Rehberi_TR
- Keller_Soru_Hazirlik
- Pompa_Motorobit_80kPa
- CCS30_Kullanim_Rehberi
- Proje_Anlatimi
- Yeni Microsoft Word Belgesi - duzeltilmis

### STM32 Öğrenme

- 16 Adımlı Progression
- Adım 2 Öncesi Hazırlık Listesi
- STM32 Ders Günlüğü
- STM32 Kavram Sözlüğü
- STM32 Proje Dashboard
- Bellek Haritası ve Register
- Datasheet'ten Pin Haritası Okuma
- Ders 4 - Kesme (Interrupt) ve EXTI
- Geliştirme Ortamı Kurulumu
- STM32 Nedir
- Volatile Pointer Macro Detaylı
- Adım 2 - Button Debounce Çözümü
- Adım 2 Debug - LED Değişmiyor
- Kod Değişiklikleri - Başlangıç Rehberi
- Prototypes User Code Main Detaylı
- main.c Kod Yapısı
- Adım 2 - Button EXTI Tam Kod
- Statik Port STM32 Dönüştürme

### SoC Tasarım

- SoC Tasarım Dashboard
- SIMULASYON_DASHBOARD
- SIMULINK_KURULUM
- ILERLEME
