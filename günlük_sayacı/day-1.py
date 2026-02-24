# from astropy import units as u
# from astropy.coordinates import EarthLocation
# from astropy.time import Time
# from astropy import constants as const
# location = EarthLocation(lat= 41.0082*u.deg ,lon = 28.9784*u.deg , height = 39*u.meter)
# now = Time.now()
# jd_now = now.jd
# lst_now = now.sidereal_time('mean' , longitude = location.lon)
# ls = const.c
# average_distance = 384400*u.km
# definion = (average_distance/ls).to(u.s)
# print(f"Sistem Zamanı:{now}")
# print(f"Julian Date: {jd_now}")
# print(f"Lst time: {lst_now}")
# print(f"time of ls: {definion.to}")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from astropy.time import Time
from astropy import units as u
now = Time.now()
nowa = now.utc
after_30_day = now + 30*u.day
nowx = now.tdb
define = after_30_day - now
print(define)
tdb = now.tdb
print(tdb)
x = (nowx.jd - nowa.jd)*u.second
print(x)
