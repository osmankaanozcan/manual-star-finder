import requests
from astropy.coordinates import EarthLocation, SkyCoord, AltAz
from astropy.time import Time
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta, datetime
from astropy.coordinates import get_body, get_sun
from scipy.interpolate import make_interp_spline


LANG = "EN"  # Change to "TR" for Turkish

messages = {
    "EN": {
        "site_status": "--- OBSERVATION SITE STATUS ---",
        "temp": "Temperature",
        "weather": "Condition",
        "clouds": "Cloud Coverage",
        "input_prompt": "\nWhich celestial object would you like to observe? ",
        "not_rising": "will not rise in the next 24 hours.",
        "plot_title": "24-Hour Visibility Analysis",
        "x_label": "Time (Local)",
        "y_label": "Altitude (Degrees)",
        "moon": "Moon",
        "horizon": "Horizon",
        "rec_moment": "RECOMMENDED OBSERVATION MOMENT",
        "moon_bright": "Moon Brightness",
        "moon_dist": "Separation",
        "opt_window": "Optimal Observation Window",
        "dawn": "Dawn Time",
        "not_rec": "is not recommended for healthy observation.",
        "score": "Score",
        "score_ex": "Sky and weather conditions are EXCELLENT.",
        "score_avg": "Observation possible, conditions are AVERAGE.",
        "score_poor": "Observation might be challenging, conditions are POOR.",
        "score_fail": "Observation not possible under current conditions."
    },
    "TR": {
        "site_status": "--- GÖZLEM SAHASI DURUMU ---",
        "temp": "Sıcaklık",
        "weather": "Hava",
        "clouds": "Bulut Oranı",
        "input_prompt": "\nHangi gök cismine bakmak istersiniz? ",
        "not_rising": "önümüzdeki 24 saat hiç doğmayacak.",
        "plot_title": "24 Saatlik Görünürlük Analizi",
        "x_label": "Saat (Lokal)",
        "y_label": "Yükseklik (Derece)",
        "moon": "Ay",
        "horizon": "Ufuk",
        "rec_moment": "ÖNERİLEN GÖZLEM ANI",
        "moon_bright": "Ay'ın Parlaklığı",
        "moon_dist": "Mesafesi",
        "opt_window": "Uygun Gözlem Aralığı",
        "dawn": "Şafak Saati",
        "not_rec": "sağlıklı gözlem için önerilmiyor.",
        "score": "Puan",
        "score_ex": "Gökyüzü ve hava koşulları MÜKEMMEL.",
        "score_avg": "Gözlem yapılabilir, koşullar ORTALAMA.",
        "score_poor": "Gözlem zorlayıcı olabilir, koşullar KÖTÜ.",
        "score_fail": "Gözlem güncel koşullar ile yapılamaz."}}

key = "683468370a34f0bffce0f6bcc9c3e4c5"

def hava_durumu(enlem, boylam):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={enlem}&lon={boylam}&appid={key}&units=metric"
    try:
        cevap = requests.get(url).json()
        bulut = cevap["clouds"]["all"]
        durum = cevap["weather"][0]["description"]
        temp = cevap["main"]["temp"]
        return bulut, durum, temp
    except:
        return None, "Data unavailable", None


lat = 42.0
lon = 28.0
konum = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=55 * u.m)
bulut, tarif, derece = hava_durumu(lat, lon)

print(f"{messages[LANG]['site_status']}")
print(f"{messages[LANG]['temp']}: {derece}°C")
print(f"{messages[LANG]['weather']}: {tarif.capitalize()}")
print(f"{messages[LANG]['clouds']}: %{bulut}")

# CİSMİN ÖNÜMÜZDEKİ 24 SAAT BOYUNCA GÖRÜNÜRLÜK ANALİZİ
hedef_yazisi = input(messages[LANG]['input_prompt'])
hedef = SkyCoord.from_name(hedef_yazisi)
suan = Time.now()
zaman_araligi = suan + np.linspace(0, 24, 1440) * u.hour
lokal_zaman = np.array([t + timedelta(hours=3) for t in zaman_araligi.datetime])
cerceve = AltAz(obstime=zaman_araligi, location=konum)
hedef_altaz = hedef.transform_to(cerceve)
yukseklik = hedef_altaz.alt.degree
ufuk_yukarisi = yukseklik > 0
gorunur_zaman = lokal_zaman[ufuk_yukarisi]
visible_height = yukseklik[ufuk_yukarisi]

