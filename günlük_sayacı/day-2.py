from astropy.coordinates import SkyCoord , AltAz , EarthLocation
from astropy.time import Time
import astropy.units as u
# konumumuz = EarthLocation(lat = 42.0*u.deg ,lon = 28.0*u.deg  , height = 45*u.m)
# now =Time.now()
# sirius = SkyCoord.from_name("sirius")
# altaz = AltAz(obstime = now , location = konumumuz)
# sonuç =sirius.transform_to(altaz)
# 
# print(f"RA = {sirius.ra:.2f} , DEC = {sirius.dec:.2f}")
# print(f"Yıldızın senin tependeki anlık yüksekliği: {sonuç.alt:.4f}")
# print(f"Yıldızın hangi yönde olduğu: {sonuç.az:.2f}")



# konumumuz = EarthLocation(lat = 42.0*u.deg ,lon = 28.0*u.deg  , height = 45*u.m)
# now = Time.now()
# sirius = SkyCoord.from_name("sirius")
# konumu = AltAz(obstime = now , location = konumumuz)
# transı = sirius.transform_to(konumu)
# altı = transı.alt
# zeniti = transı.zen
# airmass = transı.secz
# if airmass <= 2.0:
#     print("hacı ortam efso")
# if airmass >= 3.0:
#     print("hacı ortam berbo")
#
# print(f"Hedef: Sirius yıldızı")
# print(f"yüksekliği: {altı.deg:.2f}")
# print(f"zeniti: {zeniti.deg:.2f}")
# print(f"airmass değeri: {airmass:.2f}")





