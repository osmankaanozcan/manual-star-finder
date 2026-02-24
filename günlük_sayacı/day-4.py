import  numpy as np
import matplotlib.pyplot as plt
import astropy.units as u
from astropy.coordinates import SkyCoord , EarthLocation , AltAz , get_sun
from astropy.time import Time
konumum = EarthLocation(lat =41*u.deg , lon = 28*u.deg , height = 46*u.m)
now = Time.now()
aralık = np.linspace(0,12,48)
seri = now + aralık

Hedefler =["sirius", "betelgeuse", "rigel", "capella"]
plt.figure(figsize=(12,6))

for isim in Hedefler:
    yildiz = SkyCoord.from_name(isim)
    yukseklikler = []


    for an in seri:
        cerceve = AltAz(obstime = an , location = konumum)
        yildiz_yerel = yildiz.transform_to(cerceve)
        yukseklikler.append(yildiz_yerel.alt.deg)
    plt.plot(aralık , yukseklikler , label= isim.capitalize() , linewidth = 2.5)

gunes_alt = []
for an in seri:
    gunes = get_sun(an).transform_to(AltAz(obstime = an, location = konumum))
    gunes_alt.append(gunes.alt.deg)
plt.fill_between(aralık , -90 , 90 , where = np.array(gunes_alt) <-18 , color = "midnightblue" , alpha = 0.2 )
plt.axhline(0 , color = "black" , lw = 1.5)
plt.axhline(30 , color="r" , ls = "--" , alpha = 0.5 , label = "gözlemci enlemi")
plt.xlim(-20,90)
plt.title(f"Gözlem Simülasyonu: {now.iso[:16]}", fontsize=12)
plt.xlabel("Geçen Süre")
plt.ylabel("yükseklik")
plt.legend(loc="upper left" , frameon=True)
plt.grid(True , alpha = 0.2)
plt.show()