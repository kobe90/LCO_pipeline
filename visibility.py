from __future__ import print_function
import numpy as np
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)
import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.coordinates import Angle
from astropy.coordinates import get_sun, get_moon
import ephem
from matplotlib.axes import Axes
import sfdmap
import os
from LCO import *
import dill

#locating radio maps for extinction
map_location='.'
m = sfdmap.SFDMap(map_location+'/sfddata-master/')

#defining the "Observatory" class
class Observatory:
    def __init__(self, name, acr):
        self.name=name
        self.acr=acr
        self.position=EarthLocation.of_site(self.name)

#defining our observatories
siding_spring=Observatory('Siding Spring Observatory', 'Sid Spr')
mc_donald=Observatory('McDonald', 'McD')
cerro=Observatory('Cerro Tololo', 'Ce Tol')
southern=Observatory('Sutherland', 'Su')
hawaii=Observatory('Haleakala', 'Hal')
observatories_north=[mc_donald, hawaii]
observatories_south=[siding_spring, cerro, southern]

#calculating the visibility of a target from a determined obseratory
def visibility(ra, dec, observatory, time):

    source = SkyCoord(ra=Angle(ra*u.deg), dec=(dec*u.deg))
    location = observatory.position
    
    time = Time(time)
    
    altaz = source.transform_to(AltAz(obstime=time,location=location))
    altaz_sun = get_sun(time).transform_to(AltAz(obstime=time,location=location))
    altaz_moon = get_moon(time).transform_to(AltAz(obstime=time,location=location))
        
    delta_time = np.linspace(0, 24, 200)*u.hour

    frame = AltAz(obstime = time+delta_time, location=location)
    frame_night = source.transform_to(frame)
    frame_sun_night = get_sun(time+delta_time).transform_to(frame)
    frame_moon_night = get_moon(time+delta_time).transform_to(frame)
    moon_distance=np.mean(source.separation(SkyCoord(get_moon(time+delta_time).ra,get_moon(time+delta_time).dec)))
    sun_distance=np.mean(source.separation(SkyCoord(get_sun(time+delta_time).ra,get_sun(time+delta_time).dec)))
    date=ephem.Date(time.value)
    moon_phase=(date-ephem.previous_new_moon(date))/(ephem.next_new_moon(date)-ephem.previous_new_moon(date))
    
    return altaz, delta_time, frame_night, frame_sun_night, moon_distance, sun_distance, moon_phase
    
#plotting function based on the "visibility" function
def visibility_plot(ra, dec, observatories, time):
    adesso=time-Time(time.value[0:-9]+'00:00')
    adesso=(adesso.to(u.hour)).value
    time=Time(time.value[0:-9]+'00:00')
    hour_range=[0,24]
    altazs=[]
    delta_times=[]
    frame_night_alts=[]
    frame_sun_days = []
    moon_distances = []
    sun_distances = []
    moon_phases = []
    
    for item in observatories:
        altaz, delta_time, frame_night, frame_sun_night, moon_distance, sun_distance, moon_phase = visibility(ra, dec, item, time)
        altazs.append(altaz)
        delta_times.append(delta_time)
        frame_night_alts.append(frame_night.alt)
        frame_sun_days.append(frame_sun_night)
        moon_distances.append(moon_distance)
        sun_distances.append(sun_distance)
        moon_phases.append(moon_phase)
    
    fig, ax = plt.subplots(len(altazs))
    A_v=3.1*m.ebv(ra, dec)
    ax[0].set_title('RA: %.2f    DEC: %.2f     UT: %s \n MD = %i deg     MP = %.2f    SD = %i deg    $A_{v}$=%.2f' %(ra, dec, time.value[:10], moon_distances[0].value, moon_phases[0], sun_distances[0].value, A_v))
    plt.subplots_adjust(hspace=0.2)
    for i in range(0, len(altazs)):
        ax[i].set_ylim(0, 90)
        ax[i].plot(delta_times[i], frame_night_alts[i], color='g', label=observatories[i].acr)
        ax[i].fill_between(delta_times[i], 0, 90, where=frame_sun_days[i].alt.value >= 0, facecolor='black', interpolate=True)
        #ax[i].legend(loc='best')
        ax[i].set_ylabel('Altitude [deg]')
        ax[i].set_xlim(hour_range[0],hour_range[1])
        times=[time+hour for hour in range(hour_range[0], hour_range[1])*u.hour]
        #times=[Time(time.value[0:-9]+'00:00')+hour for hour in range(hour_range[0], hour_range[1])*u.hour]
        hours=[time.value[11:-10] for time in times]
        ax[i].set_xticks(range(hour_range[0], hour_range[1]))
        ax[i].set_xticklabels(hours)
        ax[i].axvline(adesso, color='red')
        ax[i].axhline(y=30., color='red')
        box = ax[i].get_position()
        ax[i].set_position([box.x0, box.y0, box.width * 0.95, box.height])
        ax[i].legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10.)
    plt.xlabel('time')
    
    return fig