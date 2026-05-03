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
from astroquery.simbad import Simbad
import re
from dotenv import load_dotenv
import os


LANG = "TR"  # Change to "TR" for Turkish

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

load_dotenv()
key = os.getenv("OPENWEATHER_API_KEY")

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
puan_s = np.where(gunes_yukseklik < -6, 50, 0)
maske = (gunes_yukseklik < -12) & (yukseklik > 15)
karanlik_zamanlar = lokal_zaman[gunes_yukseklik < -6.5]
safak_zamani = lokal_zaman[gunes_yukseklik > -3.5]

def gozlem_kalitesi(parlaklik):
    p_score = 100 if parlaklik < 2 else 70 if parlaklik < 4 else 30 if parlaklik < 6 else 0
    return p_score

simbad = Simbad()
simbad.add_votable_fields('V')
sonuc = simbad.query_object(hedef_yazisi)

if sonuc is not None:
    parlaklik_mag = sonuc['V'][0] if 'V' in sonuc.colnames else 5.0
else:
    parlaklik_mag = 5.0

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
    puan_s = 100
    ay_cezası = (ay_yuzde / 100) * ((180 - ay_mesafe) / 100) * 60
    yukseklik_ceza = ((90 - uygun_yukseklikler[zirve_index]) / 75) * 20
    puan -= puan_s
    puan -= (ay_cezası + (bulut * 1.5) + yukseklik_ceza)
    puan = max(0, min(100, puan))

    p_score = gozlem_kalitesi(parlaklik_mag)
    puan = (puan + p_score) / 2
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



#-------------------------------------------------------------------------------------------------------------------------------


def ilk_sayisal_kolon_degeri(tab, aday_kolonlar):
    if tab is None:
        return None
    ad_haritasi = {c.lower(): c for c in tab.colnames}
    for aday in aday_kolonlar:
        gercek_ad = ad_haritasi.get(aday.lower())
        if gercek_ad and not np.ma.is_masked(tab[gercek_ad][0]):
            try:
                return float(tab[gercek_ad][0])
            except (TypeError, ValueError):
                continue
    return None


def kimyasal_bilesim_tahmin_et(sonuc_tab, sp_harf):
    z_sun = 0.0134
    feh = ilk_sayisal_kolon_degeri(sonuc_tab, ["mesfe_h", "mesfe_h.fe_h", "fe_h", "feh"])

    if feh is not None:
        z_metal = z_sun * (10 ** feh)
        kaynak = f"[Fe/H] tabanli (SIMBAD, [Fe/H]={feh:+.2f})"
    else:
        z_varsayim = {
            "O": 0.0180, "B": 0.0170, "A": 0.0160,
            "F": 0.0150, "G": 0.0134, "K": 0.0120, "M": 0.0110,
        }
        z_metal = z_varsayim.get(sp_harf, z_sun)
        kaynak = "Spektral tip tabanli yaklasik tahmin"

    z_metal = float(np.clip(z_metal, 0.0001, 0.08))

    y_he = 0.2485 + 1.78 * z_metal
    y_he = float(np.clip(y_he, 0.24, 0.40))
    x_h = 1.0 - y_he - z_metal
    if x_h < 0.50:
        x_h = 0.50
        y_he = 1.0 - x_h - z_metal

    metal_paylari = {
        "Oksijen": 0.44,
        "Karbon": 0.18,
        "Neon": 0.09,
        "Demir": 0.08,
        "Silisyum": 0.05,
        "Magnezyum": 0.04,
    }
    diger_metal_pay = max(0.0, 1.0 - sum(metal_paylari.values()))

    bilesim = {
        "Hidrojen": x_h * 100,
        "Helyum": y_he * 100,
        "Oksijen": z_metal * metal_paylari["Oksijen"] * 100,
        "Karbon": z_metal * metal_paylari["Karbon"] * 100,
        "Neon": z_metal * metal_paylari["Neon"] * 100,
        "Demir": z_metal * metal_paylari["Demir"] * 100,
        "Silisyum": z_metal * metal_paylari["Silisyum"] * 100,
        "Magnezyum": z_metal * metal_paylari["Magnezyum"] * 100,
        "Diger Metaller": z_metal * diger_metal_pay * 100,
    }
    return bilesim, kaynak

