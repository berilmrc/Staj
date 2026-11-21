import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import tkinter.messagebox as messagebox


class RenkAyristiriciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renk Bazlı Faz Ayrıştırma")
        self.root.geometry("1150x680")

        self.image = None
        self.hsv = None

        # Ara aşamaları tutacağımız değişkenler (Sunum ve kontrol için)
        self.son_mask = None
        self.mask_ham = None
        self.mask_open = None
        self.mask_close = None

        # Sabit klasör yolunu tanımlıyoruz
        self.klasor_yolu = "goruntuler"
        self.resim_listesi = []

        self.build_ui()
        self.fotograflari_hazirla()

    # ==========================================
    # ARAYÜZ KURULUMU
    # ==========================================
    def build_ui(self):
        left = tk.Frame(self.root, width=260, padx=12, pady=12)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(left, text="🔄 Rastgele Fotoğraf Getir", command=self.rastgele_getir, bg="#d4edda",
                  font=("Segoe UI", 10, "bold")).pack(fill=tk.X, pady=10)

        self.h_var = tk.IntVar(value=20)
        self.tol_var = tk.IntVar(value=15)
        self.smin_var = tk.IntVar(value=0)
        self.vmin_var = tk.IntVar(value=0)
        self.temiz_var = tk.IntVar(value=2)

        self.slider("H (renk merkezi)", self.h_var, 0, 179, left)
        self.slider("Tolerans (H)", self.tol_var, 0, 90, left)
        self.slider("S min", self.smin_var, 0, 255, left)
        self.slider("V min", self.vmin_var, 0, 255, left)
        self.slider("Temizlik (gürültü)", self.temiz_var, 0, 10, left)

        self.oran_label = tk.Label(left, text="Oran: -- %", font=("Segoe UI", 14, "bold"), fg="#1a7a1a")
        self.oran_label.pack(pady=15)

        tk.Button(left, text="💾 Aşamaları Kaydet & Raporla", command=self.kaydet, bg="#e0e0e0").pack(fill=tk.X, pady=5)

        tk.Label(
            left,
            text="İpucu: Soldaki fotoğrafta\nhedef renge tıkla, H değeri\notomatik ayarlanır.",
            justify=tk.LEFT, fg="gray"
        ).pack(pady=15, anchor=tk.W)

        right = tk.Frame(self.root)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        tk.Label(right, text="Orijinal (renk seçmek için tıkla)").grid(row=0, column=0, pady=(5, 0))
        tk.Label(right, text="Sonuç (Seçilen Renk)").grid(row=0, column=1, pady=(5, 0))

        self.canvas_orijinal = tk.Label(right, bg="#222")
        self.canvas_orijinal.grid(row=1, column=0, padx=5, pady=5)
        self.canvas_orijinal.bind("<Button-1>", self.tikla)

        self.canvas_sonuc = tk.Label(right, bg="#222")
        self.canvas_sonuc.grid(row=1, column=1, padx=5, pady=5)

    def slider(self, isim, var, mn, mx, parent):
        tk.Label(parent, text=isim).pack(anchor=tk.W)
        s = tk.Scale(parent, from_=mn, to=mx, orient=tk.HORIZONTAL, variable=var,
                     command=lambda e: self.guncelle())
        s.pack(fill=tk.X, pady=(0, 8))

    # ==========================================
    # DOSYA İŞLEMLERİ
    # ==========================================
    def fotograflari_hazirla(self):
        if not os.path.exists(self.klasor_yolu):
            messagebox.showerror("Hata", f"Klasör bulunamadı. Yolu kontrol edin:\n{self.klasor_yolu}")
            return

        gecerli_uzantilar = ('.jpg', '.jpeg', '.png', '.bmp', '.tif')
        self.resim_listesi = [
            os.path.join(self.klasor_yolu, f) for f in os.listdir(self.klasor_yolu)
            if f.lower().endswith(gecerli_uzantilar)
        ]

        if self.resim_listesi:
            self.rastgele_getir()
        else:
            messagebox.showwarning("Uyarı", "Belirtilen klasörde format uyumlu fotoğraf bulunamadı!")

    def rastgele_getir(self):
        if not self.resim_listesi:
            return

        yol = random.choice(self.resim_listesi)

        file_bytes = np.fromfile(yol, dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            print(f"Hata: {yol} okunamadı.")
            return

        h, w = img.shape[:2]
        if max(h, w) > 520:
            scale = 520 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        self.image = img
        self.hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.guncelle()

    def kaydet(self):
        if self.image is None or self.son_mask is None:
            return

        # Sunum ve kontrol için özel çıktı klasörü oluşturuluyor
        ciktilar_klasoru = "Asama_Ciktilari"
        if not os.path.exists(ciktilar_klasoru):
            os.makedirs(ciktilar_klasoru)

        # 1. Aşama: Orijinal Görüntü
        cv2.imwrite(os.path.join(ciktilar_klasoru, "01_Orijinal_Mikroyapi.png"), self.image)

        # 2. Aşama: Ham Eşikleme Maskesi (Gürültülü)
        if self.mask_ham is not None:
            cv2.imwrite(os.path.join(ciktilar_klasoru, "02_Ham_Renk_Maskesi.png"), self.mask_ham)

        # 3. ve 4. Aşama: Morfolojik Filtreleme Ara Adımları
        if self.temiz_var.get() > 0:
            cv2.imwrite(os.path.join(ciktilar_klasoru, "03_Gurultu_Silinmis_Maske(Open).png"), self.mask_open)
            cv2.imwrite(os.path.join(ciktilar_klasoru, "04_Bosluklar_Kapatilmis_Maske(Close).png"), self.mask_close)

        # 5. Aşama: Nihai Binary Maske
        cv2.imwrite(os.path.join(ciktilar_klasoru, "05_Nihai_Faz_Maskesi.png"), self.son_mask)

        # 6. Aşama: Orijinal Görüntü Üzerine Kırmızı Vurgu
        overlay = self.image.copy()
        mask_bolgesi = (self.son_mask == 255)
        if np.any(mask_bolgesi):
            overlay[mask_bolgesi, 0] = (overlay[mask_bolgesi, 0] * 0.4).astype(np.uint8)
            overlay[mask_bolgesi, 1] = (overlay[mask_bolgesi, 1] * 0.4).astype(np.uint8)
            overlay[mask_bolgesi, 2] = np.clip(overlay[mask_bolgesi, 2] * 0.6 + 150, 0, 255).astype(np.uint8)

        cv2.imwrite(os.path.join(ciktilar_klasoru, "06_Renklendirilmis_Overlay.png"), overlay)

        # Kullanıcıya görsel onay ver
        messagebox.showinfo(
            "Rapor Hazır",
            f"Görüntü işleme adımlarının tamamı '{ciktilar_klasoru}' klasörüne numaralandırılarak kaydedildi.\n\nSunumunuzda bu fotoğrafları doğrudan kullanabilirsiniz."
        )

    # ==========================================
    # RENK SEÇME (EYEDROPPER)
    # ==========================================
    def tikla(self, event):
        if self.hsv is None:
            return
        x, y = event.x, event.y
        if 0 <= y < self.hsv.shape[0] and 0 <= x < self.hsv.shape[1]:
            h_deger = int(self.hsv[y, x][0])
            self.h_var.set(h_deger)
            self.guncelle()

    # ==========================================
    # ANA HESAPLAMA & ARA KATMAN KAYITLARI
    # ==========================================
    def guncelle(self):
        if self.image is None:
            return

        h_merkez = self.h_var.get()
        tol = self.tol_var.get()
        s_min = self.smin_var.get()
        v_min = self.vmin_var.get()
        temizlik = self.temiz_var.get()

        lower = np.array([max(0, h_merkez - tol), s_min, v_min])
        upper = np.array([min(179, h_merkez + tol), 255, 255])

        # AŞAMA 1: Ham Maske
        mask = cv2.inRange(self.hsv, lower, upper)
        self.mask_ham = mask.copy()

        # AŞAMA 2 & 3: Morfolojik İşlemler
        if temizlik > 0:
            kernel = np.ones((temizlik, temizlik), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            self.mask_open = mask.copy()  # Opening sonucu (gürültü silme)

            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            self.mask_close = mask.copy()  # Closing sonucu (boşluk doldurma)
        else:
            self.mask_open = None
            self.mask_close = None

        self.son_mask = mask

        sonuc = self.image.copy()
        mask_bolgesi = (mask == 255)

        if np.any(mask_bolgesi):
            sonuc[mask_bolgesi, 0] = (sonuc[mask_bolgesi, 0] * 0.4).astype(np.uint8)
            sonuc[mask_bolgesi, 1] = (sonuc[mask_bolgesi, 1] * 0.4).astype(np.uint8)
            sonuc[mask_bolgesi, 2] = np.clip(sonuc[mask_bolgesi, 2] * 0.6 + 150, 0, 255).astype(np.uint8)

        oran = (cv2.countNonZero(mask) / mask.size) * 100
        self.oran_label.config(text=f"Oran: %{oran:.2f}")

        self.goster(self.canvas_orijinal, self.image)
        self.goster(self.canvas_sonuc, sonuc)

    def goster(self, widget, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img_rgb)
        tk_im = ImageTk.PhotoImage(im)
        widget.configure(image=tk_im)
        widget.image = tk_im


if __name__ == "__main__":
    root = tk.Tk()
    app = RenkAyristiriciApp(root)
    root.mainloop()