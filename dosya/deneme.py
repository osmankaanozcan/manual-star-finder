from astropy.coordinates import SkyCoord , AltAz , EarthLocation
from astropy.time import Time
import astropy.units as u
from astroquery.simbad import Simbad


konum = EarthLocation(lat = 42*u.deg , lon=28*u.deg , height=55*u.m)
suan = Time.now()
x = input("Aradığınız gök cismini giriniz.")
yildiz = SkyCoord.from_name(x)
P = SkyCoord.from_name("polaris")
cercevee = AltAz(location=konum, obstime=suan)
donusum_yildiz = yildiz.transform_to(cercevee)
donusum_P = P.transform_to(cercevee)

def gozlem_kalitesi(h,parlaklik):
    if h < 10:
        h_score = 20
    elif h < 30:
        h_score = 60
    else:
        h_score = 100
    if parlaklik > 2:
        p_score = 100
    elif parlaklik > 4:
        p_score = 70
    elif parlaklik > 6:
        p_score = 30
    else:
        p_score = 0

    puan = (h_score * 0.4) + (p_score * 0.6)  #faktörlerin  etkileme oranlarına göre dağılımı
    return puan

try:
    simbad = Simbad()
    sonuc = simbad.query_object(x)

    if sonuc is not None:
        if 'V' in sonuc.colnames:
            parlaklik_mag = sonuc['V'][0]
        else:
            parlaklik_mag = 5.0


        puan = gozlem_kalitesi(donusum_yildiz.alt.degree, parlaklik_mag)

        if puan >= 80:
            yorum = "MÜKEMMEL - Çok iyi gözlem koşulları"
        elif puan >= 60:
            yorum = "İYİ - Kabul edilebilir gözlem koşulları"
        elif puan >= 40:
            yorum = "ORTA - Sınırlı gözlem koşulları"
        else:
            yorum = "ZAYIF - Uygun olmayan gözlem koşulları"
        print(f"\n___SIMBAD VERİLERİ___")
        print(f"Yıldız Adı: {x}")
        print(f"Görünür Büyüklük (V): {parlaklik_mag}")
        print(f"Gözlem Kalitesi Puanı: {puan:.2f}")
        print(f"Değerlendirme: {yorum}")
    else:
        print(f"Uyarı: {x} SIMBAD'da bulunamadı")

except Exception as e:
    print("SIMBAD veritabanına bağlanırken sorun yaşandı")





uzaklik = donusum_yildiz.separation(donusum_P)
alt_farki = donusum_P.alt - donusum_yildiz.alt
az_farki = donusum_P.az - donusum_yildiz.az
def el_ile_olcum(derece_küsüratlari):
    derece = int(abs(derece_küsüratlari))
    karis = derece // 20
    kalan1 = derece % 20
    yumruk = kalan1 // 10
    kalan2 = kalan1 % 10
    uc_parmak = kalan2 // 5
    kalan3 = kalan2 % 5
    serce_parmak = kalan3 // 1
    return f"{karis} karış , {yumruk} yumruk , {uc_parmak} üç parmak,{serce_parmak} serce_parmak"

dikey_olcum = el_ile_olcum(alt_farki.degree)
yatay_olcum = el_ile_olcum(az_farki.degree)
if donusum_yildiz.alt.degree > donusum_P.alt.degree:
    dikey_yon = "yukarısına"
else:
    dikey_yon = "asagısına"

if donusum_yildiz.az.degree < 180:
    yatay_yon= "sağına"
else:
    yatay_yon="soluna"

print("\n\n___GÖKYÜZÜ BULMA REHBERİ___")
print(f"Adım-1: Yüzünü tam kuzey'e dön ve polaris'i bul")
print(f"Adım-2: Polaris'ten tam [{dikey_olcum}] kadar {dikey_yon} bak.")
print(f"Adım-3: Sonra o noktadan [{yatay_olcum}] kadar {yatay_yon} doğru kay.")
print(f"Tebrikler , {x.upper()} tam olarak baktığın o bölgede.")