simbad = Simbad()
simbad.add_votable_fields('V', 'mesFe_h', 'sp_type', 'plx_value', 'plx_err')
sonuc = simbad.query_object(hedef_yazisi)

if sonuc is not None:
    if 'V' in sonuc.colnames and not np.ma.is_masked(sonuc['V'][0]):
        parlaklik_mag = float(sonuc['V'][0])
    else:
        parlaklik_mag = 5.0

    sptype_raw = None
    if 'sp_type' in sonuc.colnames and not np.ma.is_masked(sonuc['sp_type'][0]):
        sptype_val = sonuc['sp_type'][0]
        if isinstance(sptype_val, bytes):
            sptype_raw = sptype_val.decode('utf-8').strip()
        else:
            sptype_raw = str(sptype_val).strip()

    parlaklik_sinifi = 'V'  # varsayılan: ana dizi
    sinif_etiketi = "Ana Dizi (V)"
    if sptype_raw:
        sptype_upper = sptype_raw.upper()

        if re.search(r'I[AB]', sptype_upper) or re.search(r'(?<![IV])I(?![IV])', sptype_upper):
            parlaklik_sinifi = 'I'
            sinif_etiketi = "Süper Dev (I)"
        elif 'III' in sptype_upper:
            parlaklik_sinifi = 'III'
            sinif_etiketi = "Dev (III)"
        elif 'II' in sptype_upper:
            parlaklik_sinifi = 'II'
            sinif_etiketi = "Parlak Dev (II)"
        elif 'IV' in sptype_upper:
            parlaklik_sinifi = 'IV'
            sinif_etiketi = "Alt Dev (IV)"


    sp_harf = None
    sp_sayi = None
    if sptype_raw:
        eslesme_sp = re.search(r'([OBAFGKM])(\d)', sptype_raw.upper())
        if eslesme_sp:
            sp_harf = eslesme_sp.group(1)
            sp_sayi = int(eslesme_sp.group(2))

    print(f"\n📋 SPEKTRAL BİLGİ: {sptype_raw}  →  {sinif_etiketi}")

    # ======================== KIMYASAL BILESIM ANALIZI ========================
    bilesim, bilesim_kaynagi = kimyasal_bilesim_tahmin_et(sonuc, sp_harf)
    print(f"\n🧪 KIMYASAL BILESIM (kutlece, tahmini)")
    print(f"   Kaynak: {bilesim_kaynagi}")
    print(
        f"   {hedef_yazisi.upper()} -> "
        f"%{bilesim['Hidrojen']:.1f} Hidrojen, "
        f"%{bilesim['Helyum']:.1f} Helyum, "
        f"%{bilesim['Silisyum']:.2f} Silisyum"
    )
    print(
        f"   Digerleri: O %{bilesim['Oksijen']:.2f}, C %{bilesim['Karbon']:.2f}, "
        f"Ne %{bilesim['Neon']:.2f}, Fe %{bilesim['Demir']:.2f}, "
        f"Mg %{bilesim['Magnezyum']:.2f}, Diger metal %{bilesim['Diger Metaller']:.2f}"
    )

    # ======================== DALGA BOYU YUZDELERI ========================
    sinif_sicaklik = {
        "O": 40000,
        "B": 20000,
        "A": 9000,
        "F": 7000,
        "G": 5778,
        "K": 4500,
        "M": 3300,
    }
    tahmini_sicaklik = sinif_sicaklik.get(sp_harf, 5778)

    dalga = np.linspace(100.0, 2500.0, 6000)  # nm
    h = 6.62607015e-34
    c = 2.99792458e8
    k_b = 1.380649e-23
    dalga_m = dalga * 1e-9
    planck = (2.0 * h * c ** 2) / (dalga_m ** 5 * (np.exp((h * c) / (dalga_m * k_b * tahmini_sicaklik)) - 1.0))

    uv_maske = (dalga >= 100.0) & (dalga < 400.0)
    vis_maske = (dalga >= 400.0) & (dalga < 700.0)
    ir_maske = (dalga >= 700.0) & (dalga <= 2500.0)

    uv_enerji = np.trapezoid(planck[uv_maske], dalga[uv_maske])
    vis_enerji = np.trapezoid(planck[vis_maske], dalga[vis_maske])
    ir_enerji = np.trapezoid(planck[ir_maske], dalga[ir_maske])
    toplam_enerji = uv_enerji + vis_enerji + ir_enerji

    uv_yuzde = 100.0 * uv_enerji / toplam_enerji
    vis_yuzde = 100.0 * vis_enerji / toplam_enerji
    ir_yuzde = 100.0 * ir_enerji / toplam_enerji

    uv_vis_oran = uv_enerji / vis_enerji if vis_enerji > 0 else 0.0
    ir_vis_oran = ir_enerji / vis_enerji if vis_enerji > 0 else 0.0
    tepe_dalga_nm = 2_897_771.955 / tahmini_sicaklik

    print(f"\n🌈 DALGA BOYU DAGILIMI (tahmini)")
    print(f"   Tahmini sicaklik: {tahmini_sicaklik} K (Spektral sinif: {sp_harf or 'G'})")
    print(f"   Tepe dalga boyu (Wien): ~{tepe_dalga_nm:.0f} nm")
    print(f"   UV (100-400 nm): %{uv_yuzde:.1f}")
    print(f"   Gorunur (400-700 nm): %{vis_yuzde:.1f}")
    print(f"   Kizilotesi (700-2500 nm): %{ir_yuzde:.1f}")
    print(f"   Goreli siddet oranlari -> UV/Gorunur: {uv_vis_oran:.2f}, IR/Gorunur: {ir_vis_oran:.2f}")

    # ======================== SICAKLIK ANALİZİ ========================
    hedef_sicaklik = None
    gunes_sicaklik = 5778   # K

    if 'mesfe_h.teff' in sonuc.colnames and not np.ma.is_masked(sonuc['mesfe_h.teff'][0]):
        teff = float(sonuc['mesfe_h.teff'][0])
        hedef_sicaklik = (teff * 0.90, teff * 1.10)

    elif sp_harf is not None:
        sp_sicaklik_ana_dizi = {
            'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000),
            'F': (6000, 7500),   'G': (5200, 6000),   'K': (3700, 5200),
            'M': (2400, 3700)
        }
        sp_sicaklik_super_dev = {
            'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000),
            'F': (6000, 7500),   'G': (4800, 5800),   'K': (3800, 4800),
            'M': (3000, 3800)
        }
        sp_sicaklik_dev = {
            'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000),
            'F': (6000, 7500),   'G': (5000, 5800),   'K': (3900, 5000),
            'M': (3000, 3900)
        }

        if parlaklik_sinifi == 'I':
            hedef_sicaklik = sp_sicaklik_super_dev.get(sp_harf)
        elif parlaklik_sinifi in ('II', 'III'):
            hedef_sicaklik = sp_sicaklik_dev.get(sp_harf)
        else:
            hedef_sicaklik = sp_sicaklik_ana_dizi.get(sp_harf)

    if hedef_sicaklik:
        t_lo, t_hi = hedef_sicaklik
        t_ort = (t_lo + t_hi) / 2
        fark = t_ort - gunes_sicaklik

        print(f"\n🔥 SICAKLIK ANALİZİ")
        print(f"   {hedef_yazisi.upper()} Yüzey Sıcaklığı: ~{t_lo:.0f} – {t_hi:.0f} K")
        print(f"   Güneş'in Yüzey Sıcaklığı: {gunes_sicaklik} K")

        if t_lo > gunes_sicaklik:

            kat_lo = t_lo / gunes_sicaklik
            kat_hi = t_hi / gunes_sicaklik
            print(f"   📌 Güneş'ten ~{kat_lo:.1f} – {kat_hi:.1f} kat daha sıcak. (+{t_lo - gunes_sicaklik:.0f} – {t_hi - gunes_sicaklik:.0f} K fark)")
        elif t_hi < gunes_sicaklik:

            kat_lo = gunes_sicaklik / t_hi
            kat_hi = gunes_sicaklik / t_lo
            print(f"   📌 Güneş'ten ~{kat_lo:.1f} – {kat_hi:.1f} kat daha soğuk. ({t_lo - gunes_sicaklik:.0f} – {t_hi - gunes_sicaklik:.0f} K fark)")
        else:

            print(f"   📌 Güneş ile benzer sıcaklık aralığında.")
    else:
        print(f"\n🔥 SICAKLIK ANALİZİ: {hedef_yazisi.upper()} için sıcaklık verisi bulunamadı.")

   
    if parlaklik_sinifi == 'I':
        sp_kutle_tablo = kutle_super_dev
    elif parlaklik_sinifi in ('II', 'III'):
        sp_kutle_tablo = kutle_dev
    else:
        sp_kutle_tablo = kutle_ana_dizi

    def tablo_aralik_ara(tablo, harf, sayi):
        """Tabloda (alt, üst) aralık döndür. Interpolasyon destekler."""
        anahtar = f"{harf}{sayi}"
        if anahtar in tablo:
            return tablo[anahtar]
        mevcut = sorted([int(k[1:]) for k in tablo if k.startswith(harf)])
        if not mevcut:
            return None
        alt_k = max([x for x in mevcut if x <= sayi], default=mevcut[0])
        ust_k = min([x for x in mevcut if x >= sayi], default=mevcut[-1])
        if alt_k == ust_k:
            return tablo[f"{harf}{alt_k}"]
        v_alt = tablo[f"{harf}{alt_k}"]
        v_ust = tablo[f"{harf}{ust_k}"]
        oran = (sayi - alt_k) / (ust_k - alt_k)
        lo = v_alt[0] + oran * (v_ust[0] - v_alt[0])
        hi = v_alt[1] + oran * (v_ust[1] - v_alt[1])
        return (lo, hi)

    hedef_kutle = None
    if sp_harf and sp_sayi is not None:
        hedef_kutle = tablo_aralik_ara(sp_kutle_tablo, sp_harf, sp_sayi)

    gunes_kutle_kg = 1.989e30  # kg

    print(f"\n⚖️ KÜTLE ANALİZİ")
    if hedef_kutle is not None:
        k_lo, k_hi = hedef_kutle
        k_ort = (k_lo + k_hi) / 2
        print(f"   Spektral Tip: {sptype_raw}  ({sinif_etiketi})")
        print(f"   {hedef_yazisi.upper()} Tahmini Kütlesi: ~{k_lo:.1f} – {k_hi:.1f} M☉")
        print(f"   Kilogram cinsinden: ~{k_lo * gunes_kutle_kg:.3e} – {k_hi * gunes_kutle_kg:.3e} kg")
        if k_lo > 1.05:
            print(f"   📌 Güneş'in yaklaşık {k_lo:.1f} – {k_hi:.1f} katı kadar ağır.")
        elif k_hi < 0.95:
            print(f"   📌 Güneş'in yaklaşık {1/k_hi:.1f} – {1/k_lo:.1f} katı kadar hafif.")
        else:
            print(f"   📌 Güneş ile benzer kütle aralığında.")
    else:
        print(f"   {hedef_yazisi.upper()} için kütle tahmini yapılamadı.")

    # ======================== YARIÇAP ANALİZİ ========================
    yaricap_ana_dizi = {
        'O3': (12.0, 18.0), 'O5': (10.0, 14.0), 'O7': (7.5, 10.5), 'O9': (6.5, 8.5),
        'B0': (6.0, 8.5), 'B2': (4.0, 5.5), 'B5': (3.3, 4.5), 'B8': (2.3, 3.1),
        'A0': (1.90, 2.50), 'A2': (1.75, 2.15), 'A5': (1.55, 1.88), 'A7': (1.48, 1.78),
        'F0': (1.33, 1.63), 'F2': (1.24, 1.48), 'F5': (1.14, 1.34), 'F8': (1.02, 1.18),
        'G0': (0.98, 1.12), 'G2': (0.94, 1.06), 'G5': (0.85, 0.99), 'G8': (0.80, 0.92),
        'K0': (0.74, 0.88), 'K2': (0.68, 0.80), 'K5': (0.56, 0.70), 'K7': (0.49, 0.61),
        'M0': (0.43, 0.55), 'M1': (0.38, 0.50), 'M2': (0.33, 0.45), 'M3': (0.27, 0.39),
        'M4': (0.21, 0.31), 'M5': (0.16, 0.24),
    }
    # Süper Dev (I) — Levesque et al., interferometrik ölçümler
    yaricap_super_dev = {
        'O5': (15.0, 25.0), 'O9': (14.0, 22.0),
        'B0': (22.0, 40.0), 'B2': (28.0, 45.0), 'B5': (35.0, 55.0), 'B8': (45.0, 70.0),
        'A0': (50.0, 75.0), 'A2': (65.0, 95.0), 'A5': (80.0, 120.0),
        'F0': (100.0, 150.0), 'F5': (130.0, 180.0), 'F8': (150.0, 210.0),
        'G0': (170.0, 240.0), 'G2': (200.0, 300.0), 'G5': (280.0, 420.0), 'G8': (380.0, 530.0),
        'K0': (400.0, 600.0), 'K2': (500.0, 700.0), 'K5': (650.0, 950.0),
        'M0': (700.0, 1000.0), 'M1': (700.0, 900.0), 'M2': (700.0, 900.0),
        'M3': (800.0, 1200.0), 'M4': (900.0, 1400.0), 'M5': (1000.0, 1500.0),
    }
    # Dev (III)
    yaricap_dev = {
        'B0': (7.0, 13.0), 'B5': (4.5, 7.5),
        'A0': (4.0, 6.0), 'A5': (3.5, 6.0),
        'F0': (4.0, 7.0), 'F5': (4.5, 7.5),
        'G0': (5.0, 8.0), 'G5': (8.0, 12.0), 'G8': (10.0, 15.0),
        'K0': (12.0, 18.0), 'K2': (15.0, 22.0), 'K5': (20.0, 30.0),
        'M0': (30.0, 50.0), 'M1': (40.0, 60.0), 'M2': (50.0, 75.0),
        'M3': (65.0, 100.0), 'M5': (100.0, 150.0),
    }

    if parlaklik_sinifi == 'I':
        sp_yaricap_tablo = yaricap_super_dev
    elif parlaklik_sinifi in ('II', 'III'):
        sp_yaricap_tablo = yaricap_dev
    else:
        sp_yaricap_tablo = yaricap_ana_dizi

    hedef_yaricap = None
    if sp_harf and sp_sayi is not None:
        hedef_yaricap = tablo_aralik_ara(sp_yaricap_tablo, sp_harf, sp_sayi)

    gunes_yaricap_km = 696_340
    gunes_yaricap_au = 0.00465047

    gezegen_yorungeleri = [
        ("Merkür",   0.387),
        ("Venüs",    0.723),
        ("Dünya",    1.000),
        ("Mars",     1.524),
        ("Jüpiter",  5.203),
        ("Satürn",   9.537),
        ("Uranüs",  19.191),
        ("Neptün",  30.069),
    ]

    print(f"\n📏 YARIÇAP ANALİZİ")
    if hedef_yaricap is not None:
        r_lo, r_hi = hedef_yaricap
        r_ort = (r_lo + r_hi) / 2
        r_lo_km = r_lo * gunes_yaricap_km
        r_hi_km = r_hi * gunes_yaricap_km
        r_lo_au = r_lo * gunes_yaricap_au
        r_hi_au = r_hi * gunes_yaricap_au

        print(f"   {hedef_yazisi.upper()} Tahmini Yarıçapı: ~{r_lo:.0f} – {r_hi:.0f} R☉")
        print(f"   Kilometre cinsinden: ~{r_lo_km:,.0f} – {r_hi_km:,.0f} km")

        if r_lo > 1.05:
            print(f"   📌 Güneş'in yaklaşık {r_lo:.0f} – {r_hi:.0f} katı büyüklüğünde.")
        elif r_hi < 0.95:
            print(f"   📌 Güneş'in yaklaşık {1/r_hi:.1f} – {1/r_lo:.1f} katı kadar küçük.")
        else:
            print(f"   📌 Güneş ile benzer boyutta.")

        # Gezegen yörüngesi karşılaştırması (ortalama yarıçap AU'ya çevrilir)
        if r_ort * gunes_yaricap_au > 0.05:
            print(f"\n   🪐 YÖRÜNGE KARŞILAŞTIRMASI (Güneş'in yerine konulursa):")
            for gezegen, uzaklik_au in gezegen_yorungeleri:
                if r_lo_au >= uzaklik_au:
                    print(f"      ✅ {gezegen} yörüngesi ({uzaklik_au} AU) → tamamen yutardı")
                elif r_hi_au >= uzaklik_au:
                    print(f"      ⚠️ {gezegen} yörüngesi ({uzaklik_au} AU) → sınırlarına dayanırdı")
                else:
                    print(f"      ❌ {gezegen} yörüngesi ({uzaklik_au} AU) → dışında kalırdı")
                    break
    else:
        print(f"   {hedef_yazisi.upper()} için yarıçap tahmini yapılamadı.")

    # ======================== HAYATINI TAMAMLAMA ORANI ========================
    # Kütle-Ömür ilişkisi (ana dizi): t ≈ (M/M☉)^(-2.5) × 10^10 yıl
    # Evrimsel aşama tespiti: parlaklık sınıfına göre ömrün ne kadarını yaşadığını tahmin et
    #   V   (Ana Dizi)     → Hidrojen füzyonu, ömrünün %0 – %90 arası
    #   IV  (Alt Dev)      → Çekirdek hidrojeni azalıyor, ömrünün ~%90 – %95 arası
    #   III (Dev)          → Hidrojen kabuğu füzyonu, ömrünün ~%95 – %98 arası
    #   II  (Parlak Dev)   → Helyum füzyonuna geçiş, ömrünün ~%97 – %99 arası
    #   I   (Süper Dev)    → Son evre, ömrünün ~%99 – %99.9+ arası

    evrim_oranlari = {
        'V':   (0.10, 0.85),    # Ana dizi — hayatının büyük bölümü
        'IV':  (0.88, 0.95),    # Alt dev — geçiş evresi
        'III': (0.95, 0.98),    # Dev — kabuğa geçiş
        'II':  (0.97, 0.99),    # Parlak dev — ileri evre
        'I':   (0.990, 0.999),  # Süper dev — son evre
    }

    print(f"\n⏳ HAYAT EVRESİ ANALİZİ")

    if hedef_kutle is not None:
        k_ort = (hedef_kutle[0] + hedef_kutle[1]) / 2

        omur_yil = 1e10 * (k_ort ** -2.5)

        if omur_yil >= 1e9:
            omur_str = f"{omur_yil / 1e9:.1f} milyar yıl"
        else:
            omur_str = f"{omur_yil / 1e6:.1f} milyon yıl"


        oran_lo, oran_hi = evrim_oranlari.get(parlaklik_sinifi, (0.10, 0.85))


        if parlaklik_sinifi == 'V' and sp_harf == 'G':
            oran_lo, oran_hi = (0.30, 0.60)

        print(f"   Tahmini Toplam Ömür: ~{omur_str}")
        print(f"   Evrimsel Aşama: {sinif_etiketi}")
        print(f"   {hedef_yazisi.upper()} Hayatını Tamamlama Oranı: %{oran_lo * 100:.1f} – %{oran_hi * 100:.1f}")

        # Kalan ömür tahmini
        kalan_lo = omur_yil * (1 - oran_hi)
        kalan_hi = omur_yil * (1 - oran_lo)
        if kalan_hi >= 1e9:
            kalan_str_lo = f"{kalan_lo / 1e9:.2f} milyar yıl" if kalan_lo >= 1e9 else f"{kalan_lo / 1e6:.1f} milyon yıl"
            kalan_str_hi = f"{kalan_hi / 1e9:.2f} milyar yıl"
        elif kalan_hi >= 1e6:
            kalan_str_lo = f"{kalan_lo / 1e6:.1f} milyon yıl" if kalan_lo >= 1e6 else f"{kalan_lo / 1e3:.0f} bin yıl"
            kalan_str_hi = f"{kalan_hi / 1e6:.1f} milyon yıl"
        else:
            kalan_str_lo = f"{kalan_lo / 1e3:.0f} bin yıl"
            kalan_str_hi = f"{kalan_hi / 1e3:.0f} bin yıl"

        print(f"   Tahmini Kalan Ömür: ~{kalan_str_lo} – {kalan_str_hi}")

        if k_ort > 25:
            son = "Kara Delik (Çekirdek çöküşü → Süpernova → Kara Delik)"
        elif k_ort > 8:
            son = "Nötron Yıldızı (Çekirdek çöküşü → Süpernova → Nötron Yıldızı)"
        elif k_ort > 0.5:
            son = "Beyaz Cüce (Dış katmanlar → Gezegen bulutsusu → Beyaz Cüce)"
        else:
            son = "Kırmızı Cüce (Çok yavaş sönerek milyarlarca yıl daha yanacak)"
        print(f"    Beklenen Son: {son}")
    else:
        print(f"   {hedef_yazisi.upper()} için hayat evresi tahmini yapılamadı.")

    # ======================== UZAKLIK ANALİZİ ========================


    print(f"\n🌌 UZAKLIK ANALİZİ")

    plx = None
    plx_err = None
    if 'plx_value' in sonuc.colnames and not np.ma.is_masked(sonuc['plx_value'][0]):
        plx = float(sonuc['plx_value'][0])
    if 'plx_err' in sonuc.colnames and not np.ma.is_masked(sonuc['plx_err'][0]):
        plx_err = float(sonuc['plx_err'][0])

    if plx and plx > 0:
        pc_to_ly = 3.26156
        ly_to_km = 9.461e12

        uzaklik_pc = 1000.0 / plx
        uzaklik_ly = uzaklik_pc * pc_to_ly

        if plx_err and plx_err > 0:
            plx_lo = max(plx - plx_err, 0.01)
            plx_hi = plx + plx_err
            uz_hi_pc = 1000.0 / plx_lo
            uz_lo_pc = 1000.0 / plx_hi
            uz_lo_ly = uz_lo_pc * pc_to_ly
            uz_hi_ly = uz_hi_pc * pc_to_ly

            print(f"   {hedef_yazisi.upper()} Uzaklığı: ~{uz_lo_ly:.0f} – {uz_hi_ly:.0f} ışık yılı")
            print(f"   Parsek cinsinden: ~{uz_lo_pc:.1f} – {uz_hi_pc:.1f} pc")
            print(f"   Kilometre cinsinden: ~{uz_lo_ly * ly_to_km:.2e} – {uz_hi_ly * ly_to_km:.2e} km")
        else:
            uz_lo_ly = uzaklik_ly
            uz_hi_ly = uzaklik_ly
            print(f"   {hedef_yazisi.upper()} Uzaklığı: ~{uzaklik_ly:.0f} ışık yılı")
            print(f"   Parsek cinsinden: ~{uzaklik_pc:.1f} pc")
            print(f"   Kilometre cinsinden: ~{uzaklik_ly * ly_to_km:.2e} km")

        uz_ort_ly = (uz_lo_ly + uz_hi_ly) / 2
        print(f"\n   🚀 YOLCULUK SÜRESİ KARŞILAŞTIRMASI:")
        print(f"      💡 Işık hızıyla (c): ~{uz_ort_ly:.0f} yıl")

        voyager_hiz_kmh = 61_200  # km/saat
        uzaklik_km = uz_ort_ly * ly_to_km
        voyager_saat = uzaklik_km / voyager_hiz_kmh
        voyager_yil = voyager_saat / (365.25 * 24)
        if voyager_yil >= 1e9:
            voyager_str = f"{voyager_yil / 1e9:.1f} milyar yıl"
        elif voyager_yil >= 1e6:
            voyager_str = f"{voyager_yil / 1e6:.1f} milyon yıl"
        else:
            voyager_str = f"{voyager_yil:,.0f} yıl"
        print(f"      🛰️ Voyager 1 hızıyla (61,200 km/h): ~{voyager_str}")

    else:
        print(f"   {hedef_yazisi.upper()} için paralaks verisi bulunamadığından uzaklık hesaplanamadı.")
else:
    parlaklik_mag = 5.0



