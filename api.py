from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from astropy.coordinates import EarthLocation, SkyCoord, AltAz, get_body, get_sun
from astropy.time import Time
import astropy.units as u
import numpy as np
from datetime import timedelta
from astroquery.simbad import Simbad
import re
import traceback
from dotenv import load_dotenv
import os

#uvicorn api:app --reload
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = "683468370a34f0bffce0f6bcc9c3e4c5"


# ========================================================
# MODÜL 1: HAND FINDER
# ========================================================
@app.get("/api/handfinder")
def hand_finder(target_name: str):
    try:
        konum = EarthLocation(lat=42 * u.deg, lon=28 * u.deg, height=55 * u.m)
        suan = Time.now()
        yildiz = SkyCoord.from_name(target_name)
        polaris = SkyCoord.from_name("polaris")

        cerceve = AltAz(location=konum, obstime=suan)
        donusum_yildiz = yildiz.transform_to(cerceve)
        donusum_polaris = polaris.transform_to(cerceve)

        parlaklik_mag = 5.0
        try:
            simbad = Simbad()
            simbad.add_votable_fields('flux(V)')
            sonuc = simbad.query_object(target_name)
            if sonuc is not None:
                if 'FLUX_V' in sonuc.colnames and not np.ma.is_masked(sonuc['FLUX_V'][0]):
                    parlaklik_mag = float(sonuc['FLUX_V'][0])
                elif 'V' in sonuc.colnames and not np.ma.is_masked(sonuc['V'][0]):
                    parlaklik_mag = float(sonuc['V'][0])
        except Exception as e:
            pass

        h = float(donusum_yildiz.alt.degree)

        if h < 10:
            h_score = 20
        elif h < 30:
            h_score = 60
        else:
            h_score = 100

        if parlaklik_mag < 2:
            p_score = 100
        elif parlaklik_mag < 4:
            p_score = 70
        elif parlaklik_mag < 6:
            p_score = 30
        else:
            p_score = 0

        puan = float((h_score * 0.4) + (p_score * 0.6))

        if puan >= 80:
            yorum = "MÜKEMMEL"
        elif puan >= 60:
            yorum = "İYİ"
        elif puan >= 40:
            yorum = "ORTA"
        else:
            yorum = "ZAYIF"

        alt_farki = donusum_polaris.alt - donusum_yildiz.alt
        az_farki = donusum_polaris.az - donusum_yildiz.az

        def el_ile_olcum(derece_kusurati):
            derece = int(abs(float(derece_kusurati)))
            return {
                "karis": int(derece // 20),
                "yumruk": int((derece % 20) // 10),
                "uc_parmak": int(((derece % 20) % 10) // 5),
                "serce_parmak": int((((derece % 20) % 10) % 5) // 1)
            }

        return {
            "target": str(target_name).upper(),
            "dikey": el_ile_olcum(alt_farki.degree),
            "d_yon": "YUKARISINA" if float(donusum_yildiz.alt.degree) > float(
                donusum_polaris.alt.degree) else "AŞAĞISINA",
            "yatay": el_ile_olcum(az_farki.degree),
            "y_yon": "SAĞINA" if float(donusum_yildiz.az.degree) < 180 else "SOLUNA",
            "mag": float(round(parlaklik_mag, 2)),
            "score": float(round(puan, 1)),
            "yorum": str(yorum)
        }
    except Exception as e:
        return {"error": str(e)}


# ========================================================
# MODÜL 2: FINDER 2.0
# ========================================================
@app.get("/api/analyze")
def analyze_target(target_name: str):
    try:
        lat, lon = 42.0, 28.0
        konum = EarthLocation(lat=lat * u.deg, lon=lon * u.deg, height=55 * u.m)

        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        resp = requests.get(url)
        hava_cevap = resp.json()

        if resp.status_code == 200:
            bulut = float(hava_cevap["clouds"]["all"])
            durum = hava_cevap["weather"][0]["description"]
            temp = float(hava_cevap["main"]["temp"])
        else:
            bulut = 0.0
            durum = "Bilinmiyor"
            temp = 15.0

        parlaklik_mag = 5.0
        try:
            simbad = Simbad()
            simbad.add_votable_fields('flux(V)')
            sonuc = simbad.query_object(target_name)
            if sonuc is not None:
                if 'FLUX_V' in sonuc.colnames and not np.ma.is_masked(sonuc['FLUX_V'][0]):
                    parlaklik_mag = float(sonuc['FLUX_V'][0])
                elif 'V' in sonuc.colnames and not np.ma.is_masked(sonuc['V'][0]):
                    parlaklik_mag = float(sonuc['V'][0])
        except Exception as e:
            pass

        hedef = SkyCoord.from_name(target_name)
        suan = Time.now()
        zaman_araligi = suan + np.linspace(0, 24, 1440) * u.hour
        lokal_zaman = [t + timedelta(hours=3) for t in zaman_araligi.datetime]
        cerceve = AltAz(obstime=zaman_araligi, location=konum)

        hedef_altaz = hedef.transform_to(cerceve)
        yukseklik = hedef_altaz.alt.degree
        ay = get_body("moon", zaman_araligi).transform_to(cerceve).alt.degree
        gunes_altaz = get_sun(zaman_araligi).transform_to(cerceve)
        gunes_yukseklik = gunes_altaz.alt.degree

        uygun_sartlar = (yukseklik > 15) & (gunes_yukseklik < -6)
        safak_vakti = "Güneş Batmıyor"
        for i in range(1, len(gunes_yukseklik)):
            if gunes_yukseklik[i - 1] < -6.0 and gunes_yukseklik[i] >= -6.0:
                safak_vakti = lokal_zaman[i].strftime('%H:%M')
                break

        ay_yuzde, ay_mesafe, zirve_yuksekligi = 0.0, 180.0, float(np.max(yukseklik))
        start, end = "--:--", "--:--"

        if np.any(uygun_sartlar):
            uygun_yukseklikler = yukseklik[uygun_sartlar]
            zirve_index = int(np.argmax(uygun_yukseklikler))
            gercek_index = np.where(uygun_sartlar)[0][zirve_index]
            zirve_yuksekligi = float(uygun_yukseklikler[zirve_index])

            sol_index, sag_index = gercek_index, gercek_index
            while sol_index > 0 and uygun_sartlar[sol_index - 1]:
                sol_index -= 1
            while sag_index < len(uygun_sartlar) - 1 and uygun_sartlar[sag_index + 1]:
                sag_index += 1

            start_dt = lokal_zaman[sol_index]
            end_dt = lokal_zaman[sag_index]
            start = start_dt.strftime('%H:%M')
            end = end_dt.strftime('%H:%M')

            if start == end:
                end = (end_dt + timedelta(minutes=1)).strftime('%H:%M')

            ay_hedef_icin = get_body("moon", zaman_araligi).transform_to(cerceve)[gercek_index]
            ay_mesafe = float(hedef_altaz[gercek_index].separation(ay_hedef_icin).degree)
            ay_gunes_aci = float(gunes_altaz[gercek_index].separation(ay_hedef_icin).radian)
            ay_yuzde = float(((1 - np.cos(ay_gunes_aci)) / 2) * 100)

        cevre_puan = 100.0 - (((ay_yuzde / 100.0) * ((180.0 - ay_mesafe) / 100.0) * 60.0) + bulut + (
                    ((90.0 - zirve_yuksekligi) / 75.0) * 20.0))

        if parlaklik_mag < 2:
            p_score = 100
        elif parlaklik_mag < 4:
            p_score = 70
        elif parlaklik_mag < 6:
            p_score = 30
        else:
            p_score = 0
        hava_agirligi = 0.85
        parlaklik_agirligi = 0.15

        cevre_puan_sinirli = float(np.clip(cevre_puan, 0.0, 100.0))
        final_puan = int(np.clip(round(cevre_puan_sinirli * hava_agirligi + p_score * parlaklik_agirligi), 0, 100))
        return {
            "score": final_puan,
            "temp": temp,
            "weather": durum.capitalize(),
            "cloud": bulut,
            "moon_ill": round(ay_yuzde, 1),
            "moon_sep": round(ay_mesafe, 2),
            "obs_time": f"{start} - {end}" if start != "--:--" else "Önerilmez",
            "dawn_time": safak_vakti,
            "graph_labels": [t.strftime('%H:%M') for t in lokal_zaman[::10]],
            "target_y": yukseklik[::10].tolist(),
            "moon_y": ay[::10].tolist()
        }
    except Exception as e:
        return {"error": str(e)}


# ========================================================
# MODÜL 3: DERİN UZAY TELEMETRİSİ
# ========================================================
@app.get("/api/telemetry")
def get_telemetry(target_name: str):
    try:
        simbad = Simbad()
        simbad.add_votable_fields('V', 'mesFe_h', 'sp_type', 'plx_value', 'plx_err')
        sonuc = simbad.query_object(target_name)
        if sonuc is None:
            return {"error": "Cisim veritabanında bulunamadı."}

        sptype_raw = ""
        if 'sp_type' in sonuc.colnames and not np.ma.is_masked(sonuc['sp_type'][0]):
            val = sonuc['sp_type'][0]
            sptype_raw = val.decode('utf-8').strip() if isinstance(val, bytes) else str(val).strip()

        parlaklik_sinifi, sinif_id = 'V', "v"
        if sptype_raw:
            sp_up = sptype_raw.upper()
            if re.search(r'I[AB]', sp_up) or re.search(r'(?<![IV])I(?![IV])', sp_up):
                parlaklik_sinifi = 'I'
                sinif_id = "i"
            elif 'III' in sp_up:
                parlaklik_sinifi = 'III'
                sinif_id = "iii"
            elif 'II' in sp_up:
                parlaklik_sinifi = 'II'
                sinif_id = "ii"
            elif 'IV' in sp_up:
                parlaklik_sinifi = 'IV'
                sinif_id = "iv"

        sp_harf, sp_sayi = None, None
        if sptype_raw:
            eslesme = re.search(r'([OBAFGKM])(\d)', sptype_raw.upper())
            if eslesme:
                sp_harf = eslesme.group(1)
                sp_sayi = int(eslesme.group(2))

        t_lo, t_hi, teff_val = None, None, None
        for col in sonuc.colnames:
            if 'teff' in col.lower():
                val = sonuc[col][0]
                if not np.ma.is_masked(val):
                    teff_val = float(val)
                    break

        if teff_val is not None:
            t_lo, t_hi = teff_val * 0.90, teff_val * 1.10
        elif sp_harf:
            t_data = {
                'V': {'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000), 'F': (6000, 7500),
                      'G': (5200, 6000), 'K': (3700, 5200), 'M': (2400, 3700)},
                'I': {'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000), 'F': (6000, 7500),
                      'G': (4800, 5800), 'K': (3800, 4800), 'M': (3000, 3800)},
                'III': {'O': (30000, 50000), 'B': (10000, 30000), 'A': (7500, 10000), 'F': (6000, 7500),
                        'G': (5000, 5800), 'K': (3900, 5000), 'M': (3000, 3900)}
            }
            d_key = 'I' if parlaklik_sinifi == 'I' else ('III' if parlaklik_sinifi in ('II', 'III') else 'V')
            if sp_harf in t_data[d_key]:
                t_lo, t_hi = t_data[d_key][sp_harf]

        def tablo_ara(tablo, harf, sayi):
            if f"{harf}{sayi}" in tablo:
                return tablo[f"{harf}{sayi}"]
            mevcut = sorted([int(k[1:]) for k in tablo if k.startswith(harf)])
            if not mevcut:
                return None
            alt = max([x for x in mevcut if x <= sayi], default=mevcut[0])
            ust = min([x for x in mevcut if x >= sayi], default=mevcut[-1])
            if alt == ust:
                return tablo[f"{harf}{alt}"]
            v_alt, v_ust = tablo[f"{harf}{alt}"], tablo[f"{harf}{ust}"]
            oran = (sayi - alt) / (ust - alt)
            return (v_alt[0] + oran * (v_ust[0] - v_alt[0]), v_alt[1] + oran * (v_ust[1] - v_alt[1]))

        m_tablo = {
            'V': {'O3': (80.0, 120.0), 'O5': (45.0, 70.0), 'O7': (25.0, 35.0), 'O9': (18.0, 22.0), 'B0': (14.0, 20.0),
                  'B2': (6.0, 8.5), 'B5': (4.0, 5.5), 'B8': (2.7, 3.3), 'A0': (1.96, 2.40), 'A2': (1.80, 2.15),
                  'A5': (1.65, 1.90), 'A7': (1.55, 1.80), 'F0': (1.35, 1.58), 'F2': (1.25, 1.44), 'F5': (1.15, 1.33),
                  'F8': (1.04, 1.16), 'G0': (0.98, 1.08), 'G2': (0.95, 1.05), 'G5': (0.88, 0.98), 'G8': (0.83, 0.93),
                  'K0': (0.76, 0.88), 'K2': (0.70, 0.82), 'K5': (0.60, 0.72), 'K7': (0.53, 0.65), 'M0': (0.46, 0.57),
                  'M1': (0.38, 0.49), 'M2': (0.32, 0.40), 'M3': (0.24, 0.34), 'M4': (0.17, 0.24), 'M5': (0.12, 0.18)},
            'I': {'O5': (55.0, 90.0), 'O9': (25.0, 40.0), 'B0': (20.0, 30.0), 'B2': (16.0, 25.0), 'B5': (12.0, 18.0),
                  'B8': (10.0, 14.0), 'A0': (13.0, 18.0), 'A2': (11.0, 16.0), 'A5': (10.0, 15.0), 'F0': (9.0, 14.0),
                  'F5': (8.0, 12.0), 'F8': (7.0, 11.0), 'G0': (8.0, 13.0), 'G2': (8.0, 12.0), 'G5': (9.0, 14.0),
                  'G8': (10.0, 15.0), 'K0': (10.0, 16.0), 'K2': (11.0, 16.0), 'K5': (12.0, 18.0), 'M0': (13.0, 20.0),
                  'M1': (14.5, 21.0), 'M2': (16.5, 19.0), 'M3': (17.0, 25.0), 'M4': (20.0, 28.0), 'M5': (22.0, 30.0)},
            'III': {'B0': (16.0, 25.0), 'B5': (5.0, 9.0), 'A0': (3.0, 5.0), 'A5': (2.5, 3.5), 'F0': (2.0, 3.0),
                    'F5': (1.7, 2.3), 'G0': (2.0, 3.0), 'G5': (1.7, 2.4), 'G8': (1.5, 2.1), 'K0': (1.4, 2.0),
                    'K2': (1.2, 1.8), 'K5': (1.0, 1.6), 'M0': (0.9, 1.4), 'M1': (0.8, 1.3), 'M2': (0.8, 1.2),
                    'M3': (0.7, 1.1), 'M5': (0.6, 1.0)}
        }
        r_tablo = {
            'V': {'O3': (12.0, 18.0), 'O5': (10.0, 14.0), 'O7': (7.5, 10.5), 'O9': (6.5, 8.5), 'B0': (6.0, 8.5),
                  'B2': (4.0, 5.5), 'B5': (3.3, 4.5), 'B8': (2.3, 3.1), 'A0': (1.90, 2.50), 'A2': (1.75, 2.15),
                  'A5': (1.55, 1.88), 'A7': (1.48, 1.78), 'F0': (1.33, 1.63), 'F2': (1.24, 1.48), 'F5': (1.14, 1.34),
                  'F8': (1.02, 1.18), 'G0': (0.98, 1.12), 'G2': (0.94, 1.06), 'G5': (0.85, 0.99), 'G8': (0.80, 0.92),
                  'K0': (0.74, 0.88), 'K2': (0.68, 0.80), 'K5': (0.56, 0.70), 'K7': (0.49, 0.61), 'M0': (0.43, 0.55),
                  'M1': (0.38, 0.50), 'M2': (0.33, 0.45), 'M3': (0.27, 0.39), 'M4': (0.21, 0.31), 'M5': (0.16, 0.24)},
            'I': {'O5': (15.0, 25.0), 'O9': (14.0, 22.0), 'B0': (22.0, 40.0), 'B2': (28.0, 45.0), 'B5': (35.0, 55.0),
                  'B8': (45.0, 70.0), 'A0': (50.0, 75.0), 'A2': (65.0, 95.0), 'A5': (80.0, 120.0), 'F0': (100.0, 150.0),
                  'F5': (130.0, 180.0), 'F8': (150.0, 210.0), 'G0': (170.0, 240.0), 'G2': (200.0, 300.0),
                  'G5': (280.0, 420.0), 'G8': (380.0, 530.0), 'K0': (400.0, 600.0), 'K2': (500.0, 700.0),
                  'K5': (650.0, 950.0), 'M0': (700.0, 1000.0), 'M1': (700.0, 900.0), 'M2': (700.0, 900.0),
                  'M3': (800.0, 1200.0), 'M4': (900.0, 1400.0), 'M5': (1000.0, 1500.0)},
            'III': {'B0': (7.0, 13.0), 'B5': (4.5, 7.5), 'A0': (4.0, 6.0), 'A5': (3.5, 6.0), 'F0': (4.0, 7.0),
                    'F5': (4.5, 7.5), 'G0': (5.0, 8.0), 'G5': (8.0, 12.0), 'G8': (10.0, 15.0), 'K0': (12.0, 18.0),
                    'K2': (15.0, 22.0), 'K5': (20.0, 30.0), 'M0': (30.0, 50.0), 'M1': (40.0, 60.0), 'M2': (50.0, 75.0),
                    'M3': (65.0, 100.0), 'M5': (100.0, 150.0)}
        }

        m_key = 'I' if parlaklik_sinifi == 'I' else ('III' if parlaklik_sinifi in ('II', 'III') else 'V')
        k_lo, k_hi, r_lo, r_hi = None, None, None, None

        if sp_harf and sp_sayi is not None:
            m_res = tablo_ara(m_tablo[m_key], sp_harf, sp_sayi)
            if m_res:
                k_lo, k_hi = m_res
            r_res = tablo_ara(r_tablo[m_key], sp_harf, sp_sayi)
            if r_res:
                r_lo, r_hi = r_res

        orbits = []
        if r_lo is not None and r_hi is not None:
            gezegenler = [("mercury", 0.387), ("venus", 0.723), ("earth", 1.0), ("mars", 1.524), ("jupiter", 5.203)]
            r_lo_au = r_lo * 0.00465047
            r_hi_au = r_hi * 0.00465047
            for pid, au in gezegenler:
                if r_lo_au >= au:
                    status = "dead"
                elif r_hi_au >= au:
                    status = "danger"
                else:
                    status = "safe"
                orbits.append({"id": pid, "au": au, "status": status})

        life = {}
        if k_lo is not None:
            k_ort = (k_lo + k_hi) / 2
            omur = 1e10 * (k_ort ** -2.5)
            evrim_oran = {'V': (0.1, 0.85), 'IV': (0.88, 0.95), 'III': (0.95, 0.98), 'II': (0.97, 0.99),
                          'I': (0.99, 0.999)}
            oran_lo, oran_hi = evrim_oran.get(parlaklik_sinifi, (0.1, 0.85))
            if parlaklik_sinifi == 'V' and sp_harf == 'G':
                oran_lo, oran_hi = 0.3, 0.6

            if k_ort > 25:
                death_id = "bh"
            elif k_ort > 8:
                death_id = "ns"
            elif k_ort > 0.5:
                death_id = "wd"
            else:
                death_id = "rd"

            life = {
                "total": omur,
                "p_lo": oran_lo * 100,
                "p_hi": oran_hi * 100,
                "left_lo": omur * (1 - oran_hi),
                "left_hi": omur * (1 - oran_lo),
                "death": death_id
            }

        dist = {}
        if 'plx_value' in sonuc.colnames and not np.ma.is_masked(sonuc['plx_value'][0]):
            plx = float(sonuc['plx_value'][0])
            plx_err = float(sonuc['plx_err'][0]) if 'plx_err' in sonuc.colnames and not np.ma.is_masked(
                sonuc['plx_err'][0]) else 0
            if plx > 0:
                pc_lo = 1000.0 / (plx + plx_err) if plx_err else 1000.0 / plx
                pc_hi = 1000.0 / max(plx - plx_err, 0.01) if plx_err else 1000.0 / plx
                ly_lo = pc_lo * 3.26156
                ly_hi = pc_hi * 3.26156
                dist = {
                    "ly_lo": ly_lo,
                    "ly_hi": ly_hi,
                    "pc_lo": pc_lo,
                    "pc_hi": pc_hi,
                    "km_ort": ((ly_lo + ly_hi) / 2) * 9.461e12
                }

        return {
            "target": str(target_name).upper(),
            "spectral": {"raw": sptype_raw or "Bilinmiyor", "class_id": sinif_id},
            "temp": {"lo": t_lo, "hi": t_hi},
            "mass": {"lo": k_lo, "hi": k_hi},
            "radius": {"lo": r_lo, "hi": r_hi, "orbits": orbits},
            "life": life,
            "dist": dist
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}


# ========================================================
# MODÜL 4: KUANTUM & SPEKTROSKOPİ
# ========================================================
@app.get("/api/spectroscopy")
def get_spectroscopy(target_name: str):
    try:
        def _ilk_sayisal_kolon_degeri(tab, aday_kolonlar):
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

        simbad = Simbad()
        simbad.add_votable_fields("sp_type", "mesFe_h")
        sonuc = simbad.query_object(target_name)
        if sonuc is None:
            return {"error": "Cisim bulunamadı."}

        sp_type, sp_harf = None, None
        if "sp_type" in sonuc.colnames and not np.ma.is_masked(sonuc["sp_type"][0]):
            sp_raw = sonuc["sp_type"][0]
            sp_type = sp_raw.decode("utf-8").strip() if isinstance(sp_raw, bytes) else str(sp_raw).strip()
            for harf in ("O", "B", "A", "F", "G", "K", "M"):
                if harf in sp_type.upper():
                    sp_harf = harf
                    break

        # 1. KİMYASAL BİLEŞİM
        z_sun = 0.0134
        feh = _ilk_sayisal_kolon_degeri(sonuc, ["mesfe_h", "mesfe_h.fe_h", "fe_h", "feh"])
        if feh is not None:
            z_metal = z_sun * (10 ** feh)
        else:
            z_varsayim = {"O": 0.0180, "B": 0.0170, "A": 0.0160, "F": 0.0150, "G": 0.0134, "K": 0.0120, "M": 0.0110}
            z_metal = z_varsayim.get(sp_harf, z_sun)

        z_metal = float(np.clip(z_metal, 0.0001, 0.08))
        y_he = float(np.clip(0.2485 + 1.78 * z_metal, 0.24, 0.40))
        x_h = max(0.50, 1.0 - y_he - z_metal)

        if x_h == 0.50:
            y_he = 1.0 - x_h - z_metal

        bilesim = {
            "h": float(x_h * 100),
            "he": float(y_he * 100),
            "o": float(z_metal * 0.44 * 100),
            "c": float(z_metal * 0.18 * 100),
            "ne": float(z_metal * 0.09 * 100),
            "fe": float(z_metal * 0.08 * 100),
            "si": float(z_metal * 0.05 * 100),
            "mg": float(z_metal * 0.04 * 100),
            "other": float(z_metal * max(0.0, 1.0 - 0.88) * 100)
        }

        # 2. IŞIK & DALGA BOYU (PLANCK)
        sinif_sicaklik = {"O": 40000, "B": 20000, "A": 9000, "F": 7000, "G": 5778, "K": 4500, "M": 3300}
        sicaklik = sinif_sicaklik.get(sp_harf, 5778)

        dalga = np.linspace(100.0, 2500.0, 6000)
        h_const = 6.62607015e-34
        c_const = 2.99792458e8
        k_b = 1.380649e-23
        dalga_m = dalga * 1e-9
        spektrum = (2.0 * h_const * c_const ** 2) / (
                    dalga_m ** 5 * (np.exp((h_const * c_const) / (dalga_m * k_b * sicaklik)) - 1.0))

        uv_m = (dalga >= 100.0) & (dalga < 400.0)
        vis_m = (dalga >= 400.0) & (dalga < 700.0)
        ir_m = (dalga >= 700.0) & (dalga <= 2500.0)

        uv_enerji = float(np.trapezoid(spektrum[uv_m], dalga[uv_m]))
        vis_enerji = float(np.trapezoid(spektrum[vis_m], dalga[vis_m]))
        ir_enerji = float(np.trapezoid(spektrum[ir_m], dalga[ir_m]))

        toplam = uv_enerji + vis_enerji + ir_enerji

        return {
            "target": target_name.upper(),
            "sp_type": sp_type or "Bilinmiyor",
            "temp_k": float(sicaklik),
            "wien_nm": float(2_897_771.955 / sicaklik),
            "uv_pct": float(100.0 * uv_enerji / toplam),
            "vis_pct": float(100.0 * vis_enerji / toplam),
            "ir_pct": float(100.0 * ir_enerji / toplam),
            "chem": bilesim,
            "feh_source": "SIMBAD Verisi" if feh is not None else "Spektral Tahmin"
        }
    except Exception as e:
        traceback.print_exc()
        return {"error": str(e)}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)