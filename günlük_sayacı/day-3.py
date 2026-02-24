from astropy.coordinates import SkyCoord , EarthLocation , AltAz
import astropy.units as u
from astropy.time import Time
from astropy.table import Table
from astropy.utils.data import conf
conf.allow_insecure_downloads = True
konum = EarthLocation(lat=41*u.deg , lon=28*u.deg , height=45*u.m)
simdi = Time.now()
cerceve = AltAz(obstime=simdi, location=konum)
hedefler = ["sirius" , "betelgeuse" , "rigel" , "capella"  ]
rapor = Table(names = ("yıldız adı" , "yükseklik" , "hava kalitesi" ,"durum") , dtype = ("U15" , "f4" , "f4" , "U15"))

for isim in hedefler:
    yildiz_coord = SkyCoord.from_name(isim)
    yildiz_altaz = yildiz_coord.transform_to(cerceve)
    alt = yildiz_altaz.alt.deg
    if alt > 0:
        airmass = yildiz_altaz.secz.value
        if alt > 30:
            durum = "harika"
        else:
            durum = "berbat"
    else:
        airmass = 0.0
        durum = "görülemez"


    rapor.add_row([isim , alt , airmass , durum])
print(rapor)