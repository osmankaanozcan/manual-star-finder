import numpy as np
from numpy.ma.core import size
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# def f(x):
#     return x**2 + 10*np.sin(x)
#
# x0 = 0
# #-1.30644
# res =minimize(f , x0 )
# # x_grafik = np.linspace(-10,10,100)
# # plt.plot(x_grafik,f(x_grafik))
# # plt.plot(res.x , res.fun , "r*")
# # plt.show()
# print(res)

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||-

# def f(x):
#     return (x - 10)**2
# sinirlar = [(2,5)]
# res = minimize(f , x0=0 , bounds = sinirlar)
# print(res)

#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||-
def model(x , a , b):
    return a * np.sin(b * x)
x_veri = np.linspace(0,10,100)
y_gercek = 2.5 * np.sin(1.3* x_veri)
y_gurultu = y_gercek + 0.5 * np.random.normal(size=100)

parametreler , hata_payi = curve_fit(model , x_veri , y_gurultu )

plt.scatter(x_veri , y_gurultu , label = "gürültü" , color = "r" , s = 10)
plt.plot(x_veri , model(x_veri , *parametreler) , label = "tahmin" , color = "b")
plt.legend()
plt.show()