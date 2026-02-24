# from astropy.coordinates import SkyCoord
# from astroquery.simbad import Simbad
# import astropy.units as u
# import matplotlib.pyplot as plt
#
# # 1. Hedef Belirleme (Andromeda)
# hedef_isim = "andromeda"
# print(f"{hedef_isim} için veriler toplanıyor, lütfen bekle...")
# konum = SkyCoord.from_name(hedef_isim)
#
# # 2. Bölge Sorgusu (2 derecelik geniş bir alan)
# # Not: Alanı 2.0 yaparak galaksinin o meşhur elips şeklini yakalıyoruz
# taranacak_alan = 2.0 * u.deg
# sonuç = Simbad.query_region(konum, radius=taranacak_alan)
#
# # 3. Akıllı Koordinat Dönüşümü
# # Tablodaki 'RA' ve 'DEC' sütunlarını alıp sayısal dereceye çeviriyoruz
# # Bu satır az önce aldığın bütün hataları (KeyError, UnitError) kökten çözer
# harita = SkyCoord(ra=sonuç['ra'], dec=sonuç['dec'], unit=(u.deg, u.deg))
#
# # 4. Görselleştirme (Makyaj Kısmı)
# plt.figure(figsize=(12, 10))
# plt.gca().set_facecolor('#0a0a0a') # Arka planı derin uzay siyahı yapalım
#
# # Tüm yıldızları turkuaz, küçük ve hafif şeffaf çiziyoruz (s=1)
# plt.scatter(harita.ra.deg, harita.dec.deg, s=1, c='cyan', alpha=0.6, label="Tespit Edilen Yıldızlar")
#
# # SADECE Andromeda'nın merkezini kocaman kırmızı bir X ile işaretliyoruz (s=250)
# plt.scatter(konum.ra.deg, konum.dec.deg, s=250, c='red', marker='x', linewidths=3, label="Galaksi Merkezi")
#
# # Grafik Bilgileri (xlabel, ylabel, title)
# plt.title(f"{hedef_isim.upper()} YILDIZ HARİTASI - GÖREV TAMAMLANDI", color='white', fontsize=15)
# plt.xlabel("Sağ Açıklık (RA) [Derece]", color='white')
# plt.ylabel("Dik Açıklık (DEC) [Derece]", color='white')
# plt.grid(True, linestyle='--', alpha=0.2)
# plt.legend(loc='upper right')
#
# print("Harita oluşturuldu. Görüntüleniyor...")
# plt.show()
#
# # Sütun isimlerini merak edersen aşağıda görebilirsin
# print("\nVeri Tablosu Sütunları:", sonuç.colnames)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# from astropy.io import fits
# import matplotlib.pyplot as plt
# from astropy.utils.data import download_file
# import numpy as np
#
# veri = r"C:\Users\ilknu\Downloads\m31.fits"
# hdul = fits.open(veri)
# goruntu = hdul[0].data
# # logx = np.log10(goruntu + 1)
# plt.imshow(goruntu , cmap='inferno')
# plt.show()
# plt.imshow(goruntu , cmap='viridis' , vmin=800, vmax=1500)
# plt.show()
# plt.show()
# hdul.close()
# plt.close("all")

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

import astropy.units as u
import numpy as np
from astropy.io import fits
import constant as c

veri = r"C:\Users\ilknu\Downloads\m31.fits"
hdul = fits.open(veri)
goruntu = hdul[0].data
toplama = np.sum(goruntu)
dx = 23e6 * u.lyr
d = dx.to(u.m)
pi = c.
