import cv2
import os
import numpy as np
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()
while True:
    print("Lütfen açılan pencereden bir fotoğraf seçin...")
    image_file = filedialog.askopenfilename(
        title="İşlem Yapılacak Fotoğrafı Seç",
        initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "goruntuler"))
    if not image_file:
        print("İptal edildi. Program tamamen sonlandırılıyor.")
        break
    print(f"Seçilen dosya yüklendi: {image_file}")
    image=cv2.imread(image_file)                                                                     #resmi içeri aktarıldı,okundu
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.namedWindow("image",cv2.WINDOW_NORMAL)                                              #daha iyi görebilmek için resim boyutlandırıldı
    cv2.namedWindow("mask", cv2.WINDOW_NORMAL)
    cv2.namedWindow('clean_mask', cv2.WINDOW_NORMAL)
    total_pixels = image.shape[0] * image.shape[1]                                                   #resimdeki toplam piksel sayısı hesaplandı
    print("boyut:",image.shape)                                                                      #resim boyutunu hesapladık
    def nothing(x):                                                                                  #boş bir fonksiyon tanımlandı
      pass
    cv2.namedWindow('trackbar')                                                                      #trackbar penceresi oluşturuldu
    cv2.resizeWindow('trackbar',250, 250)                                                           #trackbar penceresi boyutlandırıldı
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)                                               #resim bgr dan hsv ye dönüştürüldü
    cv2.createTrackbar("lower_h", "trackbar", 0, 180, nothing)   #track bar ayarları yapıldı hsv nın üst ve alt değerleri girildi"""
    cv2.createTrackbar("lower_s", "trackbar", 0, 255, nothing)
    cv2.createTrackbar("lower_v", "trackbar", 0, 255, nothing)
    cv2.createTrackbar("upper_h", "trackbar", 0, 180, nothing)
    cv2.createTrackbar("upper_s", "trackbar", 0, 255, nothing)
    cv2.createTrackbar("upper_v", "trackbar", 0, 255, nothing)
    cv2.setTrackbarPos("upper_h", "trackbar",180)            #sabit hsv üst değerleri ayarlandı
    cv2.setTrackbarPos("upper_s", "trackbar", 255)
    cv2.setTrackbarPos("upper_v", "trackbar",255)
    kernel=np.ones((3,3),np.uint8)                                             #morfolojik işlem. temiz görüntü elde etmek için

    while True:
       display_image=image.copy()                                                    #daha hızlı yineleme yapabilsin diye fotoğrafı kopyalayıp yapıştırdı
       lower_h = cv2.getTrackbarPos("lower_h", "trackbar")      #lower ve upper değişkenleri tanımlanarak işlem sırasında kullanılacak hale getirildi döngüye sokuldu"""
       lower_s = cv2.getTrackbarPos("lower_s", "trackbar")
       lower_v = cv2.getTrackbarPos("lower_v", "trackbar")
       upper_h = cv2.getTrackbarPos("upper_h", "trackbar")
       upper_s= cv2.getTrackbarPos("upper_s", "trackbar")
       upper_v= cv2.getTrackbarPos("upper_v", "trackbar")
       lower_color =np.array([lower_h, lower_s, lower_v])                           #trackbardan aldığı değerleri numpy kütüphanesiyle çalıştırır?
       upper_color =np.array([upper_h, upper_s,upper_v])
       mask=cv2.inRange(hsv_image, lower_color, upper_color)                        #filtreleme yapar hsvli resmi alır ve up ve low değerlerine göre filteler
       renkli_maske=np.zeros_like(image)
       renkli_maske[clean_mask == 255] = [0, 255, 0]
       alpha = 0.7
       beta = 0.3
       bindirilmis_goruntu = cv2.addWeighted(image, alpha, renkli_maske, beta, 0)
       clean_mask=cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)                    #arka plandaki beyaz ufak gürültüleri temizler
       clean_mask = cv2.morphologyEx(clean_mask, cv2.MORPH_CLOSE, kernel)           #arka plandaki siyah ufak gürültüleri temizler
       target_pixels=cv2.countNonZero(clean_mask)                                   #hedef piksel
       rate=float((total_pixels-target_pixels)/total_pixels)*100
       rate2 = float(target_pixels / total_pixels) * 100
       text=f"renk orani: %{rate:.2f}"
       text2 = f"renk orani2: %{rate2:.2f}"
       cv2.putText(display_image, text, (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
       cv2.putText(display_image, text2, (850, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
       cv2.imshow('image', display_image)
       cv2.imshow('mask', mask)
       cv2.imshow('clean_mask', clean_mask)
       if cv2.waitKey(20)& 0xFF== ord('q'):
         break

cv2.destroyAllWindows()