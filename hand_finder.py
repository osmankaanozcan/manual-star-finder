from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.time import Time
import astropy.units as u
from astroquery.simbad import Simbad

# --- GLOBAL LANGUAGE SETTINGS ---
LANG = "EN"  # Change to "TR" for Turkish

messages = {
    "EN": {
        "prompt": "Enter the celestial object you are looking for: ",
        "simbad_header": "\n___SIMBAD DATA___",
        "star_name": "Star Name",
        "magnitude": "Visual Magnitude (V)",
        "quality_score": "Observation Quality Score",
        "evaluation": "Evaluation",
        "simbad_not_found": "Warning: {} not found in SIMBAD",
        "simbad_error": "Problem connecting to SIMBAD database",
        "eval_perfect": "EXCELLENT - Ideal observation conditions",
        "eval_good": "GOOD - Acceptable observation conditions",
        "eval_mid": "AVERAGE - Limited observation conditions",
        "eval_poor": "POOR - Unsuitable observation conditions",
        "guide_header": "\n\n___CELESTIAL FINDING GUIDE___",
        "step_1": "Step-1: Face North and locate Polaris.",
        "step_2": "Step-2: Look exactly [{}] {} Polaris.",
        "step_3": "Step-3: From that point, move [{}] to the {}.",
        "success": "Congratulations, {} is exactly in the region you are looking at.",
        "above": "above", "below": "below",
        "right": "right", "left": "left",
        "measurements": ["span", "fist", "three fingers", "pinky finger"]
    },
    "TR": {
        "prompt": "Aradığınız gök cismini giriniz: ",
        "simbad_header": "\n___SIMBAD VERİLERİ___",
        "star_name": "Yıldız Adı",
        "magnitude": "Görünür Büyüklük (V)",
        "quality_score": "Gözlem Kalitesi Puanı",
        "evaluation": "Değerlendirme",
        "simbad_not_found": "Uyarı: {} SIMBAD'da bulunamadı",
        "simbad_error": "SIMBAD veritabanına bağlanırken sorun yaşandı",
        "eval_perfect": "MÜKEMMEL - Çok iyi gözlem koşulları",
        "eval_good": "İYİ - Kabul edilebilir gözlem koşulları",
        "eval_mid": "ORTA - Sınırlı gözlem koşulları",
        "eval_poor": "ZAYIF - Uygun olmayan gözlem koşulları",
        "guide_header": "\n\n___GÖKYÜZÜ BULMA REHBERİ___",
        "step_1": "Adım-1: Yüzünü tam kuzey'e dön ve polaris'i bul.",
        "step_2": "Adım-2: Polaris'ten tam [{}] kadar {} bak.",
        "step_3": "Adım-3: Sonra o noktadan [{}] kadar {} doğru kay.",
        "success": "Tebrikler, {} tam olarak baktığın o bölgede.",
        "above": "yukarısına", "below": "aşağısına",
        "right": "sağına", "left": "soluna",
        "measurements": ["karış", "yumruk", "üç parmak", "serçe parmak"]
    }
}

konum = EarthLocation(lat=42 * u.deg, lon=28 * u.deg, height=55 * u.m)
suan = Time.now()
x = input(messages[LANG]['prompt'])

try:
    yildiz = SkyCoord.from_name(x)
    P = SkyCoord.from_name("polaris")
    cercevee = AltAz(location=konum, obstime=suan)
    donusum_yildiz = yildiz.transform_to(cercevee)
    donusum_P = P.transform_to(cercevee)


    def gozlem_kalitesi(h, parlaklik):
        h_score = 20 if h < 10 else 60 if h < 30 else 100
        p_score = 100 if parlaklik < 2 else 70 if parlaklik < 4 else 30 if parlaklik < 6 else 0
        return (h_score * 0.4) + (p_score * 0.6)


    simbad = Simbad()
    sonuc = simbad.query_object(x)

    if sonuc is not None:
        parlaklik_mag = sonuc['V'][0] if 'V' in sonuc.colnames else 5.0
        puan = gozlem_kalitesi(donusum_yildiz.alt.degree, parlaklik_mag)

        if puan >= 80:
            yorum = messages[LANG]['eval_perfect']
        elif puan >= 60:
            yorum = messages[LANG]['eval_good']
        elif puan >= 40:
            yorum = messages[LANG]['eval_mid']
        else:
            yorum = messages[LANG]['eval_poor']

        print(messages[LANG]['simbad_header'])
        print(f"{messages[LANG]['star_name']}: {x}")
        print(f"{messages[LANG]['magnitude']}: {parlaklik_mag}")
        print(f"{messages[LANG]['quality_score']}: {puan:.2f}")
        print(f"{messages[LANG]['evaluation']}: {yorum}")
    else:
        print(messages[LANG]['simbad_not_found'].format(x))

    # ÖLÇÜM HESAPLAMA
    alt_farki = donusum_P.alt - donusum_yildiz.alt
    az_farki = donusum_P.az - donusum_yildiz.az


    def el_ile_olcum(derece_küsüratlari):
        derece = int(abs(derece_küsüratlari))
        m = messages[LANG]['measurements']
        karis = derece // 20
        yumruk = (derece % 20) // 10
        uc_parmak = ((derece % 20) % 10) // 5
        serce_parmak = ((derece % 20) % 10) % 5
        return f"{karis} {m[0]}, {yumruk} {m[1]}, {uc_parmak} {m[2]}, {serce_parmak} {m[3]}"


    dikey_olcum = el_ile_olcum(alt_farki.degree)
    yatay_olcum = el_ile_olcum(az_farki.degree)

    dikey_yon = messages[LANG]['above'] if donusum_yildiz.alt.degree > donusum_P.alt.degree else messages[LANG]['below']
    yatay_yon = messages[LANG]['right'] if donusum_yildiz.az.degree < 180 else messages[LANG]['left']

    print(messages[LANG]['guide_header'])
    print(messages[LANG]['step_1'])
    print(messages[LANG]['step_2'].format(dikey_olcum, dikey_yon))
    print(messages[LANG]['step_3'].format(yatay_olcum, yatay_yon))
    print(messages[LANG]['success'].format(x.upper()))

except Exception as e:
    print(messages[LANG]['simbad_error'])