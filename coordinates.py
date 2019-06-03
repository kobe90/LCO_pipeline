from astropy.time import Time
from astropy.coordinates import SkyCoord
import numpy as np
from astropy import units as u
from visibility import *
import sfdmap
import os
from LCO import *

#example of "sfddata-master" folder located in the home directory
map_location=os.environ['HOME']
m = sfdmap.SFDMap(map_location+'/sfddata-master/')

class Coordinates:
    def __init__(self, ra, dec, observatory, time):
        self.ra=ra
        self.dec=dec
        self.observatory = observatory
        self.time = time
        times=[time+tempo*u.min for tempo in range(0, 30, 5)]
        alts=[]
        az=[]
        suns=[]
        moon_dists=[]
        sun_dists=[]
        for time in times:
            giacomo,_,_,_,moon_dist,sun_dist,_ = visibility(ra, dec, self.observatory,time)
            alts.append(giacomo.alt.value)
            az.append(giacomo.az.value)
            frame = AltAz(obstime = time, location=self.observatory.position)
            suns.append(get_sun(time).transform_to(frame).alt.value)
            moon_dists.append(moon_dist.value)
            sun_dists.append(sun_dist.value)
        alts=np.array(alts)
        az=np.array(az)
        suns=np.array(suns)
        moon_dists=np.array(moon_dists)
        sun_dists=np.array(sun_dists)
        self.alts = alts
        self.az=az
        self.suns = suns
        self.moon_dist=np.mean(moon_dists*u.degree)
        self.sun_dist=np.mean(sun_dists*u.degree)

def available(ra, dec, list, time):
    selection=[]
    for ciao in list:
        coor=Coordinates(ra, dec, ciao, time)
        if np.all(coor.alts>30) and np.all(coor.suns<-12) and (coor.moon_dist>30*u.degree) and (coor.sun_dist>30*u.degree) and np.all(1./(np.sin(coor.alts*2*np.pi/360))<3.0) and (weather_ok(ciao.name)=='ok'): #and np.all(coor.az<4.6*15) and (coor.av<2.) 
            selection.append(coor.observatory)
    return selection