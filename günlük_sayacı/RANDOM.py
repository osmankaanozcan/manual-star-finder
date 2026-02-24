from astropy.coordinates import SkyCoord , AltAz , EarthLocation
from astropy.time import Time
import astropy.units as u
konum = EarthLocation(lat = 42*u.deg , lon=28*u.deg , height=55*u.m)
suan = Time.now()
x = input("Aradığınız gök cismini giriniz.")
yildiz = SkyCoord.from_name(x)
P = SkyCoord.from_name("polaris")
cercevee = AltAz(location=konum, obstime=suan)
donusum_yildiz = yildiz.transform_to(cercevee)
donusum_P = P.transform_to(cercevee)

if donusum_yildiz.alt.degree > 15:
    print("gözleme uygun")
else:
    print("gözleme uygun değil")

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


print("___GÖKYÜZÜ BULMA REHBERİ___")
print(f"Adım-1: Yüzünü tam kuzey'e dön ve polaris'i bul")
print(f"Adım-2: Polaris'ten tam [{dikey_olcum}] kadar {dikey_yon} bak.")
print(f"Adım-3: Sonra o noktadan [{yatay_olcum}] kadar {yatay_yon} doğru kay.")
print(f"Tebrikler , {x.upper()} tam olarak baktığın o bölgede.")





