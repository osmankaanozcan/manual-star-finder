from os import remove

import numpy as  np
from scipy import stats
import matplotlib.pyplot as plt
# dagilim = stats.norm(loc=50 , scale=10)
# veri = dagilim.rvs(size=1000)
# print(f"ortalama: {np.mean(veri):.2f}")
# print(f"standart sapma: {np.std(veri):.2f}")
#
# plt.hist(veri , bins=30 , density=True , alpha= 0.6 , color="g" , label = "veriler")
# x = np.linspace(20,80,100)
# plt.plot(x , dagilim.pdf(x) , "r-" , lw=2 , label = "çan eğrisi")
# plt.legend()
# plt.show()

#_------------------------------------------------------------------------------------------------

# import numpy as np
# import matplotlib.pyplot as plt
# from scipy.interpolate import interp1d
#
# x = np.array([0,1,2,3,4,5])
# y = np.array([0,2,1,3,4,3])
#
# f_lineer = interp1d(x,y,kind="linear")
# f_kubik = interp1d(x,y,kind="cubic")
#
# x_yeni = np.linspace(0,5,50)
# y_lineer = f_lineer(x_yeni)
# y_kubik = f_kubik(x_yeni)
# plt.plot(x, y, 'o', label='Gerçek Noktalar')
# plt.plot(x_yeni, y_lineer, '--', label='Lineer (Düz)')
# plt.plot(x_yeni, y_kubik, '-', label='Kubik (Kavisli)')
# plt.legend()
# plt.show()

#_------------------------------------------------------------------------------------------------
#
# from astropy.coordinates  import SkyCoord
#
# sirius = SkyCoord.from_name("sirius")
# betelgeuse = SkyCoord.from_name("betelgeuse")
# print(sirius.to_string("hmsdms"))
# mesafe = sirius.separation(betelgeuse)
# print(mesafe.degree)

#_------------------------------------------------------------------------------------------------

import pandas as pd
import io

raw_data = """Campaign_ID,Category,Ad_Spend,Revenue
1001,Social,500.0,1200.0
1002,Search,-150.0,800.0
1003,Social,600.0,
1004,Display,200.0,300.0
1005,Search,400.0,
1006,Social,550.0,1300.0
1007,Display,-50.0,400.0
1008,Search,450.0,900.0"""

df = pd.read_csv(io.StringIO(raw_data))
print("--- orjinali ---")
print(df)

df_temiz = df[df["Ad_Spend"] >= 0].copy()
df_temiz["Revenue"] = df_temiz.groupby("Category")["Revenue"].transform(lambda x: x.fillna(x.mean()))
print(df_temiz)