ay = get_body("moon", zaman_araligi)
ay_altaz = ay.transform_to(cerceve)
ay_yukseklik = ay_altaz.alt.degree[ufuk_yukarisi]

if len(gorunur_zaman) == 0:
    print(f"\n({hedef_yazisi.upper()}) {messages[LANG]['not_rising']}")
else:
    x_num = mdates.date2num(gorunur_zaman)
    x_puruzsuz = np.linspace(x_num.min(), x_num.max(), 1500)
    motor = make_interp_spline(x_num, visible_height, k=3)
    y_puruzsuz = motor(x_puruzsuz)
    zaman_puruzsuz = mdates.num2date(x_puruzsuz)

    plt.figure(figsize=(10, 5))
    plt.plot(zaman_puruzsuz, y_puruzsuz, color="w", lw=2.5, label=hedef_yazisi.upper())
    plt.plot(gorunur_zaman, ay_yukseklik, color="lightgray", lw=2, ls=":", alpha=0.5, label=messages[LANG]['moon'])
    plt.axhline(0, color="b", ls="--", label=messages[LANG]['horizon'])
    plt.title(f"{hedef_yazisi.upper()} - {messages[LANG]['plot_title']}")
    plt.xlabel(messages[LANG]['x_label'])
    plt.ylabel(messages[LANG]['y_label'])
    plt.legend(loc="center right", facecolor="black", edgecolor="white", labelcolor="white", framealpha=0.8,
               bbox_to_anchor=(1.134, 0.5))
    plt.grid(True, alpha=0.2)
    plt.gca().set_facecolor('#0b0f19')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.gcf().autofmt_xdate()
    plt.show()

# ANALİZ VE PUANLAMA
gunes_altaz = get_sun(zaman_araligi).transform_to(cerceve)
gunes_yukseklik = gunes_altaz.alt.degree
maske = (gunes_yukseklik < -6) & (yukseklik > 15)
karanlik_zamanlar = lokal_zaman[gunes_yukseklik < -6.5]
safak_zamani = lokal_zaman[gunes_yukseklik > -6.5]

if np.any(maske):
    uygun_zaman = lokal_zaman[maske]
    uygun_yukseklikler = yukseklik[maske]
    zirve_index = np.argmax(uygun_yukseklikler)
    gercek_index = np.where(maske)[0][zirve_index]

    start = uygun_zaman[0].strftime('%H:%M')
    end = uygun_zaman[-1].strftime('%H:%M')

    ay_mesafe = hedef_altaz[gercek_index].separation(ay_altaz[gercek_index]).degree
    ay_gunes_aci = gunes_altaz[gercek_index].separation(ay_altaz[gercek_index]).radian
    ay_yuzde = ((1 - np.cos(ay_gunes_aci)) / 2) * 100

    print(f"\n🌟 {messages[LANG]['rec_moment']} ({hedef_yazisi.upper()}) 🌟")
    print(f"\t {messages[LANG]['moon_bright']}: %{ay_yuzde:.1f}, {messages[LANG]['moon_dist']}: {ay_mesafe:.2f}°")
    print(f"\t {messages[LANG]['opt_window']}: {start} - {end}")
    if len(karanlik_zamanlar) > 0:
        print(f"\t {messages[LANG]['dawn']}: {safak_zamani[0].strftime('%H:%M')}")

    # PUANLAMA MANTIĞI
    puan = 100
    ay_cezası = (ay_yuzde / 100) * ((180 - ay_mesafe) / 100) * 60
    yukseklik_ceza = ((90 - uygun_yukseklikler[zirve_index]) / 75) * 20
    puan -= (ay_cezası + bulut + yukseklik_ceza)
    puan = max(0, min(100, puan))

    status_msg = ""
    if puan >= 80:
        status_msg = messages[LANG]['score_ex']
    elif puan >= 50:
        status_msg = messages[LANG]['score_avg']
    elif puan >= 30:
        status_msg = messages[LANG]['score_poor']
    else:
        status_msg = messages[LANG]['score_fail']

    print(f"🔭 {messages[LANG]['score']}: {puan:.2f} / 100 -> {status_msg}")
else:
    print(f"\n{hedef_yazisi.upper()} {messages[LANG]['not_rec']}")