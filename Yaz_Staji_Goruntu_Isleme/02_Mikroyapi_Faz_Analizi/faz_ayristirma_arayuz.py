import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


class RenkAyristiriciApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Renk Bazlı Faz Ayrıştırma")
        self.root.geometry("1150x680")

        self.image = None       # Yüklenen (küçültülmüş) BGR görüntü
        self.hsv = None         # Aynı görüntünün HSV hali
        self.son_mask = None    # En son hesaplanan ikili maske

        self.build_ui()

    # ==========================================
    # ARAYÜZ KURULUMU
    # ==========================================
    def build_ui(self):
        # Sol panel: kontroller
        left = tk.Frame(self.root, width=260, padx=12, pady=12)
        left.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(left, text="Fotoğraf Aç", command=self.dosya_ac).pack(fill=tk.X, pady=5)

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

        tk.Button(left, text="Sonucu Kaydet", command=self.kaydet).pack(fill=tk.X, pady=5)

        tk.Label(
            left,
            text="İpucu: Soldaki fotoğrafta\nhedef renge tıkla, H değeri\notomatik ayarlanır.",
            justify=tk.LEFT, fg="gray"
        ).pack(pady=15, anchor=tk.W)

        # Sağ panel: görüntüler
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
    def dosya_ac(self):
        yol = filedialog.askopenfilename(
            title="Fotoğraf seç",
            filetypes=[("Görüntüler", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not yol:
            return
        img = cv2.imread(yol)
        if img is None:
            return

        # Ekrana sığması için büyük fotoğrafları küçült
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
        overlay = self.image.copy()
        mask_bolgesi = (self.son_mask == 255)
        if np.any(mask_bolgesi):
            overlay[mask_bolgesi, 0] = (overlay[mask_bolgesi, 0] * 0.4).astype(np.uint8)
            overlay[mask_bolgesi, 1] = (overlay[mask_bolgesi, 1] * 0.4).astype(np.uint8)
            overlay[mask_bolgesi, 2] = np.clip(overlay[mask_bolgesi, 2] * 0.6 + 150, 0, 255).astype(np.uint8)
        cv2.imwrite("sonuc_maske.png", self.son_mask)
        cv2.imwrite("sonuc_overlay.png", overlay)
        print("Kaydedildi: sonuc_maske.png, sonuc_overlay.png")

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
    # ANA HESAPLAMA (her kaydırıcı hareketinde çalışır)
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

        mask = cv2.inRange(self.hsv, lower, upper)

        if temizlik > 0:
            kernel = np.ones((temizlik, temizlik), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        self.son_mask = mask

        # Orijinal fotoğrafın tam kopyasıyla başla (arka plan siyah olmasın)
        sonuc = self.image.copy()
        mask_bolgesi = (mask == 255)

        # Sadece seçilen pikselleri kırmızıyla vurgula, geri kalan yerlere DOKUNMA
        if np.any(mask_bolgesi):
            sonuc[mask_bolgesi, 0] = (sonuc[mask_bolgesi, 0] * 0.4).astype(np.uint8)  # Mavi azalt
            sonuc[mask_bolgesi, 1] = (sonuc[mask_bolgesi, 1] * 0.4).astype(np.uint8)  # Yeşil azalt
            sonuc[mask_bolgesi, 2] = np.clip(sonuc[mask_bolgesi, 2] * 0.6 + 150, 0, 255).astype(np.uint8)  # Kırmızı öne çıkar

        oran = (cv2.countNonZero(mask) / mask.size) * 100
        self.oran_label.config(text=f"Oran: %{oran:.2f}")

        self.goster(self.canvas_orijinal, self.image)
        self.goster(self.canvas_sonuc, sonuc)

    def goster(self, widget, img_bgr):
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img_rgb)
        tk_im = ImageTk.PhotoImage(im)
        widget.configure(image=tk_im)
        widget.image = tk_im  # referansı tut, garbage collector silmesin


if __name__ == "__main__":
    root = tk.Tk()
    app = RenkAyristiriciApp(root)
    root.mainloop()