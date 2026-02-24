from matplotlib import pyplot as plt
from scipy.integrate import quad
import numpy as np

# def fonksiyon(x):
#     return x**2
# sonuc , hata = quad(fonksiyon, 0,10)
# print(f"integralin sonucu: {sonuc:.2f}")
# print(f"integralin hata payı: {hata:.2e}")

#Sonucu ve işlemin ne kadar güvenilir olduğunu (hata payını) ekrana yazdırıyor.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# def galaksi_isigi(x):
#     return 1/(x + 1)
# toplam_isik , hata = quad(galaksi_isigi,0,50)
# print(toplam_isik)
#Sonucu ve işlemin ne kadar güvenilir olduğunu (hata payını) ekrana yazdırıyor.

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

# def radyasyon(x):
#     return (np.log(x + 1) * np.exp(-0.5 * x))
# sonuc , hata = quad(radyasyon , 0 , 20)
# x = np.linspace(0,10,100)
# y = radyasyon(x)
# plt.plot(x,y,"r",linewidth=2 , label="Radyasyon eğrisi")
# plt.fill_between(x,y,color="b",alpha=0.3)
# plt.title("radyasyon dağılımı")
# plt.xlabel("zaman")
# plt.ylabel("yoğunluk")
# plt.grid(True , alpha=0.3)
# plt.legend()
# plt.show()

# Radyasyonun zamanla nasıl azaldığını hem hesaplıyor hem de altına boyalı bir grafik çiziyor.
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

toplam_alan = 0
def sayilar(x):
    x_tam = np.linspace(00,10,1000)
    araliklar =[(0,3,"red") , (3,5,"blue") , (5,8,"green"), (8,10,"black")]
    for bas , son , renk in araliklar:
        x_dilim = np.linspace(bas , son , 50)
        y_dilim = x_dilim
        plt.plot(x_dilim , y_dilim , color=renk , label = f"{bas}/{son} aralığı ")
        plt.fill_between(x_dilim , y_dilim , color=renk , alpha=0.3)
    plt.legend()
    plt.grid(True , alpha=0.3)
    plt.show()
sayilar(4)

# 0'dan 10'a kadar olan grafiği 4 farklı renge boyayarak parçalara ayırıyor ve görsel bir dağılım oluşturuyor.