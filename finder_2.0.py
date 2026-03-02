import requests
from astropy.coordinates import EarthLocation , SkyCoord , AltAz
from astropy.time import Time
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta , datetime
from astropy.coordinates import  get_body , get_sun


key = "683468370a34f0bffce0f6bcc9c3e4c5"
def hava_durumu(enlem,boylam):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={enlem}&lon={boylam}&appid={key}&units=metric"
    try:
        cevap = requests.get(url).json()
        bulut = cevap["clouds"]["all"]
        durum = cevap["weather"][0]["description"]
        temp = cevap["main"]["temp"]
        return bulut, durum, temp
    except:
        return None, "Veri alınamadı", None


lat = 42.0
lon = 28.0
konum = EarthLocation(lat=lat*u.deg, lon=lon*u.deg, height=55*u.m)
bulut, tarif, derece = hava_durumu(lat, lon)

print(f"--- GÖZLEM SAHASI DURUMU ---")
print(f"Sicaklik: {derece}°C")
print(f"Hava: {tarif.capitalize()}")
print(f"Bulut Orani: %{bulut}")

#------------------------------------------------------------------------------------

hedef_yazisi = input("\nHangi gök cismine bakmak istersiniz?")
hedef = SkyCoord.from_name(hedef_yazisi)
suan = Time.now()
zaman_araligi = suan + np.linspace(0,24,1440)*u.hour
lokal_zaman = np.array([t + timedelta(hours=3) for t in zaman_araligi.datetime])
cerceve = AltAz(obstime=zaman_araligi,location=konum)
hedef_altaz = hedef.transform_to(cerceve)
yukseklik = hedef_altaz.alt.degree
ufuk_yukarisi= yukseklik > 0
gorunur_zaman = lokal_zaman[ufuk_yukarisi]
visible_height = yukseklik[ufuk_yukarisi]

ay = get_body("moon",zaman_araligi)
ay_altaz = ay.transform_to(cerceve)
ay_yukseklik = ay_altaz.alt.degree[ufuk_yukarisi]

if len(gorunur_zaman) == 0:
    print(f"\n{hedef_yazisi} önümüzdeki 24 saat hiç doğmayacak")
else:
    plt.figure(figsize=(10,5))
    plt.plot(gorunur_zaman,visible_height,color = "w" , lw=2.5,label=hedef_yazisi)
    plt.plot(gorunur_zaman,ay_yukseklik,color="lightgray" , lw=2 , ls=":", alpha=0.5,label="ay")
    plt.axhline(0,color="b",ls="--",label="ufuk")
    plt.title(f"{hedef_yazisi.upper()} Doğuş ve Batış Arası Hareketi")
    plt.xlabel("Saat (Lokal)")
    plt.ylabel("Yükseklik (Derece)")
    plt.legend(loc="center right", facecolor="black", edgecolor="white", labelcolor="white", framealpha=0.8, bbox_to_anchor=(1.12, 0.5))
    plt.grid(True, alpha=0.2)
    plt.gca().set_facecolor('#0b0f19')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.show()

#------------------------------------------------------------------------------------

gunes_yukseklik = get_sun(zaman_araligi).transform_to(cerceve).alt.degree
maske = gunes_yukseklik < -6
uygun_sartlar = (yukseklik > 15) & maske
karanlik_zamanlar = lokal_zaman[gunes_yukseklik < -6.5]
safak_zamani = lokal_zaman[gunes_yukseklik > -6.5]

if np.any(uygun_sartlar):
    uygun_zaman = lokal_zaman[uygun_sartlar]
    safak = gunes_yukseklik < 5
    uygun_yukseklikler = yukseklik[uygun_sartlar]
    zirve_index = np.argmax(uygun_yukseklikler)
    zirve_zamani = uygun_zaman[zirve_index]
    zirve_yuksekligi = uygun_yukseklikler[zirve_index]
    start = uygun_zaman[0].strftime('%H:%M')
    end = uygun_zaman[-1].strftime('%H:%M')
    print(f"\n🌟 {hedef_yazisi.upper()} İÇİN ÖNERİLEN GÖZLEM ANI 🌟")
    print(f"\tSaat: {zirve_zamani.strftime('%H:%M')} (Yükseklik: {zirve_yuksekligi:.1f}°)")
    print(f"\tUygun Gözlem Aralığı: {start} - {end}")
    if len(karanlik_zamanlar) > 0:
        print(f"\nŞafak Saati: {safak_zamani[0].strftime('%H:%M') if isinstance(safak_zamani[0], datetime) else safak_zamani[0]}")
else:
    print(f"\n{hedef_yazisi.upper()} sağlıklı gözlem için önerilmiyor.")

